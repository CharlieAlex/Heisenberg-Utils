import os
from pathlib import Path

from loguru import logger

credentials_path = Path(os.getenv("GOOGLE_APPLICATION_CREDENTIALS", ""))
if credentials_path.is_file() is False:
    logger.error(f"Google application credentials file not found: {credentials_path}")
    raise FileNotFoundError("Please add GOOGLE_APPLICATION_CREDENTIALS to your environment variables.")
