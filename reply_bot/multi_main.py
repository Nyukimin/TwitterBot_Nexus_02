import argparse
import logging
import os
from datetime import datetime
from typing import List, Dict, Any

import yaml

from . import config as cfg
from .utils import setup_driver, close_driver
from .csv_generator import main_process as csv_generator_main
from .reply_processor import main_process as reply_processor_main
from .post_reply import main_process as post_reply_main
from .actions.like import run as action_like
from .actions.comment import run as action_comment
from .actions.bookmark import run as action_bookmark
from .actions.retweet import run as action_retweet
from .db import init_db


def _ensure_log_dir() -> None:
    os.makedirs('log', exist_ok=True)


class AccountPrefixFilter(logging.Filter):
    def __init__(self, prefix: str) -> None:
        super().__init__()
        self.prefix = prefix

    def filter(self, record: logging.LogRecord) -> bool:  # type: ignore[override]
        try:
            if not getattr(record, '_acct_prefixed', False):
                record.msg = f"{self.prefix} {record.msg}"
                record._acct_prefixed = True  # type: ignore[attr-defined]
        except Exception:
            pass
        return True


def load_accounts_config(path: str) -> Dict[str, Any]:
    with open(path, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f) or {}
    if 'accounts' not in data or not isinstance(data['accounts'], list):
        raise ValueError("accounts.yaml に 'accounts' 配列が定義されていません。")
    return data


def select_accounts(cfg_data: Dict[str, Any], selector: str) -> List[Dict[str, Any]]:
    accounts: List[Dict[str, Any]] = cfg_data['accounts']
    if selector.lower() == 'all':
        return accounts

    wanted = {s.strip().lower() for s in selector.split(',') if s.strip()}

    selected: List[Dict[str, Any]] = []
    for acct in accounts:
        acct_id = str(acct.get('id', '')).lower()
        handle = str(acct.get('handle', '')).lower()
        if acct_id in wanted or handle in wanted:
            selected.append(acct)

    if not selected:
        raise ValueError(f"指定されたアカウントが見つかりません: {selector}")

    return selected


def configure_logging_for_account(account_id: str, log_to_file: bool = True) -> AccountPrefixFilter:
    _ensure_log_dir()
    prefix_filter = AccountPrefixFilter(prefix=f"[{account_id}]")

    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)

    # 既存ハンドラにプレフィックス付与フィルタを追加
    for h in root_logger.handlers:
        h.addFilter(prefix_filter)

    # ファイル出力
    if log_to_file:
        ts = datetime.now().strftime('%Y%m%d_%H%M%S')
        fh = logging.FileHandler(os.path.join('log', f'{account_id}_{ts}.log'), encoding='utf-8')
        fh.setLevel(logging.INFO)
        # 既存のformatに合わせ、メッセージ冒頭に[acct]を注入する
        fh.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
        fh.addFilter(prefix_filter)
        root_logger.addHandler(fh)

    return prefix_filter


def remove_logging_filter(prefix_filter: AccountPrefixFilter) -> None:
    root_logger = logging.getLogger()
    for h in list(root_logger.handlers):
        try:
            h.removeFilter(prefix_filter)
        except Exception:
            pass


def run_for_account(acct: Dict[str, Any], live_run: bool, hours: int | None) -> None:
    account_id = str(acct.get('id', 'unknown'))
    handle = str(acct.get('handle', '')).strip()
    browser = acct.get('browser', {}) or {}
    profile_dir = browser.get('user_data_dir')
    headless = bool(browser.get('headless', False))

    # ログに [acct] 接頭辞を付与
    prefix_filter = configure_logging_for_account(account_id)

    # TARGET_USER をアカウントのハンドルに切替
    if handle:
        logging.info(f"TARGET_USER を切替: {cfg.TARGET_USER} -> {handle}")
        cfg.TARGET_USER = handle  # type: ignore[assignment]

    driver = None
    try:
        logging.info(f"=== アカウント '{account_id}' の処理を開始します (handle=@{handle}) ===")
        driver = setup_driver(headless=headless, profile_path=profile_dir)
        if not driver:
            logging.error("WebDriverの初期化に失敗しました。処理をスキップします。")
            return

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        csv_path = os.path.join('output', f'extracted_tweets_{account_id}_{timestamp}.csv')

        # ステップ1: 抽出
        hours_to_collect = hours if hours is not None else cfg.HOURS_TO_COLLECT
        logging.info(f"[抽出] 過去{hours_to_collect}時間を対象にCSV生成を開始: {csv_path}")
        extracted_csv = csv_generator_main(
            driver=driver,
            output_csv_path=csv_path,
            hours_to_collect=hours_to_collect,
        )
        if not extracted_csv or not os.path.exists(extracted_csv):
            logging.error("抽出フェーズでCSV生成に失敗しました。次のアカウントへ進みます。")
            return

        # ステップ2: 解析/返信生成
        logging.info("[解析] スレッド解析と返信生成を開始します。")
        processed_csv = reply_processor_main(driver, extracted_csv)
        if not processed_csv or not os.path.exists(processed_csv):
            logging.warning("解析フェーズで処理済みCSVの生成が確認できませんでした。投稿フェーズをスキップします。")
            return

        # ステップ3: 投稿/アクション実行（features と policies を反映）
        is_dry_run = not live_run
        features = acct.get('features', {}) or {}
        policies = acct.get('policies', {}) or {}
        rate_limits = acct.get('rate_limits', {}) or {}

        import pandas as _pd
        rows = _pd.read_csv(processed_csv).fillna('').to_dict(orient='records')

        if features.get('like', False):
            action_like(driver, rows, policies, rate_limits, account_id=account_id, dry_run=is_dry_run)
        if features.get('comment', False):
            action_comment(driver, rows, policies, rate_limits, account_id=account_id, dry_run=is_dry_run)
        if features.get('bookmark', False):
            action_bookmark(driver, rows, policies, rate_limits, account_id=account_id, dry_run=is_dry_run)
        if features.get('retweet', False):
            action_retweet(driver, rows, policies, rate_limits, account_id=account_id, dry_run=is_dry_run)
        logging.info(f"=== アカウント '{account_id}' の処理が完了しました ===")

    except Exception as e:
        logging.error(f"アカウント '{account_id}' の処理中に予期せぬエラー: {e}", exc_info=True)
    finally:
        try:
            remove_logging_filter(prefix_filter)
        except Exception:
            pass
        close_driver()


def main() -> None:
    parser = argparse.ArgumentParser(description='多アカウント用オーケストレーター')
    parser.add_argument('--accounts', type=str, default='all', help='実行対象アカウント（id or handle のカンマ区切り）/ all')
    parser.add_argument('--live-run', action='store_true', help='実際に投稿・いいねを行う（デフォルト: ドライラン）')
    parser.add_argument('--hours', type=int, default=None, help='収集対象の時間（未指定時は config.HOURS_TO_COLLECT）')
    parser.add_argument('--concurrency', type=int, default=1, help='並列実行数（ステップ1では逐次のみ対応）')
    parser.add_argument('--config', type=str, default=os.path.join('config', 'accounts.yaml'), help='アカウント設定YAMLのパス')

    args = parser.parse_args()

    if args.concurrency and args.concurrency > 1:
        logging.warning("並列実行は未実装です。逐次実行にフォールバックします。")

    cfg_path = args.config
    if not os.path.exists(cfg_path):
        raise FileNotFoundError(f"アカウント設定ファイルが見つかりません: {cfg_path}")

    # DB初期化（actions_log 等）
    init_db()

    cfg_data = load_accounts_config(cfg_path)
    targets = select_accounts(cfg_data, args.accounts)

    for acct in targets:
        run_for_account(acct, live_run=args.live_run, hours=args.hours)


if __name__ == '__main__':
    # ルートのロギング初期化（既存のbasicConfigに依存するモジュールがあるため、最小限）
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    main()


