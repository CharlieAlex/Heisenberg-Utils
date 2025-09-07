# pip3 install google-cloud-bigquery==3.29.0 google-cloud-bigquery-storage==2.28.0 db-dtypes==1.4.3 pyarrow==18.1.0
import os
from pathlib import Path
from typing import Optional

import pandas as pd
from google.cloud import bigquery
from google.oauth2 import service_account
from loguru import logger

credentials_path = Path(os.getenv("GOOGLE_APPLICATION_CREDENTIALS", ""))
BQ_CLIENT = bigquery.Client(credentials=service_account.Credentials.from_service_account_file(credentials_path))


def estimate_query_size(query_script: str, bq_client: bigquery.Client=BQ_CLIENT) -> Optional[float]:
    """
    估算查詢的處理量，並印出預估結果，回傳預估處理量(MB)。
    """
    job = bq_client.query(query_script, job_config=bigquery.QueryJobConfig(dry_run=True))
    estimated_bytes = job.total_bytes_processed

    if estimated_bytes is None:
        logger.warning("無法預估處理量!")
    elif estimated_bytes < 1024 ** 2:
        logger.info(f"預估處理量: {estimated_bytes:.0f} B")
    elif estimated_bytes < 1024 ** 3:
        logger.info(f"預估處理量: {estimated_bytes / (1024 ** 2):.2f} MB")
    else:
        logger.info(f"預估處理量: {estimated_bytes / (1024 ** 3):.2f} GB")

    return estimated_bytes


def script_to_df(
    query_script: str,
    job_config: Optional[bigquery.QueryJobConfig] = None,
    is_confirm: bool = True,
    save_path: Optional[str|Path] = None,
    bq_client: bigquery.Client = BQ_CLIENT,
) -> pd.DataFrame:
    """
    將 BigQuery 查詢結果轉換為 DataFrame。

    Args
    ---
    query_script: BigQuery 查詢腳本

    Example
    ---
    ```python
    tz = pytz.timezone("Asia/Taipei")
    target_start_date = datetime.now(tz).date()
    job_config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ScalarQueryParameter("target_start_date", "DATE", target_start_date),
            bigquery.ScalarQueryParameter("target_end_date", "DATE", "2025-03-16"),
        ]
    )
    script_path = QUERIES_PATH / 'test.sql'
    save_path = DATA_PATH / 'test.csv'
    df = path_to_df(
        script_path=script_path, job_config=job_config, is_print=False, is_confirm=True, save_path=save_path
    )
    ```
    """
    _ = estimate_query_size(query_script, bq_client)

    if is_confirm:
        confirm = input("確定要執行查詢嗎？(Y/N): ").strip().upper()
        if confirm != "Y":
            logger.info("取消查詢。")
            return pd.DataFrame()  # 回傳空 DataFrame

    try:
        job = bq_client.query(query_script, job_config=job_config)
        job.result()
        df = job.to_dataframe()
    except Exception as e:
        logger.error(f'執行查詢錯誤: {e}')
        logger.debug(f"bigquery_utils.py 憑證路徑: {credentials_path}")

    if save_path is not None:
        df.to_csv(save_path, index=False)
        logger.info(f"已成功儲存至:\n{save_path}")

    return df


def path_to_df(
    script_path: str|Path,
    job_config: Optional[bigquery.QueryJobConfig] = None,
    is_print: bool = False,
    is_confirm: bool = True,
    save_path: Optional[str|Path] = None,
    bq_client: bigquery.Client = BQ_CLIENT,
) -> pd.DataFrame:
    """
    讀取 SQL 腳本，並將查詢結果轉換為 DataFrame。

    Args:
    ---
    script_path: SQL 腳本路徑
    """
    with open(script_path, encoding="utf-8") as file:
        query_script = file.read()

    if is_print:
        logger.info(query_script)

    df = script_to_df(query_script, job_config, is_confirm, save_path, bq_client)

    return df
