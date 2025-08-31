from collections.abc import Sequence
from itertools import product
from typing import TypeVar

T = TypeVar("T")


def seq_intersect(a: Sequence[T], b: Sequence[T]) -> list[T]:
    """回傳兩個序列的交集（無順序）。

    原函數名為 col_intersect。

    Examples
    ---
    >>> seq_intersect(['a', 'b', 'c'], ['b', 'c', 'd'])
    ['b', 'c']
    """
    return list(set(a) & set(b))


def seq_difference(a: Sequence[T], b: Sequence[T]) -> list[T]:
    """回傳在 a 中但不在 b 中的元素（無順序）。

    原函數名為 col_remove。

    Examples
    ---
    >>> seq_difference(['a', 'b', 'c'], ['b', 'c', 'd'])
    ['a']
    """
    return list(set(a) - set(b))


def seq_union(a: Sequence[T], b: Sequence[T]) -> list[T]:
    """回傳 a 與 b 的聯集（不重複，順序保留）。

    原函數名為 col_non_duplicate。

    Examples
    ---
    >>> seq_union(['a', 'b', 'a', 'c', 'b'], ['a', 'b', 'd', 'e', 'f'])
    ['a', 'b', 'c', 'd', 'e', 'f']
    """
    return list(dict.fromkeys(list(a) + list(b)))


def seq_add_suffix(
    base: Sequence[str], suffixes: Sequence[str], include_base: bool = True
) -> list[str]:
    """
    對每個 base 元素加上每個 suffix 組合，並可選擇是否包含原始 base 元素。

    原函數名為 col_add_suffix。

    Args
    ---
    base: 底層元素（如欄位名稱）
    suffixes: 後綴列表
    include_base: 是否保留原始元素

    Returns
    ---
    list[str]: 所有組合（順序保留、不重複）

    Examples
    ---
    >>> generate_suffix_combinations(['a', 'b'], ['_l4w', '_l2w'])
    ['a_l4w', 'a_l2w', 'b_l4w', 'b_l2w']
    """
    result = [f"{b}{suf}" for b, suf in product(base, suffixes)]
    if include_base:
        result += base
    return list(dict.fromkeys(result))


def wrap_to_list(
    items: T | list[T] | None
) -> list[T]:
    """將單個項目或序列包裝成列表。

    原函數名為 wrap_to_list。

    Args
    ---
    items: 單個項目或序列

    Returns
    ---
    list[T]: 包裝後的列表

    Examples
    ---
    >>> wrap_to_list('a')
    ['a']
    >>> wrap_to_list(['a', 'b'])
    ['a', 'b']
    """
    if items is None:
        return []
    if isinstance(items, list):
        return items
    return [items]
