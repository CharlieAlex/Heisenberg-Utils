import os
import textwrap
from functools import partial
from pathlib import Path
from typing import Any

import numpy as np
import yaml
from loguru import logger
from matplotlib import rcParams


def filter_fields(source: dict, cls: type) -> dict:
    """
    過濾字典中的 key，僅保留在 Pydantic 模型中有定義的欄位。

    Args
    ---
    source (dict): 欲過濾的來源字典。
    cls (Type): Pydantic 模型類別，用來判斷哪些欄位需要保留。

    Returns
    ---
    dict: 僅包含 cls 中定義欄位的字典
    """
    model_field_keys = cls.model_fields.keys()
    return {k: v for k, v in source.items() if k in model_field_keys}


def build_from(config_obj: Any, cls: type) -> Any:
    """
    根據已有的 Pydantic 模型實例，建立另一個 Pydantic 模型的實例。
    此函數會自動處理欄位匹配，只傳遞目標模型所需的欄位。

    Args
    ---
    config_obj (Any): 來源 Pydantic 模型實例。
    cls (Type): 欲建立的目標 Pydantic 模型類別。

    Returns
    ---
    Any: 建立好的 Pydantic 模型實例
    """
    return cls.model_validate(config_obj.model_dump())


def merge_configs(base: dict, overrides: dict) -> dict:
    """
    合併兩組參數設定，`overrides` 的內容會覆蓋 `base` 中的對應項。

    Args
    ---
    base (dict): 預設的設定內容
    overrides (dict): 要覆蓋的設定內容

    Returns
    ---
    dict: 合併後的設定
    """
    return {**base, **overrides}


def remove_keys(d: dict, keys: list[str]) -> dict:
    """
    從字典中移除特定 key。

    Args
    ---
    d (dict): 原始字典
    keys (list[str]): 要刪除的 key 列表

    Returns
    ---
    dict: 移除 key 後的字典
    """
    return {k: v for k, v in d.items() if k not in keys}


def dict_diff_keys(d: dict, cls: type) -> list[str]:
    """
    比較字典與 Pydantic 模型的欄位，找出存在於字典但不存在於模型中的 key。

    Args
    ---
    d (dict): 要檢查的字典
    cls (Type): Pydantic 模型類別

    Returns
    ---
    list[str]: 多出來的 key
    """
    model_field_keys = cls.model_fields.keys()
    return [k for k in d if k not in model_field_keys]


def set_random_state(random_state: int=42) -> None:
    """設定環境變數 RANDOM_STATE。
    """
    os.environ['RANDOM_STATE'] = str(random_state)

    logger.debug(f'RANDOM_STATE 設定為: {random_state}')


def get_rng() -> np.random.Generator:
    """根據環境變數 RANDOM_STATE 取得 numpy 的隨機數生成器。

    Note
    ---
    如果環境變數 RANDOM_STATE 未設定，則預設為 42。
    """
    random_state = int(os.getenv('RANDOM_STATE', '42'))

    logger.debug(f'產生隨機數生成器，初始值為: {random_state}')

    return np.random.default_rng(random_state)


def load_yaml(path: str) -> dict:
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f)


def wrap_field(value, indent=24, width=120) -> str:
    """將長文本格式化為指定寬度的字符串，並在每行前添加縮進。

    Args
    ---
    value: 要格式化的值，可以是字符串或其他類型。
    indent: 每行前的縮進空格數。
    width: 每行的最大寬度。

    Returns
    ---
    str: 格式化後的字符串。
    """
    return textwrap.fill(str(value), width=width, subsequent_indent=' ' * indent)


def set_font(font_list: list[str]=['Arial Unicode MS', 'Noto Sans CJK TC', 'SimSong']) -> None:
    """設定字體。

    Args
    ---
    font_list: 字體名稱列表
    """
    rcParams['font.sans-serif'] = font_list
    rcParams['axes.unicode_minus'] = True
    logger.debug(f'字體設定順序為 {font_list}')


def set_path(target_path: str, target_name: str, suffix: str='') -> Path:
    """設定並取得PATH

    Args
    ---
    suffix: str
        PATH的後綴

    Returns
    ---
    path: str
        PATH

    NOTE
    ---
    必須有MAIN_PATH環境變量，才能使用此函數。
    """
    main_path = Path(os.environ["MAIN_PATH"])
    path = main_path / target_name / suffix
    os.environ[target_path] = str(path)
    logger.debug(f'{target_path} 設定為: {path}')
    return path


set_data_path = partial(set_path, target_path='DATA_PATH', target_name='data')
set_models_path = partial(set_path, target_path='MODELS_PATH', target_name='models')
set_dr_tester_path = partial(set_path, target_path='DR_TESTER_PATH', target_name='models', suffix='dr_tester')
set_mlruns_path = partial(set_path, target_path='MLRUNS_PATH', target_name='mlruns')
set_sa_path = partial(set_path, target_path='SA_PATH', target_name='sa')
set_queries_path = partial(set_path, target_path='QUERIES_PATH', target_name='src', suffix='queries')


def set_data_path_by_mode(mode: str) -> Path:
    """根據 mode 設定並且取得 data path。

    Args
    ---
    mode: str
        可接受的 mode 包含 local, gitlab, train, experiment, inference

    Returns
    ---
    path: str
        data path
    """
    match mode:
        case 'local':
            path = set_data_path(suffix='')
        case 'gitlab' | 'train' | 'experiment':
            path = set_data_path(suffix='train')
        case 'inference':
            path = set_data_path(suffix='inference')
        case _:
            raise ValueError(f"Invalid mode: {mode}")

    return path


def set_all_path() -> None:
    """設定所有常用路徑。
    """
    set_data_path()
    set_models_path()
    set_dr_tester_path()
    set_mlruns_path()
    set_sa_path()
    set_queries_path()
