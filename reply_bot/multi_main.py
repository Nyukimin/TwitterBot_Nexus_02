import argparse
import logging
import os
import time
from datetime import datetime
from typing import List, Dict, Any

import yaml
from selenium.common.exceptions import InvalidSessionIdException, WebDriverException

from . import config as cfg
from .utils import setup_driver, close_driver, force_restart_driver
from .csv_generator import main_process as csv_generator_main
from .reply_processor import main_process as reply_processor_main
from .post_reply import main_process as post_reply_main
from .actions.like import run as action_like
from .actions.comment import run as action_comment
from .actions.bookmark import run as action_bookmark
from .actions.retweet import run as action_retweet
from .db_stubs import has_action_log, record_action_log, count_actions_last_hours
from .operate_latest_tweet import get_top_tweet_ids_from_profile


def _human_view_handle_tweets(driver, view_handle: str, top_n: int, dwell_seconds: int) -> None:
    try:
        ids = get_top_tweet_ids_from_profile(driver, view_handle, top_n=max(1, int(top_n)))
    except Exception as e:
        logging.warning(f"[human-view] @{view_handle}: 取得失敗: {e}")
        return
    for idx, tid in enumerate(ids, start=1):
        url = f"https://x.com/any/status/{tid}"
        logging.info(f"[human-view] @{view_handle}: {idx}/{len(ids)} open {url} dwell={dwell_seconds}s")
        try:
            driver.get(url)
            from selenium.webdriver.support.ui import WebDriverWait as _W
            from selenium.webdriver.support import expected_conditions as _EC
            from selenium.webdriver.common.by import By as _By
            _W(driver, 20).until(_EC.presence_of_element_located((_By.CSS_SELECTOR, '[data-testid="tweetText"]')))
        except Exception:
            pass
        try:
            time.sleep(max(0, int(dwell_seconds)))
        except Exception:
            pass


def _run_human_like_on_start(driver, account_handle: str, policies: Dict[str, Any]) -> None:
    conf = (policies or {}).get('human_like_on_start', {}) or {}
    enabled = bool(conf.get('enabled', True))
    if not enabled:
        return
    sequence = conf.get('sequence') or [
        {'handle': 'Maya19960330', 'top_n': 10, 'dwell_seconds': 10},
        {'handle': 'ren_ai_coach', 'top_n': 10, 'dwell_seconds': 10},
        {'handle': '@self', 'top_n': 1, 'dwell_seconds': 10},
    ]
    logging.info(f"[human-start] enabled, steps={len(sequence)}")
    for step in sequence:
        try:
            h = str(step.get('handle', '')).strip()
            top_n = int(step.get('top_n', 1))
            dwell = int(step.get('dwell_seconds', 10))
            if h in ('@self', 'self'):
                target = account_handle
            else:
                target = h.lstrip('@')
            _human_view_handle_tweets(driver, target, top_n, dwell)
        except Exception as e:
            logging.warning(f"[human-start] step failed: {e}")


def _prefetch_view_collect_ids(driver, view_handle: str, top_n: int, dwell_seconds: int) -> List[str]:
    """per_target 事前閲覧: 先頭 top_n を開いて各 dwell 秒滞在し、対象 tweet_id を返す"""
    try:
        ids = get_top_tweet_ids_from_profile(driver, view_handle, top_n=max(1, int(top_n)))
    except Exception as e:
        logging.warning(f"[prefetch-view] @{view_handle}: 取得失敗: {e}")
        return []
    for idx, tid in enumerate(ids, start=1):
        url = f"https://x.com/any/status/{tid}"
        logging.info(f"[human-view] @{view_handle}: {idx}/{len(ids)} open {url} dwell={dwell_seconds}s")
        try:
            driver.get(url)
            from selenium.webdriver.support.ui import WebDriverWait as _W
            from selenium.webdriver.support import expected_conditions as _EC
            from selenium.webdriver.common.by import By as _By
            _W(driver, 20).until(_EC.presence_of_element_located((_By.CSS_SELECTOR, '[data-testid="tweetText"]')))
        except Exception:
            pass
        try:
            time.sleep(max(0, int(dwell_seconds)))
        except Exception:
            pass
    return ids


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


def _ensure_driver_alive(driver, *, headless: bool, profile_dir: str | None):
    """invalid session を事前検知し、必要に応じて自動再起動して返す。失敗時は None。"""
    try:
        # 軽いコマンドでセッション有効性を確認
        driver.execute_script("return 1")
        return driver
    except InvalidSessionIdException:
        logging.warning("WebDriver セッションが無効です。再起動します。")
    except WebDriverException as e:
        if 'invalid session id' in str(e).lower():
            logging.warning("WebDriver で invalid session id を検出。再起動します。")
        else:
            # その他の例外はそのまま伝播
            raise
    new_driver = force_restart_driver(headless=headless, profile_path=profile_dir)
    if not new_driver:
        logging.error("WebDriver の再起動に失敗しました。")
        return None
    return new_driver


def run_for_account(acct: Dict[str, Any], live_run: bool, hours: int | None, target_user: str | None = None) -> None:
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

        if getattr(cfg, 'DIRECT_ACTIONS_ONLY', False):
            # 直接アクションモード: accounts.yaml の設定に従い、対象ユーザーの最新ツイートへ実行
            from .operate_latest_tweet import get_latest_tweet_id_from_profile, get_top_tweet_ids_from_profile, _detect_existing_actions_via_ui, run_actions_on_tweet

            is_dry_run = not live_run
            features = acct.get('features', {}) or {}
            policies = acct.get('policies', {}) or {}
            rate_limits = acct.get('rate_limits', {}) or {}

            from selenium.webdriver.support.ui import WebDriverWait
            from selenium.webdriver.support import expected_conditions as EC
            from selenium.webdriver.common.by import By

            per_target = (policies or {}).get('per_target', {}) or {}
            # 起動時の人間らしさモード
            try:
                _run_human_like_on_start(driver, account_handle=handle, policies=policies)
            except Exception as _e:
                logging.warning(f"[human-start] 例外: {_e}")

            # 新設定: 先頭からの対象個数 / 対象ユーザー切替の間隔
            tweet_selection = (policies or {}).get('tweet_selection', {}) or {}
            top_n = int(tweet_selection.get('top_n', 1))
            switch_interval_sec = int((policies or {}).get('user_switch_interval_seconds', 0))
            # オプション: プロフィール読込の上限秒（上限超過や不備検知時のみ再起動）
            profile_load_timeout_sec = int((policies or {}).get('profile_load_timeout_seconds', 12))
            # --targetオプションが指定された場合、そのユーザーのみを処理対象とする
            if target_user:
                if target_user in per_target:
                    per_target = {target_user: per_target[target_user]}
                    logging.info(f"[{account_id}] --targetオプションにより {target_user} のみを処理対象とします")
                else:
                    logging.warning(f"[{account_id}] --targetで指定された {target_user} がper_targetに存在しません。処理をスキップします。")
                    return
            elif not per_target:
                logging.warning("per_target が空です。自分のプロフィールに対して実行します。")
                per_target = {handle: {'actions': [k for k, v in features.items() if v]}}

            # per_target の順に処理
            for target_handle, target_cfg in per_target.items():
                # セッションの事前ヘルスチェック（必要なら再起動）
                try:
                    checked = _ensure_driver_alive(driver, headless=headless, profile_dir=profile_dir)
                except Exception as _e:
                    logging.warning(f"@{target_handle}: ドライバーの健全性確認で例外: {_e}")
                    checked = None
                if not checked:
                    logging.error("WebDriver が利用不可のためスキップします。")
                    break
                driver = checked
                attempts = 0
                while attempts < 2:
                    try:
                        # アクション: accountのfeaturesとper_target側actionsの積集合
                        account_enabled = [k for k, v in features.items() if v]
                        target_actions = target_cfg.get('actions') if isinstance(target_cfg, dict) else None
                        if target_actions is None:
                            enabled_actions = account_enabled
                        else:
                            enabled_actions = [a for a in account_enabled if a in target_actions]
                        if not enabled_actions:
                            logging.info(f"@{target_handle}: 実行可能なアクションがありません（features / per_target.actions）")
                            break

                        # per_target 事前閲覧（閲覧のみ）
                        prefetch = (policies or {}).get('per_target_prefetch', {}) or {}
                        pre_ids: List[str] = []
                        if bool(prefetch.get('enabled', True)):
                            pre_top_n = int(prefetch.get('top_n', 5))
                            pre_dwell = int(prefetch.get('dwell_seconds', 5))
                            try:
                                logging.info(f"[prefetch-view] @{target_handle}: top_n={pre_top_n} dwell={pre_dwell}s")
                                pre_ids = _prefetch_view_collect_ids(driver, target_handle, pre_top_n, pre_dwell)
                            except Exception as _e:
                                logging.warning(f"[prefetch-view] 例外: {_e}")

                        # 先頭から top_n 件のツイートを対象（ピン留め/リポストは除外）
                        start_ts = time.time()
                        if top_n <= 1:
                            logging.info(f"@{target_handle}: 最新ツイートを取得します。")
                            tweet_ids = []
                            tid = get_latest_tweet_id_from_profile(driver, target_handle)
                            if tid:
                                tweet_ids = [tid]
                        else:
                            tweet_ids = get_top_tweet_ids_from_profile(driver, target_handle, top_n=top_n)
                        duration = time.time() - start_ts
                        # 読み込みが遅延（上限超過）または取得失敗時は一度だけブラウザ再起動して再試行
                        if (not tweet_ids) and duration >= profile_load_timeout_sec:
                            logging.warning(f"@{target_handle}: プロフィール読込が遅延({duration:.1f}s)のためブラウザ再起動→再試行します。")
                            # 既存ブラウザを先に閉じる
                            try:
                                driver.quit()
                            except Exception:
                                pass
                            new_driver = force_restart_driver(headless=headless, profile_path=profile_dir)
                            if not new_driver:
                                logging.error("WebDriverの再起動に失敗。スキップします。")
                                break
                            driver = new_driver
                            start_ts = time.time()
                            if top_n <= 1:
                                tid = get_latest_tweet_id_from_profile(driver, target_handle)
                                tweet_ids = [tid] if tid else []
                            else:
                                tweet_ids = get_top_tweet_ids_from_profile(driver, target_handle, top_n=top_n)

                        # 事前閲覧で収集したIDがあればそれら全てに対して actions を実行
                        if pre_ids:
                            for pre_tid in pre_ids:
                                tweet_url = f"https://x.com/any/status/{pre_tid}"
                                logging.info(f"@{target_handle}: ツイートに移動してUI状態検出: {tweet_url}")
                                driver.get(tweet_url)
                                WebDriverWait(driver, 30).until(
                                    EC.presence_of_element_located((By.CSS_SELECTOR, '[data-testid="tweetText"]'))
                                )
                                states = _detect_existing_actions_via_ui(driver)
                                logging.info(f"@{target_handle}: UI状態検出: {states}")
                                run_actions_on_tweet(
                                    driver=driver,
                                    account_id=account_id,
                                    target_handle=target_handle,
                                    tweet_id=pre_tid,
                                    actions=enabled_actions,
                                    policy=policies,
                                    rate_limits=rate_limits,
                                    live_run=live_run,
                                    existing_states=states,
                                )

                        if not tweet_ids and not pre_ids:
                            logging.warning(f"@{target_handle}: ツイートIDの取得に失敗しました。スキップします。")
                            break

                        for tweet_id in tweet_ids:
                            tweet_url = f"https://x.com/any/status/{tweet_id}"
                            logging.info(f"@{target_handle}: ツイートに移動してUI状態検出: {tweet_url}")
                            driver.get(tweet_url)
                            WebDriverWait(driver, 30).until(
                                EC.presence_of_element_located((By.CSS_SELECTOR, '[data-testid="tweetText"]'))
                            )
                            states = _detect_existing_actions_via_ui(driver)
                            logging.info(f"@{target_handle}: UI状態検出: {states}")

                            run_actions_on_tweet(
                                driver=driver,
                                account_id=account_id,
                                target_handle=target_handle,
                                tweet_id=tweet_id,
                                actions=enabled_actions,
                                policy=policies,
                                rate_limits=rate_limits,
                                live_run=live_run,
                                existing_states=states,
                            )

                        # ターゲット切替のインターバル（次のユーザーへ進む前に待機）
                        if switch_interval_sec > 0:
                            logging.info(f"@{target_handle}: 次ユーザーへ切替前に {switch_interval_sec}s 待機します。")
                            from time import sleep as _sleep
                            _sleep(switch_interval_sec)
                        break
                    except InvalidSessionIdException as e:
                        logging.warning(f"@{target_handle}: セッションが無効です。WebDriverを再起動して再試行します: {e}")
                        try:
                            driver.quit()
                        except Exception:
                            pass
                        new_driver = force_restart_driver(headless=headless, profile_path=profile_dir)
                        if not new_driver:
                            logging.error("WebDriverの再起動に失敗。スキップします。")
                            break
                        driver = new_driver
                        attempts += 1
                        continue
                    except WebDriverException as e:
                        if 'invalid session id' in str(e).lower():
                            logging.warning(f"@{target_handle}: invalid session id を検出。WebDriverを再起動して再試行します。")
                            try:
                                driver.quit()
                            except Exception:
                                pass
                            new_driver = force_restart_driver(headless=headless, profile_path=profile_dir)
                            if not new_driver:
                                logging.error("WebDriverの再起動に失敗。スキップします。")
                                break
                            driver = new_driver
                            attempts += 1
                            continue
                        logging.warning(f"@{target_handle}: 直接アクション処理でエラー: {e}")
                        break
                    except Exception as e:
                        logging.warning(f"@{target_handle}: 直接アクション処理でエラー: {e}")
                        break

            logging.info(f"=== アカウント '{account_id}' の直接アクション処理が完了しました ===")
        else:
            # 旧パイプライン
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            csv_path = os.path.join('output', f'extracted_tweets_{account_id}_{timestamp}.csv')

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

            logging.info("[解析] スレッド解析と返信生成を開始します。")
            processed_csv = reply_processor_main(driver, extracted_csv, account_config=account_config)
            if not processed_csv or not os.path.exists(processed_csv):
                logging.warning("解析フェーズで処理済みCSVの生成が確認できませんでした。投稿フェーズをスキップします。")
                return

            is_dry_run = not live_run
            features = acct.get('features', {}) or {}
            policies = acct.get('policies', {}) or {}
            rate_limits = acct.get('rate_limits', {}) or {}

            import pandas as _pd
            rows = _pd.read_csv(processed_csv).fillna('').to_dict(orient='records')

            if features.get('like', False):
                action_like(driver, rows, policies, rate_limits, account_id=account_id, dry_run=is_dry_run)
            if features.get('comment', False):
                # アカウント設定を渡す（comment_config等）
                action_comment(driver, rows, policies, rate_limits, account_id=account_id, dry_run=is_dry_run, account_config=account_config)
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
    parser.add_argument('--headless', action='store_true', help='強制ヘッドレスモード（accounts.yaml設定を上書き）')
    parser.add_argument('--no-headless', action='store_true', help='強制描画モード（accounts.yaml設定を上書き）')
    parser.add_argument('--target', type=str, help='対象ユーザーのhandle（@なし）を指定して、そのユーザーのみを処理対象とする')

    args = parser.parse_args()

    # --headlessと--no-headlessの同時指定チェック
    if args.headless and args.no_headless:
        raise ValueError("--headlessと--no-headlessは同時に指定できません")

    if args.concurrency and args.concurrency > 1:
        logging.warning("並列実行は未実装です。逐次実行にフォールバックします。")

    cfg_path = args.config
    if not os.path.exists(cfg_path):
        raise FileNotFoundError(f"アカウント設定ファイルが見つかりません: {cfg_path}")

    # DBは廃止。UI検出とログのみで運用します。

    cfg_data = load_accounts_config(cfg_path)
    targets = select_accounts(cfg_data, args.accounts)

    # ヘッドレス設定の上書き処理
    if args.headless:
        for acct in targets:
            if 'browser' not in acct:
                acct['browser'] = {}
            acct['browser']['headless'] = True
        logging.info("--headlessオプションにより、全アカウントでヘッドレスモードを強制有効化しました。")
    elif args.no_headless:
        for acct in targets:
            if 'browser' not in acct:
                acct['browser'] = {}
            acct['browser']['headless'] = False
        logging.info("--no-headlessオプションにより、全アカウントで描画モードを強制有効化しました。")

    for acct in targets:
        run_for_account(acct, live_run=args.live_run, hours=args.hours, target_user=args.target)


if __name__ == '__main__':
    # ルートのロギング初期化（既存のbasicConfigに依存するモジュールがあるため、最小限）
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    main()


