# ruff: noqa: T203
import os
import sys
from pathlib import Path
from pprint import pprint
from typing import Optional

from loguru import logger


def show_handlers():
    """顯示目前的處理器。
    """

    current_handlers = logger._core.handlers.copy()  # type: ignore
    return current_handlers


def remove_stderr_handlers(id: Optional[int | str] = None, show_handlers: bool = False):
    """
    移除指定的處理器

    Args:
        id (Optional[Union[int, str]], optional):
            要移除的處理器 ID，可以是：
            - None: 顯示目前處理器，讓用戶手動選擇輸入
            - 單個整數: 直接移除該 ID 的處理器
            - 逗號分隔的字串: 移除多個處理器，如 "1,2,3"
        show_handlers (bool, optional):
            是否在操作完成後顯示最新的處理器狀態。預設為 False。
    """

    current_handlers = logger._core.handlers.copy()  # type: ignore
    removed_count = 0

    if id is None:
        # 顯示當前處理器並讓用戶選擇
        pprint(current_handlers)

        user_input = input("請輸入要移除的處理器 ID (多個用逗號分隔，如 1,2,3): ").strip()

        if not user_input:
            logger.info("未輸入任何 ID，操作取消")
            return 0

        # 解析用戶輸入的 ID
        id_list = [int(x.strip()) for x in user_input.split(",") if x.strip()]

    elif isinstance(id, str):
        # 解析逗號分隔的字串
        id_list = [int(x.strip()) for x in id.split(",") if x.strip()]

    else:
        # 單個 ID
        id_list = [id]

    # 移除指定的處理器
    for handler_id in id_list:
        if handler_id in current_handlers:
            logger.remove(handler_id)
            removed_count += 1
            logger.info(f"已移除處理器 ID: {handler_id}")
        else:
            logger.info(f"處理器 ID {handler_id} 不存在")

    logger.info(f'總共移除了 {removed_count} 個處理器')

    # 如果需要顯示最新狀態
    if show_handlers:
        latest_handlers = logger._core.handlers.copy()  # type: ignore
        pprint(latest_handlers)


def start_log(level: str = "DEBUG", return_handlers: bool = False) -> Optional[tuple[int, int]]:
    """新增一個輸出處理器

    Args:
        level (str, optional): 設定處理器的日誌等級，預設為 "DEBUG"
        format (str, optional): 設定日誌輸出的格式，預設為 "{time} {level} {message}"
        show_handlers (bool, optional):
            是否在操作完成後顯示最新的處理器狀態。預設為 False。

    Returns:
        int: 新增的處理器 ID
    """
    logger.remove()  # 移除所有現有處理器

    MAIN_PATH = os.getenv('MAIN_PATH')
    if not MAIN_PATH:
        raise OSError("環境變數 'MAIN_PATH' 未設定")

    file_handler_id = logger.add(
        Path(MAIN_PATH) / 'data' / 'log' / 'output.log',
        format="{time} {level} {message}",
        level=level,
        rotation="1 week",
    )

    stderr_handler_id = logger.add(
        sys.stderr,
        level=level,
    )

    logger.info(f"開始用以下 ID 紀錄 {level} 層級以上訊息: {file_handler_id, stderr_handler_id}")

    if return_handlers:
        return file_handler_id, stderr_handler_id
