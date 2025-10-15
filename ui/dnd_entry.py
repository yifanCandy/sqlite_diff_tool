from PySide6.QtWidgets import QLineEdit
from PySide6.QtCore import Qt
import pathlib

class DragDropLineEdit(QLineEdit):
    """支持拖拽 SQLite 文件的 QLineEdit"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAcceptDrops(True)

    def dragEnterEvent(self, event):
        """拖拽进入"""
        if event.mimeData().hasUrls():
            urls = event.mimeData().urls()
            # 只接受 .db / .sqlite / .sqlite3 文件
            if any(url.toLocalFile().endswith(('.db', '.sqlite', '.sqlite3')) for url in urls):
                event.acceptProposedAction()
            else:
                event.ignore()
        else:
            event.ignore()

    def dropEvent(self, event):
        """拖拽释放"""
        urls = event.mimeData().urls()
        for url in urls:
            path = url.toLocalFile()
            if pathlib.Path(path).suffix in ['.db', '.sqlite', '.sqlite3']:
                self.setText(path)
                break
        event.acceptProposedAction()
