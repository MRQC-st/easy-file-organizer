"""标签页④ 清理查重 —— CustomTkinter 版"""

import os
import hashlib
import datetime
import tkinter as tk
import customtkinter as ctk
from tkinter import messagebox, filedialog
from utils import run_in_background

REDUNDANT_EXTS = {".tmp", ".temp", ".log", ".cache", ".bak", ".swp", ".~"}
REDUNDANT_NAMES = {"desktop.ini", "thumbs.db", ".ds_store"}


def build_tab(app):
    for w in app.rule_frame.winfo_children():
        w.destroy()

    # ── 模块容器 ──
    def make_module(title, desc, btn_text, btn_color, btn_hover, on_click,
                    extra=None):
        frame = ctk.CTkFrame(app.rule_frame, fg_color="#F8FAFC", corner_radius=8)
        frame.pack(fill=tk.X, pady=(0, 1))

        ctk.CTkLabel(frame, text=title, font=("Microsoft YaHei", 10, "bold"),
                     text_color=app.COLORS["text_primary"]
                     ).pack(anchor=tk.W, padx=10, pady=(6, 1))
        ctk.CTkLabel(frame, text=desc, font=("Microsoft YaHei", 9),
                     text_color=app.COLORS["text_secondary"],
                     wraplength=380
                     ).pack(anchor=tk.W, padx=10, pady=(0, 1))
        if extra:
            extra(frame)
        ctk.CTkButton(frame, text=btn_text,
                      font=("Microsoft YaHei", 10, "bold"),
                      fg_color=btn_color, hover_color=btn_hover,
                      corner_radius=5, height=28,
                      command=on_click
                      ).pack(anchor=tk.W, padx=10, pady=3)

    # 1 ── 删除重复文件
    dup_recursive = tk.BooleanVar(value=True)

    def _dup_extra(frame):
        cb = ctk.CTkCheckBox(frame, text="包含子文件夹", variable=dup_recursive,
                              font=("Microsoft YaHei", 9), checkbox_width=16,
                              checkbox_height=16, corner_radius=3)
        cb.pack(anchor=tk.W, padx=10, pady=(0, 1))

    make_module("🔍 删除重复文件",
                "通过 MD5 哈希识别内容完全相同的文件，自动保留最新文件",
                "执行查重删除",
                app.COLORS["danger"], app.COLORS["danger_hover"],
                lambda: _remove_duplicates(app, dup_recursive.get()),
                extra=_dup_extra)

    # 2 ── 清理空文件夹
    make_module("📂 清理空文件夹",
                "删除指定文件夹下所有空的子文件夹（自动跳过 .git / __pycache__）",
                "清理空文件夹",
                "#F59E0B", "#D97706",
                lambda: _clean_empty(app))

    # 3 ── 清理冗余文件
    make_module("🗑 清理冗余文件",
                "删除常见的垃圾文件（.tmp / .log / .bak / desktop.ini 等）",
                "清理冗余文件",
                "#8B5CF6", "#7C3AED",
                lambda: _clean_redundant(app))

    # ⚠️ 安全提示
    ctk.CTkLabel(app.rule_frame, text="⚠️ 注意：清理操作不可撤销！请谨慎操作。",
                 font=("Microsoft YaHei", 9), text_color=app.COLORS["danger"],
                 wraplength=350
                 ).pack(pady=(2, 0), anchor=tk.W, padx=4)

    app.log("🧹 清理 & 去重模块已加载")


def _get_all_files(folder, recursive=True):
    files = []
    skip = {".git", "__pycache__", ".ipynb_checkpoints"}
    if recursive:
        for root, dirs, fnames in os.walk(folder):
            dirs[:] = [d for d in dirs if d not in skip]
            for f in fnames:
                if not f.startswith("."):
                    files.append(os.path.join(root, f))
    else:
        for item in os.listdir(folder):
            if not item.startswith("."):
                p = os.path.join(folder, item)
                if os.path.isfile(p):
                    files.append(p)
    return files


def _format_size(size_bytes):
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} KB"
    else:
        return f"{size_bytes / (1024*1024):.1f} MB"


def _remove_duplicates(app, recursive):
    folder = app.path_display.get().strip()
    if not folder or not os.path.isdir(folder):
        return messagebox.showwarning("提示", "请先选择有效的文件夹")

    # 第一步：扫描重复文件
    if getattr(app, '_dup_scanning', False):
        return  # 正在扫描中，忽略重复点击

    app._dup_scanning = True

    def scan():
        files = _get_all_files(folder, recursive)
        hm = {}
        for fp in files:
            try:
                h = hashlib.md5()
                with open(fp, "rb") as f:
                    h.update(f.read())
                md5 = h.hexdigest()
                if md5 in hm:
                    hm[md5].append(fp)
                else:
                    hm[md5] = [fp]
            except Exception:
                continue
        groups = {k: v for k, v in hm.items() if len(v) > 1}
        return groups

    def on_scan_done(groups):
        app._dup_scanning = False
        app.clear_processing()
        if not groups:
            messagebox.showinfo("✅ 查重结果", "没有发现重复文件！")
            return
        _show_dup_selector(app, folder, groups)

    def on_scan_error(e):
        app._dup_scanning = False
        app.clear_processing()
        messagebox.showerror("❌ 失败", f"查重出错: {e}")

    app.set_processing("⏳ 正在扫描重复文件...")
    run_in_background(scan, on_scan_done, on_error=on_scan_error)


def _show_dup_selector(app, folder, groups):
    """弹出窗口让用户选择每组重复文件中保留哪些"""
    win = ctk.CTkToplevel(app)
    win.title("🔍 重复文件选择")
    win.geometry("700x500")
    win.minsize(500, 300)
    win.configure(fg_color="#F0F4F8")
    win.grab_set()

    # 标题
    ctk.CTkLabel(win, text=f"发现 {len(groups)} 组重复文件，请选择每组中要保留的文件：",
                 font=("Microsoft YaHei", 12, "bold"),
                 text_color=app.COLORS["text_primary"]
                 ).pack(anchor=tk.W, padx=16, pady=(12, 4))

    # 滚动区域
    scroll_frame = tk.Frame(win)
    scroll_frame.pack(fill=tk.BOTH, expand=True, padx=12, pady=(4, 8))

    canvas = tk.Canvas(scroll_frame, highlightthickness=0, bg="#F0F4F8")
    scrollbar = tk.Scrollbar(scroll_frame, orient=tk.VERTICAL, command=canvas.yview)
    inner = tk.Frame(canvas, bg="#F0F4F8")

    inner.bind("<Configure>",
               lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
    canvas.create_window((0, 0), window=inner, anchor=tk.NW)
    canvas.config(yscrollcommand=scrollbar.set)

    canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    group_vars = {}

    for idx, (md5, fps) in enumerate(sorted(groups.items(),
                                              key=lambda x: -len(x[1]))):
        fps_sorted = sorted(fps, key=lambda p: os.path.getmtime(p), reverse=True)

        group_frame = ctk.CTkFrame(inner, fg_color="white", corner_radius=8)
        group_frame.pack(fill=tk.X, pady=(0, 1), padx=4)

        ctk.CTkLabel(group_frame,
                     text=f"重复组 {idx + 1}（{len(fps_sorted)} 个文件，内容相同）",
                     font=("Microsoft YaHei", 10, "bold"),
                     text_color=app.COLORS["text_primary"]
                     ).pack(anchor=tk.W, padx=12, pady=(8, 4))

        vars_dict = {}
        for fp in fps_sorted:
            row = tk.Frame(group_frame, bg="white")
            row.pack(fill=tk.X, padx=12, pady=1)

            rel = os.path.relpath(fp, folder)
            size = _format_size(os.path.getsize(fp))
            mtime = datetime.datetime.fromtimestamp(
                os.path.getmtime(fp)).strftime("%Y-%m-%d %H:%M")

            v = tk.BooleanVar(value=(fp == fps_sorted[0]))
            vars_dict[fp] = v

            cb = tk.Checkbutton(row, variable=v, bg="white",
                                activebackground="white", bd=0)
            cb.pack(side=tk.LEFT)

            info_text = f"{rel}  |  {size}  |  修改: {mtime}"
            tk.Label(row, text=info_text, font=("Microsoft YaHei", 9),
                     bg="white", fg=app.COLORS["text_primary"],
                     anchor=tk.W).pack(side=tk.LEFT, padx=(4, 0))

        group_vars[md5] = vars_dict

    # 底部按钮
    btn_frame = ctk.CTkFrame(win, fg_color="transparent")
    btn_frame.pack(fill=tk.X, padx=10, pady=(0, 8))

    summary_label = ctk.CTkLabel(btn_frame, text="",
                                  font=("Microsoft YaHei", 9),
                                  text_color=app.COLORS["text_secondary"])
    summary_label.pack(side=tk.LEFT)

    def update_summary():
        to_delete = sum(
            len(vars_dict) - sum(v.get() for v in vars_dict.values())
            for vars_dict in group_vars.values()
        )
        to_keep = sum(sum(v.get() for v in d.values()) for d in group_vars.values())
        summary_label.configure(text=f"将删除 {to_delete} 个文件，保留 {to_keep} 个")

    for vars_dict in group_vars.values():
        for v in vars_dict.values():
            v.trace_add("write", lambda *a: update_summary())
    update_summary()

    def on_confirm():
        to_delete = []
        for md5, vars_dict in group_vars.items():
            for fp, v in vars_dict.items():
                if not v.get():
                    to_delete.append(fp)

        if not to_delete:
            messagebox.showinfo("提示", "所有文件都被标记为保留，没有文件需要删除。")
            return

        if not messagebox.askyesno("⚠️ 确认删除",
                                    f"确定要删除以下 {len(to_delete)} 个重复文件吗？\n此操作不可撤销！"):
            return

        def do():
            cnt = 0
            for fp in to_delete:
                try:
                    os.remove(fp)
                    cnt += 1
                except Exception:
                    continue
            return cnt

        def done(cnt):
            app.clear_processing()
            app.log(f"🔍 删除重复文件完成，删除了 {cnt} 个文件")
            messagebox.showinfo("✅ 完成", f"成功删除 {cnt} 个重复文件")
            win.destroy()

        def error(e):
            app.clear_processing()
            app.log(f"❌ 删除失败: {e}")
            messagebox.showerror("❌ 失败", f"操作出错: {e}")
            win.destroy()

        app.set_processing("⏳ 正在删除重复文件...")
        win.destroy()
        run_in_background(do, done, error)

    def on_cancel():
        win.destroy()

    ctk.CTkButton(btn_frame, text="❌ 取消",
                  font=("Microsoft YaHei", 9),
                  fg_color="white", hover_color="#F1F5F9",
                  text_color=app.COLORS["text_primary"],
                  corner_radius=5, width=80, height=28,
                  command=on_cancel).pack(side=tk.RIGHT, padx=(8, 0))

    ctk.CTkButton(btn_frame, text="🗑 确认删除选中文件",
                  font=("Microsoft YaHei", 10, "bold"),
                  fg_color=app.COLORS["danger"],
                  hover_color=app.COLORS["danger_hover"],
                  corner_radius=5, width=160, height=28,
                  command=on_confirm).pack(side=tk.RIGHT)


def _clean_empty(app):
    folder = app.path_display.get().strip()
    if not folder or not os.path.isdir(folder):
        return messagebox.showwarning("提示", "请先选择有效的文件夹")
    if not messagebox.askyesno("确认", "确定要删除所有空文件夹吗？"):
        return

    def do():
        cnt = 0
        for root, dirs, _ in os.walk(folder, topdown=False):
            for d in dirs:
                if d in (".git", "__pycache__"):
                    continue
                dp = os.path.join(root, d)
                try:
                    if not os.listdir(dp):
                        os.rmdir(dp)
                        cnt += 1
                except Exception:
                    continue
        return cnt

    def done(cnt):
        app.clear_processing()
        app.log(f"📂 清理空文件夹完成，删除了 {cnt} 个空文件夹")
        messagebox.showinfo("✅ 完成", f"成功删除 {cnt} 个空文件夹")
    app.set_processing("⏳ 正在清理空文件夹...")
    run_in_background(do, done)


def _clean_redundant(app):
    folder = app.path_display.get().strip()
    if not folder or not os.path.isdir(folder):
        return messagebox.showwarning("提示", "请先选择有效的文件夹")
    if not messagebox.askyesno("确认",
                                "确定要删除所有冗余/临时文件吗？\n"
                                "（.tmp .log .bak desktop.ini Thumbs.db 等）"):
        return

    def do():
        cnt = 0
        for root, dirs, fnames in os.walk(folder):
            dirs[:] = [d for d in dirs if d not in (".git", "__pycache__")]
            for f in fnames:
                ext = os.path.splitext(f)[1].lower()
                if ext in REDUNDANT_EXTS or f.lower() in REDUNDANT_NAMES:
                    try:
                        os.remove(os.path.join(root, f))
                        cnt += 1
                    except Exception:
                        continue
        return cnt

    def done(cnt):
        app.clear_processing()
        app.log(f"🗑 清理冗余文件完成，删除了 {cnt} 个冗余文件")
        messagebox.showinfo("✅ 完成", f"成功删除 {cnt} 个冗余文件")
    app.set_processing("⏳ 正在清理冗余文件...")
    run_in_background(do, done)