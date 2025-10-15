import sqlite3
import pandas as pd

def run_query(db_path, sql):
    conn = sqlite3.connect(db_path)
    df = pd.read_sql_query(sql, conn)
    conn.close()
    return df

def export_csv(df, filename):
    df.to_csv(filename, index=False, encoding="utf-8-sig")
