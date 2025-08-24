import logging
import os
import time


try:
    import msvcrt  # Windows 専用ロック
    _IS_WINDOWS = os.name == 'nt'
except Exception:  # 安全側
    msvcrt = None
    _IS_WINDOWS = False

try:
    import fcntl  # POSIX ロック
except Exception:
    fcntl = None


class ProfileLock:
    """
    Chrome の user_data_dir（プロファイル）用の排他ロック。
    - 同一プロファイルを複数プロセスで同時使用して Chrome が拒否/ハングするのを防ぐ。
    - Windows: msvcrt.locking による 1 バイトロック（非ブロッキング + ポーリング）
    - POSIX: fcntl.flock による排他ロック（非ブロッキング + ポーリング）
    """

    def __init__(self, profile_dir: str, timeout_seconds: int = 120, poll_interval_seconds: float = 0.5) -> None:
        self.profile_dir = os.path.abspath(profile_dir)
        self.lock_file_path = os.path.join(self.profile_dir, ".profile.lock")
        self.timeout_seconds = timeout_seconds
        self.poll_interval_seconds = poll_interval_seconds
        self._fh = None
        self._locked = False

    def acquire(self) -> bool:
        os.makedirs(self.profile_dir, exist_ok=True)
        # 追記モードで開き、存在しない場合は作成
        self._fh = open(self.lock_file_path, "a+")
        start = time.time()

        while True:
            try:
                if _IS_WINDOWS and msvcrt is not None:
                    try:
                        # 1バイトの非ブロッキングロック
                        msvcrt.locking(self._fh.fileno(), msvcrt.LK_NBLCK, 1)
                    except OSError as e:
                        raise BlockingIOError from e
                elif fcntl is not None:
                    fcntl.flock(self._fh.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
                else:
                    # ロック非対応環境ではベストエフォート（常に獲得成功扱い）
                    pass

                # PID を記録
                try:
                    self._fh.seek(0)
                    self._fh.truncate()
                    self._fh.write(str(os.getpid()))
                    self._fh.flush()
                    try:
                        os.fsync(self._fh.fileno())
                    except Exception:
                        pass
                except Exception:
                    # 記録失敗は致命ではない
                    pass

                self._locked = True
                logging.info(f"[profile-lock] acquired: {self.lock_file_path}")
                return True

            except BlockingIOError:
                if (time.time() - start) >= self.timeout_seconds:
                    logging.warning(f"[profile-lock] timeout waiting: {self.lock_file_path}")
                    return False
                time.sleep(self.poll_interval_seconds)
            except Exception as e:
                # 予期せぬエラーでも一定時間はリトライ
                logging.warning(f"[profile-lock] error while acquiring {self.lock_file_path}: {e}")
                if (time.time() - start) >= self.timeout_seconds:
                    return False
                time.sleep(self.poll_interval_seconds)

    def release(self) -> None:
        if not self._fh:
            return
        try:
            if _IS_WINDOWS and msvcrt is not None:
                try:
                    msvcrt.locking(self._fh.fileno(), msvcrt.LK_UNLCK, 1)
                except Exception:
                    pass
            elif fcntl is not None:
                try:
                    fcntl.flock(self._fh.fileno(), fcntl.LOCK_UN)
                except Exception:
                    pass
        finally:
            try:
                self._fh.close()
            except Exception:
                pass
            self._fh = None
            if self._locked:
                logging.info(f"[profile-lock] released: {self.lock_file_path}")
            self._locked = False

    def __enter__(self):
        ok = self.acquire()
        if not ok:
            raise TimeoutError(f"Failed to acquire profile lock: {self.lock_file_path}")
        return self

    def __exit__(self, exc_type, exc, tb):
        self.release()


