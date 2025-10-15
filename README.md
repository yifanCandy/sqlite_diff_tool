sqlite_compare_tool/
│
├── main.py                     # 入口：程序启动入口
│
├── ui/
│   ├── __init__.py             # 可以为空，用来标识这是一个 Python 包
│   ├── main_window.py          # 主窗口逻辑
│   └── dnd_entry.py            # 支持拖拽文件的输入框控件
│
├── core/
│   ├── __init__.py
│   ├── db_utils.py             # 执行 SQL 查询、差集计算、导出 CSV
│   └── diff_utils.py           # 专门放结果集比较逻辑（也可合并到 db_utils）
│
└── requirements.txt

使用 spec 文件打包
pyinstaller main.spec
