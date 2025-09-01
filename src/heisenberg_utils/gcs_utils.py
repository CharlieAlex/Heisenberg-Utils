import os
from datetime import timedelta

import requests
from dotenv import load_dotenv
from google.cloud import storage
from google.oauth2 import service_account
from loguru import logger

load_dotenv()
credentials_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
logger.debug(f"bigquery_utils.py 憑證路徑: {credentials_path}")
gcs_client = storage.Client(credentials=service_account.Credentials.from_service_account_file(credentials_path))


def upload_to_gcs(
    bucket_name: str,
    local_file_path: str,
    destination_blob_name: str,
    gcs_client: storage.Client=gcs_client,
) -> None:
    """
    將本地檔案上傳到 GCS Bucket（使用 service account）

    Args
    ---
    bucket_name (str): GCS 的 bucket 名稱
    local_file_path (str): 上傳到 GCS 的本地檔案路徑
    destination_blob_name (str): GCS 上的物件路徑（例如 models/model_v1.pkl）

    Example
    ---
    ```python
    from utils.gcs_utils import upload_to_gcs

    upload_to_gcs(
        bucket_name="person-carplusdata-weichun",
        local_file_path=MODELS_PATH / "shap_values" / "shap_values0110.pkl",
        destination_blob_name="shap_values/shap_values0110.pkl"
    )
    ```
    """
    try:
        bucket = gcs_client.bucket(bucket_name)
        blob = bucket.blob(destination_blob_name)
        blob.upload_from_filename(local_file_path)

        logger.success(f"✅ 檔案成功上傳：{local_file_path} → gs://{bucket_name}/{destination_blob_name}")

    except Exception as e:
        logger.error(f"❌ 上傳失敗：{e}")


def download_from_gcs(
    bucket_name: str,
    blob_name: str,
    local_file_path: str,
    gcs_client: storage.Client=gcs_client,
) -> None:
    """
    從 GCS bucket 下載檔案到本地

    Args
    ---
    bucket_name (str): GCS 的 bucket 名稱
    blob_name (str): GCS 上的物件路徑（例如 models/model_v1.pkl）
    local_file_path (str): 下載到本機的儲存路徑

    Example
    ---
    ```python
    from utils.gcs_utils import download_from_gcs

    download_from_gcs(
        bucket_name="person-carplusdata-weichun",
        blob_name="shap_values/shap_values0110.pkl",
        local_file_path=MODELS_PATH / "shap_values0110.pkl"
    )
    ```
    """
    try:
        bucket = gcs_client.bucket(bucket_name)
        blob = bucket.blob(blob_name)

        blob.download_to_filename(local_file_path)
        logger.success(f"✅ 已成功下載：gs://{bucket_name}/{blob_name} → {local_file_path}")

    except Exception as e:
        logger.error(f"❌ 下載失敗：{e}")


def generate_signed_url(
    bucket_name: str,
    blob_name: str,
    expiration_minutes: int = 15,
    gcs_client: storage.Client=gcs_client,
) -> str:
    """
    生成簽名 URL，讓人可以下載 GCS 上的檔案。

    Args
    ---
    bucket_name (str): GCS 的 bucket 名稱
    blob_name (str): GCS 上的物件路徑（例如 models/model_v1.pkl）
    expiration_minutes (int): 簽名 URL 的有效時間（分鐘）

    Example
    ---
    ```python
    from utils.gcs_utils import generate_signed_url

    url = generate_signed_url(
        bucket_name="person-carplusdata-weichun",
        blob_name="shap_values/shap_values0110.pkl",
        expiration_minutes=60
    )
    ```
    """
    bucket = gcs_client.bucket(bucket_name)
    blob = bucket.blob(blob_name)

    url = blob.generate_signed_url(
        version="v4",
        expiration=timedelta(minutes=expiration_minutes),
        method="GET",
    )

    return url


def download_from_signed_url(signed_url: str, save_path: str):
    """
    從簽名 URL 下載檔案到本地

    Args
    ---
    signed_url (str): 簽名 URL
    save_path (str): 下載到本地的儲存路徑

    Example
    ---
    ```python
    from utils.gcs_utils import download_from_signed_url

    download_from_signed_url(
        signed_url=url,
        save_path=MODELS_PATH / "model_v1.pkl"
    )
    ```
    """
    response = requests.get(signed_url)

    if response.status_code == 200:
        with open(save_path, 'wb') as f:
            f.write(response.content)
        logger.info(f"✅ 檔案已儲存至 {save_path}")
    else:
        logger.error(f"❌ 無法下載：{response.status_code} - {response.text}")
