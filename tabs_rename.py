"""标签页① 批量改名 —— CustomTkinter 版"""

import os
import tkinter as tk
import customtkinter as ctk
from tkinter import messagebox
from datetime import datetime


def build_tab(app):
    for w in app.rule_frame.winfo_children():
        w.destroy()

    # ── 规则说明 ──
    ctk.CTkLabel(app.rule_frame, text="我希望这样命名我的文件：",
                 font=("Microsoft YaHei", 11), text_color=app.COLORS["text_primary"]
                 ).pack(anchor=tk.W, pady=(0, 10))

    # ── 命名规则选择 ──
    tabs_frame = ctk.CTkFrame(app.rule_frame, fg_color="transparent")
    tabs_frame.pack(fill=tk.X, pady=(0, 10))

    tab_vars = {
        "text": tk.BooleanVar(value=True),
        "date": tk.BooleanVar(value=False),
        "number": tk.BooleanVar(value=True),
        "filename": tk.BooleanVar(value=False),
    }

    tab_data = [("前缀文本", "text"), ("日期标记", "date"),
                ("编号排序", "number"), ("保留原名", "filename")]
    for text, key in tab_data:
        cb = ctk.CTkCheckBox(tabs_frame, text=text, variable=tab_vars[key],
                             font=("Microsoft YaHei", 10), checkbox_width=18,
                             checkbox_height=18, corner_radius=4)
        cb.pack(side=tk.LEFT, padx=6)

    # ── 输入框 ──
    fields_frame = ctk.CTkFrame(app.rule_frame, fg_color="transparent")
    fields_frame.pack(fill=tk.X, pady=(0, 10))

    def _make_row(parent, label_text, children_cb):
        row = ctk.CTkFrame(parent, fg_color="transparent")
        row.pack(fill=tk.X, pady=4)
        ctk.CTkLabel(row, text=label_text, font=("Microsoft YaHei", 10),
                     text_color=app.COLORS["text_primary"],
                     width=10, anchor=tk.W).pack(side=tk.LEFT)
        children_cb(row)
        return row

    def _prefix_row(row):
        nonlocal prefix_entry
        prefix_entry = ctk.CTkEntry(row, font=("Microsoft YaHei", 10),
                                     corner_radius=6, placeholder_text="例如：项目文件")
        prefix_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        prefix_entry.insert(0, "我的文件")

    def _date_row(row):
        nonlocal date_var, date_format_var
        date_var = tk.StringVar(value=datetime.now().strftime("%Y-%m-%d"))
        date_entry = ctk.CTkEntry(row, textvariable=date_var,
                                   font=("Microsoft YaHei", 10), width=110,
                                   corner_radius=6)
        date_entry.pack(side=tk.LEFT)
        date_format_var = ctk.StringVar(value="年-月-日")
        fmt_menu = ctk.CTkOptionMenu(row, variable=date_format_var,
                                      values=["年-月-日", "年/月/日", "年月日"],
                                      font=("Microsoft YaHei", 10),
                                      dropdown_font=("Microsoft YaHei", 10),
                                      corner_radius=6)
        fmt_menu.pack(side=tk.LEFT, padx=5)

    def _number_row(row):
        nonlocal number_var
        number_var = tk.StringVar(value="001")
        spin = tk.Spinbox(row, from_=1, to=9999, textvariable=number_var,
                          width=8, font=("Microsoft YaHei", 10),
                          relief=tk.SOLID, bd=1)
        spin.pack(side=tk.LEFT)
        ctk.CTkLabel(row, text="（自动补零）",
                     font=("Microsoft YaHei", 9),
                     text_color=app.COLORS["text_hint"]
                     ).pack(side=tk.LEFT, padx=6)

    prefix_entry = None
    date_var = None
    date_format_var = None
    number_var = None

    _make_row(fields_frame, "前缀文本：", _prefix_row)
    _make_row(fields_frame, "日期格式：", _date_row)
    _make_row(fields_frame, "起始编号：", _number_row)

    # ── 操作按钮 ──
    btn_frame = ctk.CTkFrame(app.rule_frame, fg_color="transparent")
    btn_frame.pack(fill=tk.X, pady=(12, 0))

    ctk.CTkButton(btn_frame, text="👁 预览新名称",
                  font=("Microsoft YaHei", 11, "bold"),
                  fg_color="#0891B2", hover_color="#0E7490",
                  corner_radius=6, height=40,
                  command=lambda: _preview(app, prefix_entry, date_var,
                                           date_format_var, number_var, tab_vars)
                  ).pack(fill=tk.X, pady=(0, 8))

    ctk.CTkButton(btn_frame, text="✅ 应用这些更改！",
                  font=("Microsoft YaHei", 11, "bold"),
                  fg_color=app.COLORS["primary"],
                  hover_color=app.COLORS["primary_hover"],
                  corner_radius=6, height=40,
                  command=lambda: _apply(app, prefix_entry, date_var,
                                         date_format_var, number_var, tab_vars)
                  ).pack(fill=tk.X)

    app.log("📝 批量改名模块已加载")


def _build_name(app, item, prefix, date_str, date_format, start_num,
                use_text, use_date, use_number, count):
    filename = item["name"]
    name_part, ext = os.path.splitext(filename)
    new_name = ""
    if use_text and prefix:
        new_name += prefix
    if use_date:
        if date_format == "年-月-日":
            dp = date_str.replace("-", "_")
        elif date_format == "年/月/日":
            dp = date_str.replace("/", "_")
        else:
            dp = date_str
        new_name += "_" + dp if new_name else dp
    if use_number:
        new_name += "_" + f"{start_num + count:03d}" if new_name else f"{start_num + count:03d}"
    if not new_name:
        new_name = name_part
    return new_name + ext


def _preview(app, prefix_entry, date_var, date_format_var, number_var, tab_vars):
    if not app.file_items:
        return messagebox.showwarning("提示", "请先选择文件夹并加载文件")
    use_text = tab_vars["text"].get()
    use_date = tab_vars["date"].get()
    use_number = tab_vars["number"].get()
    new_names = {}
    count = 0
    for item in app.file_items:
        full_new = _build_name(app, item,
                               prefix_entry.get().strip() if prefix_entry else "",
                               date_var.get() if date_var else "",
                               date_format_var.get() if date_format_var else "",
                               int(number_var.get() or "1") if number_var else 1,
                               use_text, use_date, use_number, count)
        new_names[item["name"]] = full_new
        count += 1
    app.refresh_file_list(new_names)
    app.log(f"👁 已预览 {count} 个文件的新名称")


def _apply(app, prefix_entry, date_var, date_format_var, number_var, tab_vars):
    if not app.file_items:
        return messagebox.showwarning("提示", "没有可重命名的文件")
    if not messagebox.askyesno("确认操作", "确定要应用这些更改吗？\n此操作可以撤销。"):
        return

    use_text = tab_vars["text"].get()
    use_date = tab_vars["date"].get()
    use_number = tab_vars["number"].get()
    prefix = prefix_entry.get().strip() if prefix_entry else ""
    date_str = date_var.get() if date_var else ""
    date_format = date_format_var.get() if date_format_var else ""
    start_num = int(number_var.get() or "1") if number_var else 1

    pairs = []
    count = 0
    for item in app.file_items:
        if not item["var"].get():
            continue
        filepath = item["path"]
        full_new = _build_name(app, item, prefix, date_str, date_format,
                                start_num, use_text, use_date, use_number, count)
        new_path = os.path.join(os.path.dirname(filepath), full_new)
        try:
            os.rename(filepath, new_path)
            pairs.append((filepath, new_path))
            count += 1
            item["name"] = full_new
            item["path"] = new_path
            item["label"].config(text=full_new, fg=app.COLORS["success"])
            item["status"].config(text="✅ 已完成", fg=app.COLORS["success"])
        except Exception as e:
            app.log(f"❌ 重命名失败: {item['name']} - {str(e)}")

    if pairs:
        app.push_undo("rename", f"批量重命名 {count} 个文件", pairs)
        messagebox.showinfo("✅ 完成", f"成功重命名 {count} 个文件")
        app._update_status()
    else:
        messagebox.showwarning("提示", "没有文件被重命名")
