"""标签页④ 清理查重 —— CustomTkinter 版"""

import os
import hashlib
import tkinter as tk
import customtkinter as ctk
from tkinter import messagebox, filedialog
from utils import run_in_background

REDUNDANT_EXTS = {".tmp", ".temp", ".log", ".cache", ".bak", ".swp", ".~"}
REDUNDANT_NAMES = {"desktop.ini", "thumbs.db", ".ds_store"}


def _section_title(parent, text):
    return ctk.CTkLabel(parent, text=text,
                        font=("Microsoft YaHei", 11, "bold"),
                        text_color=app.COLORS["text_primary"],
                        anchor=tk.W)


def build_tab(app):
    for w in app.rule_frame.winfo_children():
        w.destroy()

    # ── 路径 ──
    pf = ctk.CTkFrame(app.rule_frame, fg_color="transparent")
    pf.pack(fill=tk.X, pady=(0, 12))
    ctk.CTkLabel(pf, text="目标文件夹：", font=("Microsoft YaHei", 10),
                 text_color=app.COLORS["text_primary"]).pack(side=tk.LEFT)
    path_entry = ctk.CTkEntry(pf, font=("Microsoft YaHei", 10),
                               corner_radius=6)
    path_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
    path_entry.insert(0, os.getcwd())
    ctk.CTkButton(pf, text="📂 浏览",
                  font=("Microsoft YaHei", 9),
                  fg_color="#E8F0FE", hover_color="#DBE5F5",
                  text_color=app.COLORS["primary"],
                  corner_radius=6, width=80, height=30,
                  command=lambda: _browse(app, path_entry)).pack(side=tk.LEFT)

    # ── 模块容器 ──
    def make_module(title, desc, btn_text, btn_color, btn_hover, on_click,
                    extra=None):
        frame = ctk.CTkFrame(app.rule_frame, fg_color="#F8FAFC", corner_radius=8)
        frame.pack(fill=tk.X, pady=(0, 10))

        ctk.CTkLabel(frame, text=title, font=("Microsoft YaHei", 11, "bold"),
                     text_color=app.COLORS["text_primary"]
                     ).pack(anchor=tk.W, padx=12, pady=(8, 2))
        ctk.CTkLabel(frame, text=desc, font=("Microsoft YaHei", 9),
                     text_color=app.COLORS["text_secondary"],
                     wraplength=380
                     ).pack(anchor=tk.W, padx=12, pady=(0, 4))
        if extra:
            extra(frame)
        ctk.CTkButton(frame, text=btn_text,
                      font=("Microsoft YaHei", 10, "bold"),
                      fg_color=btn_color, hover_color=btn_hover,
                      corner_radius=6, height=34,
                      command=on_click
                      ).pack(anchor=tk.W, padx=12, pady=6)

    # 1 ── 删除重复文件
    dup_recursive = tk.BooleanVar(value=True)

    def _dup_extra(frame):
        cb = ctk.CTkCheckBox(frame, text="包含子文件夹", variable=dup_recursive,
                              font=("Microsoft YaHei", 9), checkbox_width=18,
                              checkbox_height=18, corner_radius=4)
        cb.pack(anchor=tk.W, padx=12, pady=(0, 2))

    make_module("🔍 删除重复文件",
                "通过 MD5 哈希识别内容完全相同的文件，自动保留最新文件",
                "执行查重删除",
                app.COLORS["danger"], app.COLORS["danger_hover"],
                lambda: _remove_duplicates(app, path_entry, dup_recursive.get()),
                extra=_dup_extra)

    # 2 ── 清理空文件夹
    make_module("📂 清理空文件夹",
                "删除指定文件夹下所有空的子文件夹（自动跳过 .git / __pycache__）",
                "清理空文件夹",
                "#F59E0B", "#D97706",
                lambda: _clean_empty(app, path_entry))

    # 3 ── 清理冗余文件
    make_module("🗑 清理冗余文件",
                "删除常见的垃圾文件（.tmp / .log / .bak / desktop.ini 等）",
                "清理冗余文件",
                "#8B5CF6", "#7C3AED",
                lambda: _clean_redundant(app, path_entry))

    # ⚠️ 安全提示
    ctk.CTkLabel(app.rule_frame, text="⚠️ 注意：清理操作不可撤销！请谨慎操作。",
                 font=("Microsoft YaHei", 9), text_color=app.COLORS["danger"],
                 wraplength=350
                 ).pack(pady=(4, 0), anchor=tk.W, padx=4)

    app.log("🧹 清理 & 去重模块已加载")


def _browse(app, path_entry):
    folder = filedialog.askdirectory()
    if folder:
        path_entry.delete(0, tk.END)
        path_entry.insert(0, folder)


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


def _remove_duplicates(app, path_entry, recursive):
    folder = path_entry.get().strip()
    if not folder or not os.path.isdir(folder):
        return messagebox.showwarning("提示", "请先选择有效的文件夹")
    if not messagebox.askyesno("⚠️ 警告",
                                "此操作会永久删除重复文件！\n建议先备份。确定继续吗？"):
        return

    def do():
        files = _get_all_files(folder, recursive)
        hm = {}
        dup = []
        for fp in files:
            try:
                h = hashlib.md5()
                with open(fp, "rb") as f:
                    h.update(f.read())
                md5 = h.hexdigest()
                if md5 in hm:
                    if os.path.getmtime(fp) > os.path.getmtime(hm[md5]):
                        dup.append(hm[md5])
                        hm[md5] = fp
                    else:
                        dup.append(fp)
                else:
                    hm[md5] = fp
            except Exception:
                continue
        cnt = 0
        for fp in dup:
            try:
                os.remove(fp)
                cnt += 1
            except Exception:
                continue
        return cnt

    def done(cnt):
        app.log(f"🔍 删除重复文件完成，删除了 {cnt} 个重复文件")
        messagebox.showinfo("✅ 完成", f"成功删除 {cnt} 个重复文件")
    run_in_background(do, done)


def _clean_empty(app, path_entry):
    folder = path_entry.get().strip()
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
        app.log(f"📂 清理空文件夹完成，删除了 {cnt} 个空文件夹")
        messagebox.showinfo("✅ 完成", f"成功删除 {cnt} 个空文件夹")
    run_in_background(do, done)


def _clean_redundant(app, path_entry):
    folder = path_entry.get().strip()
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
        app.log(f"🗑 清理冗余文件完成，删除了 {cnt} 个冗余文件")
        messagebox.showinfo("✅ 完成", f"成功删除 {cnt} 个冗余文件")
    run_in_background(do, done)
