"""Chrome Automation Utils - Chrome自動化とプロファイル管理のための統合ユーティリティライブラリ"""

from .manager import ProfiledChromeManager
from .exceptions import ProfileNotFoundError, ProfileCreationError, ChromeLaunchError

__version__ = "1.0.0"
__all__ = ["ProfiledChromeManager", "ProfileNotFoundError", "ProfileCreationError", "ChromeLaunchError"]