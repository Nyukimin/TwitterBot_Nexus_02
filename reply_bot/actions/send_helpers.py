import time
from selenium.webdriver.common.keys import Keys
import pyperclip


def send_clipboard_paste_then_ctrl_enter(driver, reply_input, text: str, paste_delay_seconds: float = 0.5) -> None:
    """
    返信入力欄に text を貼り付け、少し待ってから Ctrl+Enter で送信する。
    旧パイプラインで動作していた手順をそのまま関数化。
    """
    final_reply_text = (text or '').replace('<br>', '\n')
    pyperclip.copy(final_reply_text)
    reply_input.send_keys(Keys.CONTROL, 'v')
    time.sleep(paste_delay_seconds)
    reply_input.send_keys(Keys.CONTROL, Keys.ENTER)


def insert_text_robust(driver, reply_input, text: str, paste_delay_seconds: float = 0.2) -> bool:
    """
    できる限り確実に contentEditable な返信欄へ文字を入力する。
    手順:
      1) クリップボード貼り付け（Ctrl+V）
      2) 空のままなら JS の execCommand('insertText') / input イベントで挿入
      3) 非BMP絵文字が原因で失敗する場合に備え、ハートを BMP の '❤️' にフォールバック
    戻り値: 挿入に成功したら True、失敗なら False
    """
    try:
        final_reply_text = (text or '').replace('<br>', '\n')
        # 1) クリップボード貼り付け
        pyperclip.copy(final_reply_text)
        reply_input.send_keys(Keys.CONTROL, 'v')
        time.sleep(paste_delay_seconds)

        current = (reply_input.text or '').strip()
        if not current:
            try:
                current = (driver.execute_script('return (arguments[0].innerText || arguments[0].textContent || "").trim();', reply_input) or '').strip()
            except Exception:
                current = ''
        if current:
            return True

        # 2) JS で直接挿入（insertText → input イベント）
        js = r"""
        var el = arguments[0];
        var txt = arguments[1];
        try { el.focus(); } catch(e) {}
        var sel = window.getSelection();
        try { sel.removeAllRanges(); } catch(e) {}
        var range = document.createRange();
        try { range.selectNodeContents(el); range.collapse(false); sel.addRange(range); } catch(e) {}
        var ok = false;
        try { ok = document.execCommand('insertText', false, txt); } catch(e) { ok = false; }
        if (!ok) {
          try { el.dispatchEvent(new InputEvent('beforeinput', {inputType:'insertText', data:txt, bubbles:true})); } catch(e) {}
          try { el.textContent = (el.textContent || '') + txt; } catch(e) {}
          try { el.dispatchEvent(new InputEvent('input', {inputType:'insertText', data:txt, bubbles:true})); } catch(e) {}
        }
        return (el.innerText || el.textContent || '').trim();
        """
        inserted = (driver.execute_script(js, reply_input, final_reply_text) or '').strip()
        if inserted:
            return True

        # 3) 非BMP絵文字のフォールバック（🩷 → ❤️）
        fallback_text = final_reply_text.replace('🩷', '❤️')
        if fallback_text != final_reply_text:
            inserted2 = (driver.execute_script(js, reply_input, fallback_text) or '').strip()
            if inserted2:
                return True
        return False
    except Exception:
        return False