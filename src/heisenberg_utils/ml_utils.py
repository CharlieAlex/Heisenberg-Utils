from typing import Optional

import numpy as np
import pandas as pd
from numpy.typing import NDArray


def generate_bootstrap_indices(
    data_idx: Optional[NDArray] = None,
    n_size: int = 10000,
    replications: int = 10,
    test_ratio: float = 0.1,
    rng: np.random.Generator = np.random.default_rng(),
) -> list[tuple[pd.Index, pd.Index]]:
    """產生多個訓練集和測試集 index。

    Args
    ---
    data_idx: 資料的 index。
    n_size: 資料的數量，如果沒給 data_idx 時才會使用。
    replications: 重複的次數。
    test_ratio: 測試集的比例。

    Returns
    ---
    train_idx_list: 訓練集 index 列表。
    test_idx_list: 測試集 index 列表。
    """
    if data_idx is None:
        data_idx = np.arange(0, n_size)
    else:
        n_size = len(data_idx)

    train_idx_list = [
        pd.Index(rng.choice(data_idx, int(n_size*(1-test_ratio)), replace=False))
        for _ in range(replications)
    ]

    test_idx_list = [
        pd.Index(data_idx).difference(train_idx)
        for train_idx in train_idx_list
    ]

    return list(zip(train_idx_list, test_idx_list))
