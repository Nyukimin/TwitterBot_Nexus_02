"""Chrome Automation Utils - Chrome自動化とプロファイル管理のための統合ユーティリティライブラリ"""

from .chrome_automation_utils.manager import ProfiledChromeManager
from .chrome_automation_utils.exceptions import ProfileNotFoundError, ProfileCreationError, ChromeLaunchError

__version__ = "1.0.0"
__all__ = ["ProfiledChromeManager", "ProfileNotFoundError", "ProfileCreationError", "ChromeLaunchError"]