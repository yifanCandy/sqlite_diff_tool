import tkinter as tk
from tkinterdnd2 import DND_FILES, TkinterDnD

class DragDropEntry(tk.Entry):
    def __init__(self, master, textvariable=None, **kwargs):
        super().__init__(master, textvariable=textvariable, **kwargs)
        self.drop_target_register(DND_FILES)
        self.dnd_bind('<<Drop>>', self._on_drop)

    def _on_drop(self, event):
        file_path = event.data.strip('{}')  # 去掉花括号
        self.delete(0, tk.END)
        self.insert(0, file_path)
