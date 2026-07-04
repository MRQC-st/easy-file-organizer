"""标签页② 分类整理 —— CustomTkinter 版"""

import os
import shutil
import datetime
import tkinter as tk
import customtkinter as ctk
from tkinter import messagebox, filedialog
from utils import run_in_background

TYPE_MAP = {
    "照片": [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp", ".svg"],
    "文档": [".doc", ".docx", ".pdf", ".txt", ".xls", ".xlsx", ".ppt",
             ".pptx", ".md", ".csv", ".json", ".xml"],
    "视频": [".mp4", ".avi", ".mov", ".mkv", ".wmv", ".flv"],
    "音频": [".mp3", ".wav", ".flac", ".aac", ".ogg"],
    "压缩包": [".zip", ".rar", ".7z", ".tar", ".gz"],
}


def build_tab(app):
    for w in app.rule_frame.winfo_children():
        w.destroy()

    # ── 整理模式选择 ──
    mode_frame = ctk.CTkFrame(app.rule_frame, fg_color="transparent")
    mode_frame.pack(fill=tk.X, pady=(0, 1))

    ctk.CTkLabel(mode_frame, text="选择整理模式：",
                 font=("Microsoft YaHei", 10, "bold"),
                 text_color=app.COLORS["text_primary"]
                 ).pack(anchor=tk.W, pady=(0, 1))

    mode_var = ctk.StringVar(value="type")
    radio_frame = ctk.CTkFrame(mode_frame, fg_color="transparent")
    radio_frame.pack(fill=tk.X)

    ctk.CTkRadioButton(radio_frame, text="📁 按文件类型整理",
                       variable=mode_var, value="type",
                       font=("Microsoft YaHei", 9),
                       command=lambda: _refresh(app, content_frame, mode_var)
                       ).pack(side=tk.LEFT, padx=6)
    ctk.CTkRadioButton(radio_frame, text="📅 按修改日期整理",
                       variable=mode_var, value="date",
                       font=("Microsoft YaHei", 9),
                       command=lambda: _refresh(app, content_frame, mode_var)
                       ).pack(side=tk.LEFT, padx=6)

    content_frame = ctk.CTkFrame(app.rule_frame, fg_color="transparent")
    content_frame.pack(fill=tk.X, pady=(0, 1))
    _build_type_content(app, content_frame)

    # ── 执行 ──
    btn_frame = ctk.CTkFrame(app.rule_frame, fg_color="transparent")
    btn_frame.pack(fill=tk.X, pady=(1, 0))

    ctk.CTkButton(btn_frame, text="✅ 开始整理文件！",
                  font=("Microsoft YaHei", 10, "bold"),
                  fg_color=app.COLORS["primary"],
                  hover_color=app.COLORS["primary_hover"],
                  corner_radius=5, height=28,
                  command=lambda: _do_organize(app, mode_var.get())
                  ).pack(fill=tk.X)

    app.log("📂 整理模块已加载")


def _refresh(app, parent, mode_var):
    for w in parent.winfo_children():
        w.destroy()
    if mode_var.get() == "type":
        _build_type_content(app, parent)
    else:
        _build_date_content(app, parent)


def _build_type_content(app, parent):
    info = ctk.CTkFrame(parent, fg_color="#F8FAFC", corner_radius=5)
    info.pack(fill=tk.X)

    ctk.CTkLabel(info,
                 text="将按文件扩展名自动分类到：照片 / 文档 / 视频 / 音频 / 压缩包 / 其他",
                 font=("Microsoft YaHei", 9),
                 text_color=app.COLORS["text_secondary"],
                 fg_color="transparent", wraplength=380
                 ).pack(padx=12, pady=8, anchor=tk.W)

    tf = ctk.CTkFrame(info, fg_color="transparent")
    tf.pack(padx=10, pady=(0, 1), fill=tk.X)
    colors = ["#FF6B6B", "#45B7D1", "#4ECDC4", "#FF9800", "#96CEB4"]
    for i, (cat, _) in enumerate(TYPE_MAP.items()):
        ctk.CTkLabel(tf, text=f"📁 {cat}", font=("Microsoft YaHei", 9),
                     text_color=colors[i % len(colors)]
                     ).pack(side=tk.LEFT, padx=4)


def _build_date_content(app, parent):
    info = ctk.CTkFrame(parent, fg_color="#F8FAFC", corner_radius=5)
    info.pack(fill=tk.X)

    ctk.CTkLabel(info,
                 text="将根据文件修改日期自动归类到年/月文件夹",
                 font=("Microsoft YaHei", 9),
                 text_color=app.COLORS["text_secondary"],
                 fg_color="transparent", wraplength=380
                 ).pack(padx=12, pady=8, anchor=tk.W)

    ff = ctk.CTkFrame(info, fg_color="transparent")
    ff.pack(padx=10, pady=(0, 1), fill=tk.X)

    ctk.CTkLabel(ff, text="日期格式：", font=("Microsoft YaHei", 9)
                 ).pack(side=tk.LEFT)

    date_fmt = ctk.StringVar(value="年/月")
    ctk.CTkOptionMenu(ff, variable=date_fmt,
                      values=["年/月", "仅年份", "仅月份"],
                      font=("Microsoft YaHei", 9),
                      dropdown_font=("Microsoft YaHei", 9),
                      corner_radius=5
                      ).pack(side=tk.LEFT, padx=4)

    parent.date_fmt = date_fmt


def _get_files(folder):
    return [os.path.join(folder, f) for f in os.listdir(folder)
            if not f.startswith(".") and os.path.isfile(os.path.join(folder, f))]


def _do_organize(app, mode):
    folder = app.path_display.get().strip()
    if not folder or not os.path.isdir(folder):
        return messagebox.showwarning("提示", "请先选择有效的文件夹")
    files = _get_files(folder)
    if not files:
        return messagebox.showinfo("提示", "文件夹中没有文件")
    if not messagebox.askyesno("确认操作",
                                f"确定要整理 {len(files)} 个文件吗？\n此操作可以撤销。"):
        return
    if mode == "type":
        _organize_by_type(app, folder, files)
    else:
        _organize_by_date(app, folder, files)


def _organize_by_type(app, folder, files):
    def do():
        pairs = []
        for fp in files:
            ext = os.path.splitext(fp)[1].lower()
            cat = "其他"
            for c, exts in TYPE_MAP.items():
                if ext in exts:
                    cat = c
                    break
            td = os.path.join(folder, cat)
            os.makedirs(td, exist_ok=True)
            np = os.path.join(td, os.path.basename(fp))
            if fp != np:
                shutil.move(fp, np)
                pairs.append((fp, np))
        return pairs

    def done(pairs):
        app.clear_processing()
        if pairs:
            app.push_undo("move", "按类型整理", pairs)
            app.log(f"📂 按类型整理完成，移动了 {len(pairs)} 个文件")
            messagebox.showinfo("✅ 完成", f"成功整理 {len(pairs)} 个文件")
        else:
            messagebox.showinfo("提示", "没有文件需要移动")
    app.set_processing("⏳ 正在按类型整理...")
    run_in_background(do, done)


def _organize_by_date(app, folder, files):
    def do():
        pairs = []
        for fp in files:
            mtime = os.path.getmtime(fp)
            date_str = datetime.datetime.fromtimestamp(mtime).strftime("%Y-%m")
            td = os.path.join(folder, date_str)
            os.makedirs(td, exist_ok=True)
            np = os.path.join(td, os.path.basename(fp))
            if fp != np:
                shutil.move(fp, np)
                pairs.append((fp, np))
        return pairs

    def done(pairs):
        app.clear_processing()
        if pairs:
            app.push_undo("move", "按日期整理", pairs)
            app.log(f"📅 按日期整理完成，移动了 {len(pairs)} 个文件")
            messagebox.showinfo("✅ 完成", f"成功整理 {len(pairs)} 个文件")
        else:
            messagebox.showinfo("提示", "没有文件需要移动")
    app.set_processing("⏳ 正在按日期整理...")
    run_in_background(do, done)
