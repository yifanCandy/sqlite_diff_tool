import tkinter as tk
from tkinter import filedialog, messagebox
import pandas as pd
from tkinterdnd2 import TkinterDnD
from ui.dnd_entry import DragDropEntry
from core.db_utils import run_query, export_csv
from core.diff_utils import diff_dataframe

class SQLiteCompareApp:
    def __init__(self):
        self.root = TkinterDnD.Tk()
        self.root.title("SQLite 差集比较工具")
        self.root.geometry("1200x700")
        self.left_df = None
        self.right_df = None
        self.create_ui()

    def create_ui(self):
        # 顶层框架：左右部分
        top_frame = tk.Frame(self.root)
        top_frame.pack(fill="both", expand=True, padx=10, pady=5)

        left_frame = tk.LabelFrame(top_frame, text="左侧数据库", padx=10, pady=10)
        left_frame.pack(side="left", fill="both", expand=True, padx=5)

        right_frame = tk.LabelFrame(top_frame, text="右侧数据库", padx=10, pady=10)
        right_frame.pack(side="right", fill="both", expand=True, padx=5)

        # 左侧内容
        tk.Label(left_frame, text="数据库文件（支持拖拽）").pack(anchor="w")
        self.left_db_path = tk.StringVar()
        DragDropEntry(left_frame, textvariable=self.left_db_path, width=50).pack(anchor="w")
        tk.Button(left_frame, text="选择文件", command=lambda: self.choose_file(self.left_db_path)).pack(anchor="w", pady=3)

        tk.Label(left_frame, text="SQL 查询:").pack(anchor="w", pady=(10, 0))
        self.left_sql = tk.Text(left_frame, height=5, width=60)
        self.left_sql.pack(fill="x")

        tk.Button(left_frame, text="执行查询", command=lambda: self.execute_query("left")).pack(pady=5)
        self.left_result = tk.Text(left_frame, height=15)
        self.left_result.pack(fill="both", expand=True)

        # 右侧内容
        tk.Label(right_frame, text="数据库文件（支持拖拽）").pack(anchor="w")
        self.right_db_path = tk.StringVar()
        DragDropEntry(right_frame, textvariable=self.right_db_path, width=50).pack(anchor="w")
        tk.Button(right_frame, text="选择文件", command=lambda: self.choose_file(self.right_db_path)).pack(anchor="w", pady=3)

        tk.Label(right_frame, text="SQL 查询:").pack(anchor="w", pady=(10, 0))
        self.right_sql = tk.Text(right_frame, height=5, width=60)
        self.right_sql.pack(fill="x")

        tk.Button(right_frame, text="执行查询", command=lambda: self.execute_query("right")).pack(pady=5)
        self.right_result = tk.Text(right_frame, height=15)
        self.right_result.pack(fill="both", expand=True)

        # 底部按钮与结果框
        bottom_frame = tk.Frame(self.root)
        bottom_frame.pack(fill="both", expand=True, padx=10, pady=10)

        tk.Button(bottom_frame, text="比较结果集（左 - 右）", command=self.compare_diff).pack(side="left", padx=10)
        tk.Button(bottom_frame, text="导出差集到 CSV",  command=self.export_diff_csv).pack(side="left", padx=10)

        self.diff_result = tk.Text(bottom_frame, height=10)
        self.diff_result.pack(fill="both", expand=True, pady=10)

    def choose_file(self, var):
        path = filedialog.askopenfilename(filetypes=[("SQLite 数据库", "*.db;*.sqlite;*.sqlite3")])
        if path:
            var.set(path)

    def execute_query(self, side):
        db_path = self.left_db_path.get() if side == "left" else self.right_db_path.get()
        sql = self.left_sql.get("1.0", "end").strip() if side == "left" else self.right_sql.get("1.0", "end").strip()

        if not db_path:
            messagebox.showwarning("提示", "请选择数据库文件")
            return
        if not sql:
            messagebox.showwarning("提示", "请输入 SQL 查询语句")
            return

        try:
            df = run_query(db_path, sql)
            text_widget = self.left_result if side == "left" else self.right_result
            text_widget.delete("1.0", "end")
            text_widget.insert("1.0", df.to_string(index=False))

            if side == "left":
                self.left_df = df
            else:
                self.right_df = df

        except Exception as e:
            messagebox.showerror("错误", str(e))

    def compare_diff(self):
        if self.left_df is None or self.right_df is None:
            messagebox.showwarning("提示", "请先执行两边查询")
            return

        diff_df = diff_dataframe(self.left_df, self.right_df)
        self.diff_result.delete("1.0", "end")
        if diff_df.empty:
            self.diff_result.insert("1.0", "✅ 两个结果完全一致")
        else:
            self.diff_result.insert("1.0", diff_df.to_string(index=False))
            self.last_diff_df = diff_df  # 保存差集结果

    def export_diff_csv(self):
        if not hasattr(self, "last_diff_df"):
            messagebox.showwarning("提示", "请先比较结果")
            return
        file = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV 文件", "*.csv")])
        if file:
            export_csv(self.last_diff_df, file)
            messagebox.showinfo("完成", f"差集已导出到：{file}")

    def run(self):
        self.root.mainloop()
