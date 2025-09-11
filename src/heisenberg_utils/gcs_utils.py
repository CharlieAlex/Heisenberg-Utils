import os
from datetime import timedelta
from pathlib import Path

import requests
from dotenv import load_dotenv
from google.cloud import storage
from google.oauth2 import service_account
from loguru import logger

load_dotenv()
credentials_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
gcs_client = storage.Client(credentials=service_account.Credentials.from_service_account_file(credentials_path))


def upload_to_gcs(
    bucket_name: str,
    local_file_path: str | Path,
    destination_blob_name: str | Path,
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
        blob = bucket.blob(str(destination_blob_name))
        blob.upload_from_filename(local_file_path)

        logger.info(f"✅ 檔案成功上傳：{local_file_path} → gs://{bucket_name}/{destination_blob_name}")

    except Exception as e:
        logger.error(f"❌ 上傳失敗：{e}")


def download_from_gcs(
    bucket_name: str,
    blob_name: str | Path,
    local_file_path: str | Path,
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
        blob = bucket.blob(str(blob_name))

        blob.download_to_filename(local_file_path)
        logger.info(f"✅ 已成功下載：gs://{bucket_name}/{blob_name} → {local_file_path}")

    except Exception as e:
        logger.error(f"❌ 下載失敗：{e}")


def sync_gcs_file_to_local(
    bucket_name: str,
    gcs_blob_name: str | Path,
    local_file_path: str | Path,
    gcs_client: storage.Client = gcs_client,
) -> bool:
    """
    檢查 GCS 上的檔案是否存在，如果存在，則同步（下載）到本地。
    這滿足了您不使用 try-except 來判斷存在性的需求。

    Returns:
        bool: 如果檔案存在且成功下載，回傳 True；否則回傳 False。
    """
    try:
        bucket = gcs_client.bucket(bucket_name)
        blob = bucket.blob(str(gcs_blob_name))

        if blob.exists():
            logger.info(f"發現遠端檔案 gs://{bucket_name}/{gcs_blob_name}，正在同步至本地...")
            download_from_gcs(bucket_name, gcs_blob_name, local_file_path, gcs_client)   # type: ignore
            return True
        else:
            logger.info(f"遠端檔案 gs://{bucket_name}/{gcs_blob_name} 不存在，將在本地建立新檔案。")
            return False
    except Exception as e:
        logger.error(f"❌ 同步 GCS 檔案時發生錯誤：{e}")
        return False


def delete_from_gcs(
    bucket_name: str,
    blob_name: str | Path,
    gcs_client: storage.Client = gcs_client,
) -> None:
    """從 GCS Bucket 刪除一個物件。"""
    try:
        bucket = gcs_client.bucket(bucket_name)
        blob = bucket.blob(str(blob_name))

        if not blob.exists():
            logger.warning(f"⚠️ 嘗試刪除但檔案不存在：gs://{bucket_name}/{blob_name}")
            return

        blob.delete()
        logger.info(f"✅ 檔案成功刪除：gs://{bucket_name}/{blob_name}")

    except Exception as e:
        logger.error(f"❌ 刪除 GCS 檔案時發生錯誤：{e}")


def generate_signed_url(
    bucket_name: str,
    blob_name: str | Path,
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
    blob = bucket.blob(str(blob_name))

    url = blob.generate_signed_url(
        version="v4",
        expiration=timedelta(minutes=expiration_minutes),
        method="GET",
    )

    return url


def download_from_signed_url(signed_url: str, save_path: str | Path):
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
