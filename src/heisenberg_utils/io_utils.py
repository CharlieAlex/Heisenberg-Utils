from typing import Any, Literal

import cloudpickle
import joblib
from loguru import logger

from .config_utils import set_models_path

MODELS_PATH = set_models_path()


def save_model(
    model: Any,
    path: str,
    name: str,
    dump_method: Literal['joblib', 'cloudpickle'] = 'joblib',
    ext: str = "pkl",
) -> None:
    """儲存模型到指定目錄與檔名。

    Args
    ---
    model: 要儲存的模型物件（通常為 sklearn 類別）
    path: 儲存的資料夾路徑
    name: 模型檔名（不含副檔名）
    ext: 檔案格式（預設為 "pkl")
    """
    full_path = MODELS_PATH / path
    full_path.mkdir(parents=True, exist_ok=True)
    file_path = full_path / f"{name}.{ext}"

    match dump_method:
        case 'joblib':
            joblib.dump(model, file_path)
        case 'cloudpickle':
            with open(file_path, "wb") as f:
                cloudpickle.dump(model, f)
    logger.info(f"模型儲存至:\n{file_path}")


def load_model(path: str, name: str, ext: str = "pkl") -> Any:
    """從指定目錄載入模型。

    Args
    ---
    path: 模型儲存目錄
    name: 模型檔名（不含副檔名）
    ext: 檔案格式（預設為 "pkl")

    Returns
    ---
    載入的模型物件
    """
    file_path = MODELS_PATH / path / f"{name}.{ext}"
    logger.info(f"Loading model from {file_path}")

    if not file_path.is_file():
        raise FileNotFoundError(f"Model file not found at {file_path}")

    return joblib.load(file_path)
