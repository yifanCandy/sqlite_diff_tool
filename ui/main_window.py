from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, QLabel,
    QLineEdit, QTextEdit, QPushButton, QFileDialog, QMessageBox
)
from PySide6.QtCore import Qt
from .dnd_entry import DragDropLineEdit
from core.db_utils import run_query, export_csv
from core.diff_utils import diff_dataframe
import sys
import pandas as pd

class SQLiteCompareApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("SQLite 差集比较工具")
        self.resize(1200, 700)

        self.left_df = None
        self.right_df = None
        self.last_diff_df = None

        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout(self)

        # =================== 上部左右布局 ===================
        top_layout = QHBoxLayout()

        # 左侧数据库组
        left_group = QGroupBox("左侧数据库")
        left_layout = QVBoxLayout()
        left_layout.addWidget(QLabel("数据库文件（支持拖拽）"))
        self.left_db_line = DragDropLineEdit()
        left_layout.addWidget(self.left_db_line)
        left_btn = QPushButton("选择文件")
        left_btn.clicked.connect(lambda: self.choose_file(self.left_db_line))
        left_layout.addWidget(left_btn)
        left_layout.addWidget(QLabel("SQL 查询:"))
        self.left_sql_text = QTextEdit()
        self.left_sql_text.setFixedHeight(80)
        left_layout.addWidget(self.left_sql_text)
        left_exec_btn = QPushButton("执行查询")
        left_exec_btn.clicked.connect(lambda: self.execute_query("left"))
        left_layout.addWidget(left_exec_btn)
        self.left_result_text = QTextEdit()
        self.left_result_text.setReadOnly(True)
        left_layout.addWidget(self.left_result_text)
        left_group.setLayout(left_layout)
        top_layout.addWidget(left_group, 1)

        # 右侧数据库组
        right_group = QGroupBox("右侧数据库")
        right_layout = QVBoxLayout()
        right_layout.addWidget(QLabel("数据库文件（支持拖拽）"))
        self.right_db_line = DragDropLineEdit()
        right_layout.addWidget(self.right_db_line)
        right_btn = QPushButton("选择文件")
        right_btn.clicked.connect(lambda: self.choose_file(self.right_db_line))
        right_layout.addWidget(right_btn)
        right_layout.addWidget(QLabel("SQL 查询:"))
        self.right_sql_text = QTextEdit()
        self.right_sql_text.setFixedHeight(80)
        right_layout.addWidget(self.right_sql_text)
        right_exec_btn = QPushButton("执行查询")
        right_exec_btn.clicked.connect(lambda: self.execute_query("right"))
        right_layout.addWidget(right_exec_btn)
        self.right_result_text = QTextEdit()
        self.right_result_text.setReadOnly(True)
        right_layout.addWidget(self.right_result_text)
        right_group.setLayout(right_layout)
        top_layout.addWidget(right_group, 1)

        main_layout.addLayout(top_layout)

        # =================== 底部布局：左侧按钮，右侧差集显示 ===================
        bottom_layout = QHBoxLayout()

        # 左侧按钮区域
        btn_layout_outer = QVBoxLayout()  # 外层垂直布局，用于上下居中

        # 添加上方伸缩，使按钮垂直居中
        btn_layout_outer.addStretch(1)

        # 创建按钮并垂直排列
        compare_btn = QPushButton("比较结果集（左 - 右）")
        export_btn = QPushButton("导出差集到 CSV")
        compare_btn.clicked.connect(self.compare_diff)
        export_btn.clicked.connect(self.export_diff_csv)

        btn_layout_outer.addWidget(compare_btn, alignment=Qt.AlignmentFlag.AlignHCenter)
        btn_layout_outer.addWidget(export_btn, alignment=Qt.AlignmentFlag.AlignHCenter)

        # 下方伸缩，使按钮垂直居中
        btn_layout_outer.addStretch(1)

        # 左侧按钮区域占0权重
        bottom_layout.addLayout(btn_layout_outer, 0)

        # 右侧差集显示区域保持不变
        self.diff_result_text = QTextEdit()
        self.diff_result_text.setReadOnly(True)
        bottom_layout.addWidget(self.diff_result_text, 1)

        main_layout.addLayout(bottom_layout)

    # =================== 文件选择 ===================
    def choose_file(self, line_edit: QLineEdit):
        path, _ = QFileDialog.getOpenFileName(
            self, "选择 SQLite 数据库文件", "", "SQLite 文件 (*.db *.sqlite *.sqlite3)"
        )
        if path:
            line_edit.setText(path)

    # =================== 执行 SQL 查询 ===================
    def execute_query(self, side: str):
        db_path = self.left_db_line.text() if side == "left" else self.right_db_line.text()
        sql = self.left_sql_text.toPlainText().strip() if side == "left" else self.right_sql_text.toPlainText().strip()

        if not db_path:
            QMessageBox.warning(self, "提示", "请选择数据库文件")
            return
        if not sql:
            QMessageBox.warning(self, "提示", "请输入 SQL 查询语句")
            return

        try:
            df = run_query(db_path, sql)
            if side == "left":
                self.left_df = df
                self.left_result_text.setText(df.to_string(index=False))
            else:
                self.right_df = df
                self.right_result_text.setText(df.to_string(index=False))
        except Exception as e:
            QMessageBox.critical(self, "错误", str(e))

    # =================== 比较差集 ===================
    def compare_diff(self):
        if self.left_df is None or self.right_df is None:
            QMessageBox.warning(self, "提示", "请先执行两边查询")
            return

        diff_df = diff_dataframe(self.left_df, self.right_df)
        self.diff_result_text.clear()
        if diff_df.empty:
            self.diff_result_text.setText("✅ 两个结果完全一致")
            self.last_diff_df = None
        else:
            self.diff_result_text.setText(diff_df.to_string(index=False))
            self.last_diff_df = diff_df

    # =================== 导出差集 CSV ===================
    def export_diff_csv(self):
        if self.last_diff_df is None:
            QMessageBox.warning(self, "提示", "请先比较结果")
            return

        file, _ = QFileDialog.getSaveFileName(self, "导出差集 CSV", "", "CSV 文件 (*.csv)")
        if file:
            export_csv(self.last_diff_df, file)
            QMessageBox.information(self, "完成", f"差集已导出到：{file}")
