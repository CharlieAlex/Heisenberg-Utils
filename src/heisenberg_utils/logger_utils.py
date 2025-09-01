# ruff: noqa: T203
import os
import sys
from pathlib import Path
from pprint import pprint
from typing import Any, Optional

from loguru import logger

DATA_PATH = Path(os.environ['MAIN_PATH']) / 'data'


def remove_stderr_handlers(
    logger_instance: Any = logger,
    id: Optional[int | str] = None,
    show_latest_handlers: bool = False
):
    """
    移除指定的處理器

    Args:
        logger_instance (Any, optional): 要操作的 logger 實例
        id (Optional[Union[int, str]], optional):
            要移除的處理器 ID，可以是：
            - None: 顯示目前處理器，讓用戶手動選擇輸入
            - 單個整數: 直接移除該 ID 的處理器
            - 逗號分隔的字串: 移除多個處理器，如 "1,2,3"
        show_latest_handlers (bool, optional):
            是否在操作完成後顯示最新的處理器狀態。預設為 False。
    """

    current_handlers = logger_instance._core.handlers.copy()  # type: ignore
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
            logger_instance.remove(handler_id)
            removed_count += 1
            logger.info(f"已移除處理器 ID: {handler_id}")
        else:
            logger.info(f"處理器 ID {handler_id} 不存在")

    logger_instance.info(f'總共移除了 {removed_count} 個處理器')

    # 如果需要顯示最新狀態
    if show_latest_handlers:
        latest_handlers = logger_instance._core.handlers.copy()  # type: ignore
        pprint(latest_handlers)


logger.remove()

file_handler_id = logger.add(
    DATA_PATH / 'log' / 'output.log',
    format="{time} {level} {message}",
    rotation="1 week",
    level="INFO",
)

stderr_handler_id = logger.add(sys.stderr, level="DEBUG")
