# ruff: noqa: T203
import logging
import os
import sys
from contextlib import contextmanager
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


def redirect_libraries_logging_to_loguru(log_level_map: dict[str, str]):
    """
    攔截並重定向指定函式庫的日誌訊息，統一由 Loguru 處理。

    Args:
        log_level_map (Dict[str, str], optional):
            一個字典，key 為函式庫的 logger 名稱 (e.g., "optuna", "mlflow"),
            value 為希望攔截的最低日誌級別 (e.g., "INFO")。
    """

    class InterceptHandler(logging.Handler):
        """
        一個將標準 logging 訊息重定向到 Loguru 的處理器。
        """
        def emit(self, record: logging.LogRecord) -> None:  # noqa: PLR6301
            try:
                level = logger.level(record.levelname).name
            except ValueError:
                level = record.levelno

            frame, depth = logging.currentframe(), 2
            while frame and frame.f_code.co_filename == logging.__file__:
                frame = frame.f_back
                depth += 1

            logger.opt(depth=depth, exception=record.exc_info).log(
                level,
                record.getMessage(),
            )

    LEVEL_MAPPING = {
        'NOTSET': logging.NOTSET,
        'DEBUG': logging.DEBUG,
        'INFO': logging.INFO,
        'WARNING': logging.WARNING,
        'ERROR': logging.ERROR,
        'CRITICAL': logging.CRITICAL
    }

    log_level_map_processed = {
        module: LEVEL_MAPPING[level.upper()]
        for module, level in log_level_map.items()
    }

    # 建立一個共用的攔截器實例
    handler = InterceptHandler()

    for lib_name, level in log_level_map_processed.items():
        # 取得目標函式庫的 logger
        lib_logger = logging.getLogger(lib_name)

        # 清除已存在的處理器，避免重複輸出
        lib_logger.handlers.clear()

        # 設定希望攔截的最低級別
        lib_logger.setLevel(level)

        # 加入我們自訂的攔截處理器
        lib_logger.addHandler(handler)

        logger.info(f"Redirected '{lib_name}' logging to Loguru at level {logging.getLevelName(level)}.")


@contextmanager
def suppress_stdout():
    """一個上下文管理器，可以暫時抑制(suppress)區塊內的標準輸出。
    """
    # 將當前的 stdout 保存起來
    original_stdout = sys.stdout
    # 在 try 區塊中，將 stdout 指向 os.devnull
    try:
        sys.stdout = open(os.devnull, 'w')  # noqa: PLW1514
        yield
    # 無論如何，在 finally 區塊中確保恢復原始的 stdout
    finally:
        sys.stdout.close()
        sys.stdout = original_stdout
