import numba as nb
import numpy as np
from numpy.typing import NDArray


@nb.njit()
def one_hot_encode_array(array: NDArray[np.int_]) -> NDArray[np.float64]:
    """將 numpy array 轉換成 one-hot encoding 的矩陣。

    Examples
    ---
    >>> one_hot_encode_array(np.array([1, 2, 3, 4, 5, 1, 2, 3, 4, 5]))
    array([
        [0, 1, 0, 0],
        [0, 0, 1, 0],
        [0, 0, 0, 1],
        [1, 0, 0, 0],
        [0, 1, 0, 0],
    ])
    """
    n_values = int(np.max(array) + 1)
    return np.eye(n_values)[array]


@nb.njit()
def one_hot_decode_array(array: NDArray[np.int_]) -> NDArray[np.int_]:
    """將 one-hot encoding 的矩陣轉換成原始的 array。

    Examples
    ---
    >>> one_hot_decode_array(np.array([
        [0, 1, 0, 0],
        [0, 0, 1, 0],
        [0, 0, 0, 1],
        [1, 0, 0, 0],
        [0, 1, 0, 0],
    ]))
    array([0, 2, 3, 0, 1])
    """
    return np.argmax(array, axis=1)


def normalize_array(array: NDArray[np.float64]) -> NDArray[np.float64]:
    """Normalize array to sum to 1."""
    total = array.sum()
    if total == 0:
        raise ValueError("Sum is zero")
    return array / total


def sum_col_array(array: NDArray[np.float64]) -> NDArray[np.float64]:
    """Sum over axis 0 (column-wise sum)."""
    return array.sum(axis=0)
