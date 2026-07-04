"""标签页⑤ 数据导出 —— CustomTkinter 版"""

import os
import tkinter as tk
import customtkinter as ctk
from tkinter import messagebox, filedialog
from datetime import datetime
from utils import run_in_background

# 顶部导入，确保 PyInstaller 打包时能检测到 pandas / openpyxl
try:
    import pandas as pd  # noqa: F401
    _PANDAS_OK = True
except ImportError:
    _PANDAS_OK = False


def build_tab(app):
    for w in app.rule_frame.winfo_children():
        w.destroy()

    # ── 导出设置 ──
    opt_frame = ctk.CTkFrame(app.rule_frame, fg_color="#F8FAFC", corner_radius=8)
    opt_frame.pack(fill=tk.X, pady=(0, 8))

    ctk.CTkLabel(opt_frame, text="⚙️ 导出设置",
                 font=("Microsoft YaHei", 10, "bold"),
                 text_color=app.COLORS["text_primary"]
                 ).pack(anchor=tk.W, padx=12, pady=(8, 4))

    recursive_var = tk.BooleanVar(value=True)
    ctk.CTkCheckBox(opt_frame, text="包含子文件夹", variable=recursive_var,
                    font=("Microsoft YaHei", 9),
                    checkbox_width=18, checkbox_height=18, corner_radius=4
                    ).pack(anchor=tk.W, padx=12, pady=4)

    ctk.CTkLabel(opt_frame,
                 text="导出的文件清单包含：文件名 | 大小(KB) | 修改时间",
                 font=("Microsoft YaHei", 9),
                 text_color=app.COLORS["text_secondary"]
                 ).pack(anchor=tk.W, padx=10, pady=(0, 1))

    # ── 按钮 ──
    btn_frame = ctk.CTkFrame(app.rule_frame, fg_color="transparent")
    btn_frame.pack(fill=tk.X, pady=(6, 0))

    ctk.CTkButton(btn_frame, text="📄 导出为 TXT",
                  font=("Microsoft YaHei", 10, "bold"),
                  fg_color="#0891B2", hover_color="#0E7490",
                  corner_radius=5, height=28,
                  command=lambda: _export_txt(app, recursive_var.get())
                  ).pack(fill=tk.X, pady=(0, 1))

    ctk.CTkButton(btn_frame, text="📊 导出为 Excel",
                  font=("Microsoft YaHei", 10, "bold"),
                  fg_color=app.COLORS["primary"],
                  hover_color=app.COLORS["primary_hover"],
                  corner_radius=5, height=28,
                  command=lambda: _export_xlsx(app, recursive_var.get())
                  ).pack(fill=tk.X)

    app.log("📊 数据导出模块已加载")


def _get_files_info(folder, recursive):
    results = []
    if recursive:
        for root, dirs, fnames in os.walk(folder):
            dirs[:] = [d for d in dirs if d not in (".git", "__pycache__")]
            for f in fnames:
                fp = os.path.join(root, f)
                try:
                    s = os.stat(fp)
                    results.append({"name": os.path.relpath(fp, folder),
                                    "size_kb": round(s.st_size / 1024, 2),
                                    "mtime": datetime.fromtimestamp(s.st_mtime).strftime("%Y-%m-%d %H:%M:%S"),
                                    "path": fp})
                except Exception:
                    continue
    else:
        for item in os.listdir(folder):
            fp = os.path.join(folder, item)
            if os.path.isfile(fp) and not item.startswith("."):
                try:
                    s = os.stat(fp)
                    results.append({"name": item, "size_kb": round(s.st_size / 1024, 2),
                                    "mtime": datetime.fromtimestamp(s.st_mtime).strftime("%Y-%m-%d %H:%M:%S"),
                                    "path": fp})
                except Exception:
                    continue
    return results


def _export_txt(app, recursive):
    folder = app.path_display.get().strip()
    if not folder or not os.path.isdir(folder):
        return messagebox.showwarning("提示", "请先选择有效的文件夹")
    save_path = os.path.join(folder, "文件目录清单.txt")

    def do():
        info = _get_files_info(folder, recursive)
        lines = ["=== 文件目录核对清单 ===\n\n"]
        lines.append(f"{'文件名':<40s}\t{'大小(KB)':<10s}\t{'修改时间'}\n")
        lines.append("=" * 70 + "\n")
        for fi in info:
            lines.append(f"{fi['name']:<40s}\t{fi['size_kb']:<10.2f}\t{fi['mtime']}\n")
        with open(save_path, "w", encoding="utf-8") as f:
            f.writelines(lines)
        return len(info)

    def done(cnt):
        app.clear_processing()
        app.log(f"📄 导出 TXT 目录清单: 共 {cnt} 个文件")
        messagebox.showinfo("✅ 导出成功",
                            f"目录清单已保存至：\n{save_path}\n\n共 {cnt} 个文件")
    app.set_processing("⏳ 正在导出 TXT...")
    run_in_background(do, done)


def _export_xlsx(app, recursive):
    folder = app.path_display.get().strip()
    if not folder or not os.path.isdir(folder):
        return messagebox.showwarning("提示", "请先选择有效的文件夹")
    if not _PANDAS_OK:
        messagebox.showerror("❌ 缺少依赖",
                             "Excel 导出需要安装 pandas 和 openpyxl：\n\n"
                             "pip install pandas openpyxl")
        return
    save_path = filedialog.asksaveasfilename(
        title="保存目录清单", defaultextension=".xlsx",
        filetypes=[("Excel 文件", "*.xlsx")], initialfile="目录清单.xlsx")
    if not save_path:
        return

    def do():
        info = _get_files_info(folder, recursive)
        pd.DataFrame(info).to_excel(save_path, index=False)
        return len(info)

    def done(cnt):
        app.clear_processing()
        app.log(f"📊 导出 Excel 目录清单: 共 {cnt} 个文件")
        messagebox.showinfo("✅ 导出成功",
                            f"目录清单已保存至：\n{save_path}\n\n共 {cnt} 个文件")

    def on_error(msg):
        app.clear_processing()
        messagebox.showerror("❌ 导出失败", str(msg))

    app.set_processing("⏳ 正在导出 Excel...")
    run_in_background(do, done, on_error=on_error)
