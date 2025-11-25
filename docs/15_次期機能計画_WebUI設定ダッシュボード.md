# 次期機能計画: Web UI設定ダッシュボード

**作成日**: 2025-11-24  
**ステータス**: 計画中（未実装）  
**優先度**: 中  
**実装予定**: v3.0.0

---

## 📋 目次

1. [概要](#概要)
2. [背景・目的](#背景目的)
3. [技術アーキテクチャ](#技術アーキテクチャ)
4. [実装計画](#実装計画)
5. [機能仕様](#機能仕様)
6. [開発工数見積もり](#開発工数見積もり)
7. [技術選定](#技術選定)

---

## 🎯 概要

現在YAMLファイルで管理しているConfig設定を、Webブラウザ上で視覚的に編集・管理できるダッシュボードUIを実装します。

**主な機能:**
- ✅ 全24アカウントの一覧表示・管理
- ✅ ビジュアルなYAML設定エディタ
- ✅ アカウントON/OFF切替（ワンクリック）
- ✅ スケジュール設定（ドラッグ&ドロップ）
- ✅ 画像プレビュー（`config/{user}/images/`）
- ✅ リアルタイムログビューア
- ✅ ボット実行状態監視

---

## 🔍 背景・目的

### **現状の課題**

1. **YAMLファイル直接編集の煩雑性**
   - 24個のアカウントを手動で編集
   - YAML構文エラーのリスク
   - 設定の可視化が困難

2. **複数アカウント管理の効率性**
   - 各アカウントの有効/無効切替が面倒
   - スケジュール設定の全体把握が難しい
   - 設定変更後の即座の反映確認ができない

3. **非技術者の運用困難性**
   - YAMLファイル編集にはテキストエディタとYAML知識が必要
   - 設定ミスによるボット停止リスク

### **解決策**

Webベースの直感的UIを提供し、以下を実現：

- ✅ **視覚的な設定管理**: グラフィカルなインターフェースで設定を可視化
- ✅ **ワンクリック操作**: アカウントのON/OFF切替を簡単に
- ✅ **リアルタイム反映**: 設定変更を即座にYAMLファイルに保存
- ✅ **エラー防止**: フォームバリデーションで設定ミスを防止
- ✅ **運用効率化**: 複数アカウントの一括管理

---

## 🏗️ 技術アーキテクチャ

### **ディレクトリ構成**

```
TwitterBot_Nexus_02/
├── web_ui/                        # 新規Webインターフェース
│   ├── backend/                   # FastAPI バックエンド
│   │   ├── main.py               # FastAPIアプリケーション
│   │   ├── api/
│   │   │   ├── config.py         # Config CRUD API
│   │   │   ├── accounts.py       # アカウント管理API
│   │   │   ├── schedule.py       # スケジュール管理API
│   │   │   ├── images.py         # 画像管理API
│   │   │   └── status.py         # ボット状態監視API
│   │   ├── models/
│   │   │   ├── config_schema.py  # Pydantic設定スキーマ
│   │   │   └── account_schema.py # Pydanticアカウントスキーマ
│   │   ├── services/
│   │   │   ├── yaml_manager.py   # YAML読み書きサービス
│   │   │   └── bot_monitor.py    # ボット監視サービス
│   │   └── requirements.txt       # バックエンド依存パッケージ
│   │
│   └── frontend/                  # React フロントエンド
│       ├── src/
│       │   ├── components/
│       │   │   ├── Dashboard.jsx        # メインダッシュボード
│       │   │   ├── AccountManager.jsx   # アカウント管理
│       │   │   ├── ConfigEditor.jsx     # YAML編集UI
│       │   │   ├── ScheduleEditor.jsx   # スケジュール編集
│       │   │   ├── ImageGallery.jsx     # 画像プレビュー
│       │   │   └── LogViewer.jsx        # ログビューア
│       │   ├── pages/
│       │   │   ├── Home.jsx
│       │   │   ├── Accounts.jsx
│       │   │   └── Settings.jsx
│       │   ├── api/
│       │   │   └── client.js            # API通信クライアント
│       │   ├── App.jsx
│       │   └── index.js
│       ├── package.json
│       └── public/
│
├── reply_bot/                     # 既存ボット（変更なし）
├── config/                        # 既存設定（変更なし）
└── run_web_ui.bat                 # Web UI起動スクリプト（新規）
```

### **システム構成図**

```
┌─────────────────┐      HTTP API      ┌──────────────────┐
│                 │ ◄────────────────► │                  │
│  React Frontend │                    │  FastAPI Backend │
│  (localhost:3000)                    │  (localhost:8000)│
│                 │                    │                  │
└─────────────────┘                    └──────────────────┘
                                                │
                                                │ YAML読み書き
                                                ▼
                                       ┌──────────────────┐
                                       │                  │
                                       │  config/         │
                                       │  ├── user1/      │
                                       │  │   ├── accounts.yaml
                                       │  │   ├── profile/
                                       │  │   └── images/
                                       │  └── user2/...  │
                                       │                  │
                                       └──────────────────┘
```

---

## 📅 実装計画（3段階）

### **Phase 1: FastAPI バックエンド（3-5時間）**

#### **1.1 プロジェクトセットアップ**

```bash
mkdir -p web_ui/backend/api web_ui/backend/models web_ui/backend/services
cd web_ui/backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install fastapi uvicorn pydantic pyyaml python-dotenv
pip freeze > requirements.txt
```

#### **1.2 FastAPIアプリケーション実装**

**main.py:**
```python
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import yaml
from pathlib import Path
from typing import List, Dict, Optional

app = FastAPI(
    title="TwitterBot Config Manager API",
    description="YAML設定ファイルの可視化・編集API",
    version="1.0.0"
)

# CORS設定（Reactからのアクセス許可）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydanticモデル定義
class AccountConfig(BaseModel):
    username: str
    profile_name: str
    enabled: bool
    features: Dict
    policies: Dict
    rate_limits: Optional[Dict] = None

class ScheduleItem(BaseModel):
    time: str
    days: List[str]
    content: str
    enabled: bool

# APIエンドポイント実装
@app.get("/api/accounts")
async def list_accounts() -> List[Dict]:
    """全アカウント一覧取得"""
    config_dir = Path("../../config")
    accounts = []
    
    for user_dir in config_dir.glob("*/"):
        if user_dir.is_dir():
            yaml_path = user_dir / "accounts.yaml"
            if yaml_path.exists():
                with open(yaml_path, encoding='utf-8') as f:
                    data = yaml.safe_load(f)
                    accounts.append({
                        "username": user_dir.name,
                        "enabled": data.get("enabled", False),
                        "profile_name": data.get("profile_name", ""),
                        "features": data.get("features", {}),
                        "config_path": str(yaml_path)
                    })
    
    return accounts

@app.get("/api/accounts/{username}")
async def get_account(username: str) -> Dict:
    """特定アカウント設定取得"""
    yaml_path = Path(f"../../config/{username}/accounts.yaml")
    
    if not yaml_path.exists():
        raise HTTPException(status_code=404, detail=f"Account {username} not found")
    
    with open(yaml_path, encoding='utf-8') as f:
        config = yaml.safe_load(f)
    
    return {
        "username": username,
        "config": config
    }

@app.put("/api/accounts/{username}")
async def update_account(username: str, config: AccountConfig) -> Dict:
    """アカウント設定更新"""
    yaml_path = Path(f"../../config/{username}/accounts.yaml")
    
    if not yaml_path.exists():
        raise HTTPException(status_code=404, detail=f"Account {username} not found")
    
    # YAML保存
    with open(yaml_path, 'w', encoding='utf-8') as f:
        yaml.dump(config.dict(), f, allow_unicode=True, default_flow_style=False)
    
    return {"message": "Updated successfully", "username": username}

@app.get("/api/status")
async def bot_status() -> Dict:
    """ボット実行状態取得"""
    import psutil
    import os
    
    # プロセス検索（reply_bot実行中かチェック）
    running_processes = []
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            cmdline = proc.info['cmdline']
            if cmdline and 'reply_bot' in ' '.join(cmdline):
                running_processes.append({
                    'pid': proc.info['pid'],
                    'name': proc.info['name']
                })
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass
    
    return {
        "status": "running" if running_processes else "stopped",
        "processes": running_processes,
        "total_accounts": len(list(Path("../../config").glob("*/accounts.yaml")))
    }

@app.get("/api/images/{username}")
async def get_user_images(username: str) -> List[str]:
    """ユーザー画像一覧取得"""
    images_dir = Path(f"../../config/{username}/images")
    
    if not images_dir.exists():
        return []
    
    images = []
    for img_file in images_dir.glob("**/*.png"):
        images.append(str(img_file.relative_to(images_dir)))
    
    return images

# 起動コマンド（main関数）
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
```

#### **1.3 テスト実行**

```bash
# FastAPI起動
python main.py

# ブラウザで確認
# http://localhost:8000/docs （Swagger UI）
# http://localhost:8000/api/accounts （アカウント一覧）
```

---

### **Phase 2: React フロントエンド（5-8時間）**

#### **2.1 プロジェクトセットアップ**

```bash
cd web_ui
npx create-react-app frontend
cd frontend
npm install axios material-ui @mui/material @emotion/react @emotion/styled
npm install react-router-dom
```

#### **2.2 主要コンポーネント実装**

**AccountManager.jsx:**
```jsx
import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Card, CardContent, Typography, Switch, Grid } from '@mui/material';

function AccountManager() {
  const [accounts, setAccounts] = useState([]);
  const [loading, setLoading] = useState(true);
  
  useEffect(() => {
    fetchAccounts();
  }, []);
  
  const fetchAccounts = async () => {
    try {
      const response = await axios.get('http://localhost:8000/api/accounts');
      setAccounts(response.data);
      setLoading(false);
    } catch (error) {
      console.error('Failed to fetch accounts:', error);
      setLoading(false);
    }
  };
  
  const toggleAccount = async (username, currentStatus) => {
    try {
      const account = accounts.find(a => a.username === username);
      const updatedConfig = {
        ...account,
        enabled: !currentStatus
      };
      
      await axios.put(`http://localhost:8000/api/accounts/${username}`, updatedConfig);
      fetchAccounts(); // リロード
    } catch (error) {
      console.error('Failed to toggle account:', error);
    }
  };
  
  if (loading) return <div>Loading...</div>;
  
  return (
    <div style={{ padding: '20px' }}>
      <Typography variant="h4" gutterBottom>
        アカウント管理（全{accounts.length}件）
      </Typography>
      
      <Grid container spacing={3}>
        {accounts.map((account) => (
          <Grid item xs={12} sm={6} md={4} key={account.username}>
            <Card>
              <CardContent>
                <Typography variant="h6">{account.username}</Typography>
                <Typography color="textSecondary">
                  プロファイル: {account.profile_name}
                </Typography>
                
                <div style={{ marginTop: '10px' }}>
                  <Switch
                    checked={account.enabled}
                    onChange={() => toggleAccount(account.username, account.enabled)}
                    color="primary"
                  />
                  <span>{account.enabled ? '有効' : '無効'}</span>
                </div>
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>
    </div>
  );
}

export default AccountManager;
```

**ConfigEditor.jsx:**
```jsx
import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { TextField, Button, Box, Typography } from '@mui/material';

function ConfigEditor({ username }) {
  const [config, setConfig] = useState(null);
  const [loading, setLoading] = useState(true);
  
  useEffect(() => {
    if (username) {
      fetchConfig();
    }
  }, [username]);
  
  const fetchConfig = async () => {
    try {
      const response = await axios.get(`http://localhost:8000/api/accounts/${username}`);
      setConfig(response.data.config);
      setLoading(false);
    } catch (error) {
      console.error('Failed to fetch config:', error);
      setLoading(false);
    }
  };
  
  const handleSave = async () => {
    try {
      await axios.put(`http://localhost:8000/api/accounts/${username}`, config);
      alert('保存しました！');
    } catch (error) {
      console.error('Failed to save config:', error);
      alert('保存に失敗しました');
    }
  };
  
  if (loading || !config) return <div>Loading...</div>;
  
  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h5" gutterBottom>
        {username} - 設定編集
      </Typography>
      
      <TextField
        fullWidth
        label="プロファイル名"
        value={config.profile_name || ''}
        onChange={(e) => setConfig({ ...config, profile_name: e.target.value })}
        margin="normal"
      />
      
      <TextField
        fullWidth
        label="有効化"
        select
        value={config.enabled ? 'true' : 'false'}
        onChange={(e) => setConfig({ ...config, enabled: e.target.value === 'true' })}
        margin="normal"
      >
        <option value="true">有効</option>
        <option value="false">無効</option>
      </TextField>
      
      <Button 
        variant="contained" 
        color="primary" 
        onClick={handleSave}
        sx={{ mt: 2 }}
      >
        保存
      </Button>
    </Box>
  );
}

export default ConfigEditor;
```

---

### **Phase 3: 統合・デプロイ（2-3時間）**

#### **3.1 起動スクリプト作成**

**run_web_ui.bat:**
```batch
@echo off
echo ========================================
echo TwitterBot Web UI 起動中...
echo ========================================
echo.

echo [1/2] FastAPI Backend 起動...
start "FastAPI Backend" cmd /k "cd web_ui\backend && python main.py"
timeout /t 3

echo [2/2] React Frontend 起動...
start "React Frontend" cmd /k "cd web_ui\frontend && npm start"

echo.
echo ========================================
echo Web UI 起動完了！
echo ========================================
echo Backend API: http://localhost:8000
echo Frontend UI: http://localhost:3000
echo Swagger Docs: http://localhost:8000/docs
echo ========================================
pause
```

#### **3.2 動作確認**

```bash
# Web UI起動
run_web_ui.bat

# ブラウザで確認
# http://localhost:3000 - React UI
# http://localhost:8000/docs - API Docs
```

---

## 🎨 機能仕様

### **1. ダッシュボード画面**

- ✅ 全アカウント一覧表示（カード形式）
- ✅ 各アカウントのステータス（有効/無効）表示
- ✅ ボット実行状態表示（実行中/停止中）
- ✅ 最新ログ表示（最新10件）

### **2. アカウント管理画面**

- ✅ アカウント一覧表示
- ✅ ON/OFF切替（ワンクリック）
- ✅ 個別設定編集（ConfigEditorへ遷移）
- ✅ アカウント検索・フィルタリング

### **3. 設定編集画面**

- ✅ YAML設定のビジュアル編集
- ✅ フォームバリデーション
- ✅ リアルタイムプレビュー
- ✅ 保存時のバックアップ作成

### **4. スケジュール管理画面**

- ✅ スケジュール一覧表示
- ✅ ドラッグ&ドロップでスケジュール編集
- ✅ 時間指定（時:分）
- ✅ 曜日指定（複数選択可）

### **5. 画像管理画面**

- ✅ ユーザー別画像プレビュー
- ✅ 画像アップロード機能
- ✅ 画像削除機能
- ✅ ディレクトリ別表示（morning/lunch/evening）

### **6. ログビューア画面**

- ✅ リアルタイムログ表示
- ✅ ログレベルフィルタ（INFO/WARNING/ERROR）
- ✅ ログ検索機能
- ✅ ログダウンロード機能

---

## 📊 開発工数見積もり

| フェーズ | タスク | 作業時間 | 難易度 |
|---------|--------|---------|--------|
| **Phase 1** | FastAPI基本実装 | 3時間 | ⭐⭐ 低 |
| **Phase 1** | API エンドポイント実装 | 2時間 | ⭐⭐ 低 |
| **Phase 2** | React プロジェクトセットアップ | 1時間 | ⭐ 低 |
| **Phase 2** | AccountManager実装 | 2時間 | ⭐⭐ 低 |
| **Phase 2** | ConfigEditor実装 | 2時間 | ⭐⭐⭐ 中 |
| **Phase 2** | その他コンポーネント | 3時間 | ⭐⭐ 低 |
| **Phase 3** | 統合・デバッグ | 2時間 | ⭐⭐ 低 |
| **Phase 3** | ドキュメント作成 | 1時間 | ⭐ 低 |
| **合計** | - | **16時間** | **⭐⭐⭐** |

**実装期間:** 2-3日（1日5-8時間作業の場合）

---

## 🔧 技術選定

### **バックエンド: FastAPI（推奨）**

**選定理由:**
- ✅ Python製（既存プロジェクトと統合しやすい）
- ✅ 高速・軽量（Uvicorn ASGI）
- ✅ 自動API Docs生成（Swagger UI）
- ✅ Pydanticによる型安全性
- ✅ 非同期処理対応

**代替案:**
- Flask（シンプル・軽量）
- Django（フルスタック）

### **フロントエンド: React（推奨）**

**選定理由:**
- ✅ 最も人気のあるUIライブラリ
- ✅ 豊富なUIコンポーネント（Material-UI）
- ✅ 開発者コミュニティが大きい
- ✅ Reactの学習リソースが豊富

**代替案:**
- Vue.js（シンプル・学習コスト低）
- Streamlit（Pythonのみで実装可能・最も簡単）

### **より簡単な代替案: Streamlit**

**実装例:**
```python
import streamlit as st
import yaml
from pathlib import Path

st.set_page_config(page_title="TwitterBot Config Manager", layout="wide")

st.title("🤖 TwitterBot 設定管理")

# サイドバー: アカウント選択
config_dir = Path("config")
usernames = [d.name for d in config_dir.glob("*/") if d.is_dir()]
selected_user = st.sidebar.selectbox("アカウント選択", usernames)

# メイン画面: 設定編集
if selected_user:
    yaml_path = config_dir / selected_user / "accounts.yaml"
    
    with open(yaml_path, encoding='utf-8') as f:
        config = yaml.safe_load(f)
    
    st.header(f"{selected_user} - 設定")
    
    # フォーム
    with st.form("config_form"):
        enabled = st.checkbox("有効化", value=config.get("enabled", False))
        profile_name = st.text_input("プロファイル名", value=config.get("profile_name", ""))
        
        # 保存ボタン
        if st.form_submit_button("保存"):
            config["enabled"] = enabled
            config["profile_name"] = profile_name
            
            with open(yaml_path, 'w', encoding='utf-8') as f:
                yaml.dump(config, f, allow_unicode=True)
            
            st.success("✅ 保存しました！")
    
    # 現在の設定表示
    st.subheader("現在の設定（YAML）")
    st.code(yaml.dump(config, allow_unicode=True), language='yaml')
```

**実装時間: 2-4時間**

**起動方法:**
```bash
streamlit run web_ui/streamlit_app.py
```

---

## 📝 次のステップ

実装を希望される場合は、以下の順で進めます：

1. **技術選定の確認**: FastAPI+React または Streamlit
2. **Phase 1実装**: バックエンドAPI構築
3. **Phase 2実装**: フロントエンドUI構築
4. **Phase 3実装**: 統合・テスト・デプロイ

---

**最終更新**: 2025-11-24  
**ドキュメントバージョン**: 1.0.0