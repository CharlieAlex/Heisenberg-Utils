from collections.abc import Callable
from functools import wraps
from typing import Any

from loguru import logger


def safe_execution(enabled: bool = True):
    """ 裝飾器：可選擇是否捕捉函數執行中的例外，避免程式崩潰 """
    def decorator(func: Callable) -> Callable:
        if not enabled:
            return func  # 直接回傳原函數，不做 try-except

        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            try:
                return func(*args, **kwargs)
            except Exception as e:
                logger.warning(f"{func.__name__} 執行失敗，錯誤訊息: {e}")
                return None  # 可以根據需求選擇回傳值
        return wrapper

    return decorator
