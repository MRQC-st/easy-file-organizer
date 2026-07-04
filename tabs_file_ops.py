"""标签页③ 文件操作 —— CustomTkinter 版"""

import os
import shutil
import datetime
import tkinter as tk
import customtkinter as ctk
from tkinter import messagebox, filedialog
from utils import run_in_background


def build_tab(app):
    for w in app.rule_frame.winfo_children():
        w.destroy()

    # ── 模块：批量移动 ──
    _make_ops_module(app, "📦 批量移动文件",
                     "将所有选中文件移动到另一个文件夹",
                     "📦 选择目标文件夹并移动",
                     app.COLORS["success"], app.COLORS["success_hover"],
                     lambda: _batch_move(app))

    # ── 模块：批量复制 ──
    _make_ops_module(app, "📋 批量复制文件",
                     "将所有选中文件复制到另一个文件夹（保留原文件）",
                     "📋 选择目标文件夹并复制",
                     app.COLORS["primary"], app.COLORS["primary_hover"],
                     lambda: _batch_copy(app))

    # ── 模块：一键备份 ──
    _make_ops_module(app, "💾 一键备份",
                     "创建整个文件夹的 ZIP 压缩包备份",
                     "💾 选择保存位置并备份",
                     app.COLORS["warning"], app.COLORS["warning_hover"],
                     lambda: _backup(app))

    app.log("📦 文件操作模块已加载")


def _make_ops_module(app, title, desc, btn_text, btn_color, btn_hover, cmd):
    frame = ctk.CTkFrame(app.rule_frame, fg_color="#F8FAFC", corner_radius=8)
    frame.pack(fill=tk.X, pady=(0, 1))

    ctk.CTkLabel(frame, text=title, font=("Microsoft YaHei", 10, "bold"),
                 text_color=app.COLORS["text_primary"]
                 ).pack(anchor=tk.W, padx=10, pady=(6, 1))
    ctk.CTkLabel(frame, text=desc, font=("Microsoft YaHei", 9),
                 text_color=app.COLORS["text_secondary"],
                 wraplength=380
                 ).pack(anchor=tk.W, padx=10, pady=(0, 1))
    ctk.CTkButton(frame, text=btn_text,
                  font=("Microsoft YaHei", 10, "bold"),
                  fg_color=btn_color, hover_color=btn_hover,
                  corner_radius=5, height=28,
                  command=cmd
                  ).pack(anchor=tk.W, padx=10, pady=3)


def _get_files(folder):
    return [os.path.join(folder, f) for f in os.listdir(folder)
            if not f.startswith(".") and os.path.isfile(os.path.join(folder, f))]


def _batch_move(app):
    src = app.path_display.get().strip()
    if not src or not os.path.isdir(src):
        return messagebox.showwarning("提示", "请先选择有效的源文件夹")
    dst = filedialog.askdirectory(title="选择目标文件夹")
    if not dst:
        return
    if src == dst:
        return messagebox.showwarning("提示", "源文件夹和目标文件夹不能相同")
    files = _get_files(src)
    if not files:
        return messagebox.showinfo("提示", "源文件夹中没有文件")
    if not messagebox.askyesno("确认操作",
                                f"确定要将 {len(files)} 个文件移动到\n{dst} 吗？\n此操作可以撤销。"):
        return

    def do():
        pairs = [(fp, os.path.join(dst, os.path.basename(fp))) for fp in files]
        for old, new in pairs:
            shutil.move(old, new)
        return pairs

    def done(pairs):
        app.clear_processing()
        app.push_undo("move", "批量移动", pairs)
        app.log(f"📦 批量移动完成，移动了 {len(pairs)} 个文件")
        messagebox.showinfo("✅ 完成", f"成功移动 {len(pairs)} 个文件")
    app.set_processing("⏳ 正在批量移动...")
    run_in_background(do, done)


def _batch_copy(app):
    src = app.path_display.get().strip()
    if not src or not os.path.isdir(src):
        return messagebox.showwarning("提示", "请先选择有效的源文件夹")
    dst = filedialog.askdirectory(title="选择目标文件夹")
    if not dst:
        return
    if src == dst:
        return messagebox.showwarning("提示", "源文件夹和目标文件夹不能相同")
    files = _get_files(src)
    if not files:
        return messagebox.showinfo("提示", "源文件夹中没有文件")
    if not messagebox.askyesno("确认操作",
                                f"确定要将 {len(files)} 个文件复制到\n{dst} 吗？"):
        return

    def do():
        cnt = 0
        for fp in files:
            shutil.copy2(fp, os.path.join(dst, os.path.basename(fp)))
            cnt += 1
        return cnt

    def done(cnt):
        app.clear_processing()
        app.log(f"📋 批量复制完成，复制了 {cnt} 个文件")
        messagebox.showinfo("✅ 完成", f"成功复制 {cnt} 个文件")
    app.set_processing("⏳ 正在批量复制...")
    run_in_background(do, done)


def _backup(app):
    folder = app.path_display.get().strip()
    if not folder or not os.path.isdir(folder):
        return messagebox.showwarning("提示", "请先选择有效的文件夹")

    folder_name = os.path.basename(folder)
    date_str = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    default_name = f"{folder_name}_备份_{date_str}"
    save_path = filedialog.asksaveasfilename(
        title="保存备份文件", defaultextension=".zip",
        filetypes=[("压缩文件", "*.zip")], initialfile=default_name)
    if not save_path:
        return

    def do():
        zip_base = save_path.replace(".zip", "")
        shutil.make_archive(zip_base, "zip", folder)
        return save_path

    def done(path):
        app.clear_processing()
        app.log(f"💾 备份完成: {path}")
        messagebox.showinfo("✅ 备份成功", f"备份文件已保存至：\n{path}")
    app.set_processing("⏳ 正在备份...")
    run_in_background(do, done)
