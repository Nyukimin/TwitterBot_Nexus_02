param(
  [switch]$ForceClean = $false,  # まずは誤爆防止のため既定は false。必要時に -ForceClean で上書き
  [string]$ProfilePath = "C:\GenerativeAI\Twitter_reply_02\profile\twitter_main",
  [switch]$UseEphemeralRunProfile = $false,  # true なら実行ごとに一時プロファイルを派生
  [string]$PythonExe = "C:\Users\nyuki\miniconda3\envs\TwitterReplyEnv\python.exe",
  [string]$BotName = "Maya19970330"    # 多重起動防止用 Mutex 名
)

# ===== 基本設定 =====
$ErrorActionPreference = 'Stop'
$Hours   = 24
$LiveRun = $true

# 作業ディレクトリ固定（タスクスケジューラ対策）
Set-Location "C:\GenerativeAI\Twitter_reply_02"

# Python の標準出力エンコードを UTF-8 に固定（ログ文字化け防止）
$env:PYTHONIOENCODING = 'utf-8'

# ===== ユーティリティ（プロファイル厳密判定）=====
function Get-ChromeProcsForProfile($prof) {
  $esc = [regex]::Escape($prof)
  Get-CimInstance Win32_Process |
    Where-Object {
      $_.Name -eq 'chrome.exe' -and
      $_.CommandLine -match "--user-data-dir=(""$esc""|$esc)(\s|$)"
    }
}

function Get-ChromeDriverForProfile($prof) {
  # chromedriver は user-data-dir を直接持たないことも多いので、ゆるめ一致
  $esc = [regex]::Escape($prof)
  Get-CimInstance Win32_Process |
    Where-Object { $_.Name -eq 'chromedriver.exe' -and $_.CommandLine -match $esc }
}

function Stop-ProcsUsingProfile($prof, $logFile) {
  $busyChrome = Get-ChromeProcsForProfile $prof
  $busyDriver = Get-ChromeDriverForProfile $prof

  if ($busyChrome -or $busyDriver) {
    if (-not $ForceClean) {
      $msg = "Profile in use. Use -ForceClean to terminate."
      Write-Host $msg
      Add-Content -LiteralPath $logFile -Value "[$(Get-Date -Format yyyyMMdd_HHmmss)] $msg" -Encoding utf8
      if ($busyChrome) { Add-Content -LiteralPath $logFile -Value ($busyChrome | Select ProcessId, Name, CommandLine | Format-List | Out-String) -Encoding utf8 }
      if ($busyDriver) { Add-Content -LiteralPath $logFile -Value ($busyDriver | Select ProcessId, Name, CommandLine | Format-List | Out-String) -Encoding utf8 }
      exit 1
    }

    Add-Content -LiteralPath $logFile -Value "[$(Get-Date -Format yyyyMMdd_HHmmss)] Killing EXACT user-data-dir=$prof" -Encoding utf8
    if ($busyChrome) { Add-Content -LiteralPath $logFile -Value ($busyChrome | Select ProcessId, Name, CommandLine | Format-List | Out-String) -Encoding utf8 }
    if ($busyDriver) { Add-Content -LiteralPath $logFile -Value ($busyDriver | Select ProcessId, Name, CommandLine | Format-List | Out-String) -Encoding utf8 }

    $busyChrome | ForEach-Object { Stop-Process -Id $_.ProcessId -Force }
    $busyDriver | ForEach-Object { Stop-Process -Id $_.ProcessId -Force }
  }
}

# ===== 準備 =====
$timestamp  = Get-Date -Format yyyyMMdd_HHmmss
$runProfile = if ($UseEphemeralRunProfile) { "$ProfilePath`_run_$timestamp" } else { $ProfilePath }

# ログ出力先（UTF-8）
$logDir = "C:\GenerativeAI\Twitter_reply_02\log"
if (-not (Test-Path $logDir)) { New-Item -ItemType Directory -Path $logDir | Out-Null }
$logFile = Join-Path $logDir "bot_$timestamp.log"
Add-Content -LiteralPath $logFile -Value "[$timestamp] RUN START" -Encoding utf8
Write-Host "[$timestamp] RUNNING reply_bot.main"

# ===== 多重起動防止（Mutex）=====
$mutexName  = "Global\$BotName"
$createdNew = $false
$mutex      = $null

try {
  $mutex = [System.Threading.Mutex]::new($true, $mutexName, [ref]$createdNew)
  if (-not $createdNew) {
    $msg = "Already running. BotName=$BotName"
    Write-Host $msg
    Add-Content -LiteralPath $logFile -Value "[$(Get-Date -Format yyyyMMdd_HHmmss)] $msg" -Encoding utf8
    exit 1
  }

  # プロファイル使用中のプロセスを必要に応じて停止（誤爆対策は関数内で実施）
  Stop-ProcsUsingProfile -prof $runProfile -logFile $logFile

  # Python 側へプロファイル情報を環境変数で受け渡し（reply_bot がこれを参照して --user-data-dir を付ける想定）
  $env:REPLYBOT_USER_DATA_DIR = $runProfile
  # 必要ならプロファイル名も：$env:REPLYBOT_PROFILE_DIR = "Default"

  # ===== Python 実行引数を確定 =====
  $pyArgs = @('-m','reply_bot.main','--timestamp',$timestamp,'--hours',$Hours)
  if ($LiveRun) { $pyArgs += '--live-run' }

  # ===== 実行：Start-Process で標準出力／標準エラーを確実に捕捉 =====
  $tmpDir    = Join-Path $env:TEMP "reply_bot_$timestamp"
  New-Item -ItemType Directory -Path $tmpDir | Out-Null
  $stdoutTmp = Join-Path $tmpDir "stdout.txt"
  $stderrTmp = Join-Path $tmpDir "stderr.txt"

  $proc = Start-Process -FilePath $PythonExe `
                        -ArgumentList $pyArgs `
                        -RedirectStandardOutput $stdoutTmp `
                        -RedirectStandardError  $stderrTmp `
                        -NoNewWindow -PassThru -Wait

  $exitCode = $proc.ExitCode

  # ===== ログへまとめて追記（UTF-8）=====
  if (Test-Path $stdoutTmp) {
    Add-Content -LiteralPath $logFile -Value "=== STDOUT ===" -Encoding utf8
    Add-Content -LiteralPath $logFile -Value (Get-Content -Path $stdoutTmp -Raw) -Encoding utf8
  }
  if (Test-Path $stderrTmp) {
    Add-Content -LiteralPath $logFile -Value "=== STDERR ===" -Encoding utf8
    Add-Content -LiteralPath $logFile -Value (Get-Content -Path $stderrTmp -Raw) -Encoding utf8
  }

  Add-Content -LiteralPath $logFile -Value "ExitCode=$exitCode" -Encoding utf8

} finally {
  if ($mutex) { $mutex.ReleaseMutex(); $mutex.Dispose() }
  # 一時ファイル削除（ログは残す）
  if ($tmpDir -and (Test-Path $tmpDir)) { Remove-Item -LiteralPath $tmpDir -Recurse -Force -ErrorAction SilentlyContinue }
}

# 終了タイムスタンプ
Add-Content -LiteralPath $logFile -Value "[${(Get-Date).ToString('yyyyMMdd_HHmmss')}]" -Encoding utf8
