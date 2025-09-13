#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
reply_botモジュールのエントリーポイント

python -m reply_bot.login_assist で実行できるようにするための__main__.py
"""

import sys
import argparse

def main():
    """メインエントリーポイント"""
    # コマンドライン引数を解析
    # `python -m reply_bot.login_assist` と `python -m reply_bot login_assist` の両方をサポート
    if len(sys.argv) > 1:
        if sys.argv[1] == 'login_assist':
            # サブコマンド形式の場合
            from .login_assist import main as login_assist_main
            sys.argv = [sys.argv[0]] + sys.argv[2:]  # サブコマンドを削除
            login_assist_main()
        elif sys.argv[1] == 'check_login_status':
            # check_login_statusサブコマンド
            from .check_login_status import main as check_login_main
            sys.argv = [sys.argv[0]] + sys.argv[2:]  # サブコマンドを削除
            check_login_main()
        else:
            print(f"不明なコマンド: {sys.argv[1]}")
            print_help()
            sys.exit(1)
    elif '.' in sys.argv[0] and 'login_assist' in sys.argv[0]:
        # 直接モジュール指定形式の場合 (python -m reply_bot.login_assist)
        from .login_assist import main as login_assist_main
        login_assist_main()
    elif '.' in sys.argv[0] and 'multi_main' in sys.argv[0]:
        # 直接モジュール指定形式の場合 (python -m reply_bot.multi_main)
        from .multi_main import main as multi_main_main
        multi_main_main()
    elif '.' in sys.argv[0] and 'check_login_status' in sys.argv[0]:
        # 直接モジュール指定形式の場合 (python -m reply_bot.check_login_status)
        from .check_login_status import main as check_login_main
        check_login_main()
    else:
        # ヘルプを表示
        print_help()
        sys.exit(1)

def print_help():
    """ヘルプメッセージを表示"""
    print("使用方法:")
    print("  python -m reply_bot.login_assist --config CONFIG_FILE [--headless]")
    print("  python -m reply_bot login_assist --config CONFIG_FILE [--headless]")
    print("  python -m reply_bot.multi_main --config CONFIG_FILE [options]")
    print("  python -m reply_bot multi_main --config CONFIG_FILE [options]")
    print("  python -m reply_bot.check_login_status [--headless]")
    print("  python -m reply_bot check_login_status [--headless]")
    print("")
    print("利用可能なコマンド:")
    print("  login_assist       - Twitterログイン支援ツール（fixed_chrome使用）")
    print("  multi_main         - 多アカウント用オーケストレーター")
    print("  check_login_status - Twitterのログイン状態を確認します")
    print("")
    print("オプション:")
    print("  --headless - ブラウザをヘッドレスモード（非表示）で起動します")
    print("  --config   - アカウント設定ファイルのパス")

if __name__ == "__main__":
    main()