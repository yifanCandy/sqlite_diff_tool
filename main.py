from ui.main_window import SQLiteCompareApp
from PySide6.QtWidgets import QApplication
import sys

if __name__ == "__main__":
    app = QApplication(sys.argv)         # 创建 QApplication
    window = SQLiteCompareApp()          # 创建主窗口
    window.show()                        # 显示窗口
    sys.exit(app.exec())                 # 启动 Qt 事件循环
