import os
import time
from pathlib import Path
from typing import Optional

import pandas as pd
import pygsheets
from dotenv import load_dotenv
from loguru import logger

from .config_utils import set_all_path
from .decorators import safe_execution

load_dotenv()
set_all_path()

DATA_PATH = Path(os.environ["DATA_PATH"])
SA_PATH = Path(os.environ["SA_PATH"])
GOOGLE_APPLICATION_CREDENTIALS = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')


@safe_execution()
def download_gsheet(
    url: str,
    sheet_name: str,
    save_path: Optional[str | Path]=None,
    service_file=GOOGLE_APPLICATION_CREDENTIALS
) -> pd.DataFrame:
    """將Google Sheet下載為DataFrame。"""

    def _remove_invisible_str(df: pd.DataFrame) -> pd.DataFrame:
        return (df
            .replace(r"[\s\u200B]+", " ", regex=True)
            .apply(lambda x: x.str.strip() if x.dtype == "object" else x)
            .copy()
        )

    gc = pygsheets.authorize(service_file=service_file)
    sht = gc.open_by_url(url)
    wk = sht.worksheet_by_title(sheet_name)
    df = wk.get_as_df()

    if save_path:
        save_path = DATA_PATH / save_path
        df.to_csv(save_path, index=False)
        logger.info(f'資料已成功下載至{save_path}')

        df = pd.read_csv(save_path)  # TODO: 不知為何讀完以後再刪除才不會出問題，找時間修正
        df = _remove_invisible_str(df)
        df.to_csv(save_path, index=False)

    return df


@safe_execution()
def upload_to_gsheet(
        url: str, sheet_name: str, local_path: Optional[str] = None,
        df: Optional[pd.DataFrame] = None, batch_size: int = 20_000,
        drop_unused_columns: bool = False
    ) -> bool:
    """將DataFrame分批上傳到指定的Google Sheet。

    Args:
        url: Google Sheet的URL
        sheet_name: 工作表名稱
        local_path: 本地CSV檔案路徑（相對於DATA_PATH）
        df: 要上傳的DataFrame（如果提供df，則忽略local_path）
        batch_size: 每批上傳的資料行數，預設20,000行
        drop_unused_columns: 是否刪除未使用的欄位，預設False

    Returns:
        bool: 上傳是否成功
    """
    # 準備要上傳的DataFrame
    if df is not None:
        upload_df = df.copy()
    elif local_path:
        full_path = DATA_PATH / local_path
        if not full_path.exists():
            logger.error(f'檔案不存在: {full_path}')
            return False
        upload_df = pd.read_csv(full_path)
    else:
        logger.error('必須提供 df 或 local_path 其中之一')
        return False

    # 連接到Google Sheets
    gc = pygsheets.authorize(service_file=GOOGLE_APPLICATION_CREDENTIALS)
    sht = gc.open_by_url(url)

    # 檢查工作表是否存在，不存在則新建
    worksheet_names = [ws.title for ws in sht.worksheets()]
    if sheet_name in worksheet_names:
        wk = sht.worksheet_by_title(sheet_name)
        logger.info(f'使用現有工作表: {sheet_name}')
    else:
        logger.info(f'工作表 "{sheet_name}" 不存在，正在新建...')
        wk = sht.add_worksheet(sheet_name)
        logger.info(f'已成功新建工作表: {sheet_name}')

    # 檢查資料大小與工作表限制
    total_rows = len(upload_df)
    data_rows = total_rows + 1  # +1 for header
    data_cols = len(upload_df.columns)
    sheet_rows = wk.rows
    sheet_cols = wk.cols

    # 如果資料超出工作表大小，需要擴展工作表
    if data_rows > sheet_rows or data_cols > sheet_cols:
        new_rows = max(data_rows, sheet_rows)
        new_cols = max(data_cols, sheet_cols)
        logger.info(f'擴展工作表大小至 {new_rows} 行 x {new_cols} 列')
        wk.resize(rows=new_rows, cols=new_cols)

    # 清空現有內容
    wk.clear()

    # 分批上傳
    if total_rows <= batch_size:
        # 資料量不大，直接上傳
        wk.set_dataframe(upload_df, start='A1', copy_index=False, copy_head=True)
        logger.info(f'資料已成功上傳至 Google Sheet: {sheet_name} ({total_rows} 行資料)')
    else:
        # 分批上傳
        num_batch = (total_rows + batch_size - 1) // batch_size
        logger.info(f'資料較大 ({total_rows} 行)，將分 {num_batch} 批上傳')

        # 先寫入標題行
        header_df = pd.DataFrame([upload_df.columns.tolist()], columns=upload_df.columns)
        wk.set_dataframe(header_df, start='A1', copy_index=False, copy_head=False)

        # 分批寫入資料
        for i in range(0, total_rows, batch_size):
            batch_df = upload_df.iloc[i:i+batch_size].copy()
            start_row = i + 2  # +2 because row 1 is header and rows are 1-indexed

            # 計算結束行號
            end_row = min(start_row + len(batch_df) - 1, data_rows)

            logger.info(f'上傳第 {i//batch_size + 1} 批資料 (行 {start_row} 到 {end_row})')

            # 將資料轉換為值列表
            values = batch_df.to_numpy().tolist()

            # 使用 update_values 方法批量寫入
            range_name = f'A{start_row}:{chr(65 + data_cols - 1)}{end_row}'
            wk.update_values(range_name, values)

            # 避免API限制，稍微暫停
            time.sleep(0.1)

        logger.info(f'資料已成功分批上傳至 Google Sheet: {sheet_name} ({total_rows} 行資料')

    # 刪除未使用的欄位
    if drop_unused_columns:
        logger.info('開始刪除未使用的欄位...')

        # 找出最後一個有資料的欄位
        last_used_col = data_cols
        current_sheet_cols = wk.cols

        # 如果工作表的欄位數大於實際使用的欄位數，則刪除多餘的欄位
        if current_sheet_cols > last_used_col:
            # 調整工作表大小，只保留有資料的欄位
            wk.resize(rows=wk.rows, cols=last_used_col)

            logger.info(f'已刪除個未使用的欄位，現在工作表有 {last_used_col} 欄')
        else:
            logger.info('沒有發現未使用的欄位需要刪除')

    logger.success(f'上傳GSheet已完成: {url}')

    return True
