"""共享工具函数：后台线程、滚动列表、通用辅助"""

import threading
import tkinter as tk
from tkinter import ttk


def run_in_background(func, on_done=None, on_error=None):
    """在后台线程执行函数，防止 UI 卡死。"""
    def wrapper():
        try:
            result = func()
            if on_done:
                on_done(result)
        except Exception as e:
            if on_error:
                on_error(str(e))
    threading.Thread(target=wrapper, daemon=True).start()


def build_scrollable_checkbox_list(parent, height=100):
    """构建可滚动的多选列表容器，返回 (canvas, inner_frame, check_vars_dict)。

    用法：
        canvas, inner_frame, check_vars = build_scrollable_checkbox_list(parent, height=80)
        # 往里添加选项：
        for item in items:
            v = tk.BooleanVar()
            tk.Checkbutton(inner_frame, text=item, variable=v).pack(anchor=tk.W, fill=tk.X)
            check_vars[item] = v
    """
    container = tk.Frame(parent)
    container.pack(fill=tk.BOTH, expand=True)

    canvas = tk.Canvas(container, height=height, highlightthickness=0)
    scrollbar = ttk.Scrollbar(container, orient=tk.VERTICAL, command=canvas.yview)
    inner_frame = tk.Frame(canvas)

    inner_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
    )
    canvas.create_window((0, 0), window=inner_frame, anchor=tk.NW)
    canvas.config(yscrollcommand=scrollbar.set)

    canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    check_vars = {}
    return canvas, inner_frame, check_vars
