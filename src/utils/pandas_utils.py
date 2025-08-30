import pandas as pd

from .sequence_utils import seq_intersect


def format_number(df: pd.DataFrame, num_digits: int = 2) -> pd.DataFrame:
    """將 DataFrame 中的數字格式化為字串，保留小數點後 num_digits 位。
    支援普通欄位與 MultiIndex 欄位。

    Args:
        df (pd.DataFrame): 欲格式化的資料
        num_digits (int): 小數點後位數

    Returns:
        pd.DataFrame: 字串格式化後的資料
    """
    df_formatted = df.copy()
    numeric_cols = df.select_dtypes(include="number").columns

    for col in numeric_cols:
        df_formatted[col] = df[col].map(lambda x: f"{x:,.{num_digits}f}" if pd.notna(x) else "")

    return df_formatted


def drop_multicol(df: pd.DataFrame, cols: list[str]) -> pd.DataFrame:
    """
    從 MultiIndex 欄位中，根據第一層或第二層欄位名稱，刪除符合的欄位。

    Args
    ---
    df (pd.DataFrame): 含多層欄位的 DataFrame
    cols (list[str]): 欲刪除的欄位名（第一層或第二層）

    Returns
    ---
    pd.DataFrame: 刪除後的 DataFrame

    Example
    ---
    >>> mulit_col_df.columns
    MultiIndex([('registered_days', 'mean'),
                ('registered_days', 'sum'),
                ('registered_days', 'std')],
               )
    >>> drop_multicol(mulit_col_df, ['mean'])
    MultiIndex([('registered_days', 'sum'),
                ('registered_days', 'std')],
               )
    """
    if not isinstance(df.columns, pd.MultiIndex):
        raise ValueError("DataFrame 欄位必須為 MultiIndex。")

    to_drop = [col for col in df.columns if col[0] in cols or col[1] in cols]
    return df.drop(columns=to_drop)


def col_check_exist(col_list: list[str], df: pd.DataFrame) -> list[str]:
    """給定一個欄位名稱列表，回傳在 dataframe 中存在的欄位名稱列表。

    Examples
    ---
    >>> col_check_exist(['a', 'b', 'f'], ['a', 'b', 'c', 'd'])
    ['a', 'b']
    """
    df_cols = df.columns.tolist()
    return seq_intersect(col_list, df_cols)
