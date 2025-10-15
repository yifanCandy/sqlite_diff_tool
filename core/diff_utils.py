import pandas as pd

def diff_dataframe(df_left: pd.DataFrame, df_right: pd.DataFrame) -> pd.DataFrame:
    # 计算左减右
    combined = pd.concat([df_left, df_right, df_right]).drop_duplicates(keep=False)
    return combined
