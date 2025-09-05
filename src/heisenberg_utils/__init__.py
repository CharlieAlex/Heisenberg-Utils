import os
from pathlib import Path

from loguru import logger

MAIN_PATH = Path(os.getenv("MAIN_PATH", ""))
if not os.getenv("MAIN_PATH"):
    logger.warning("No MAIN_PATH found, please add MAIN_PATH to your environment variables")

credentials_path = MAIN_PATH / Path(os.getenv("GOOGLE_APPLICATION_CREDENTIALS", "sa/sa.json"))
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = str(credentials_path)
if credentials_path.is_file() is False:
    logger.error(f"Google application credentials file not found: {credentials_path}")
    raise FileNotFoundError("Please add GOOGLE_APPLICATION_CREDENTIALS to your environment variables.")
