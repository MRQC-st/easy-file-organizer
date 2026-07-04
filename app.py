"""主应用窗口 —— CustomTkinter 现代外观"""

import os
import json
import shutil
import tkinter as tk
import customtkinter as ctk
from tkinter import messagebox, filedialog
from datetime import datetime
from PIL import Image, ImageTk

CONFIG_PATH = os.path.join(os.path.expanduser("~"), "batch_tool_config.json")
ICON_DIR = os.path.join(os.path.dirname(__file__), "icons")

ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")


class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("轻松文件整理助手")
        self.geometry("1280x780")
        self.minsize(1000, 650)

        # 撤销历史栈
        self.undo_history = []
        self.config = self._load_config()
        self._path_entries = []
        self.current_module = tk.StringVar(value="rename")

        # 主题色
        self.COLORS = {
            "primary":     "#3B82F6",
            "primary_hover": "#2563EB",
            "success":     "#22C55E",
            "success_hover": "#16A34A",
            "danger":      "#EF4444",
            "danger_hover": "#DC2626",
            "warning":     "#F59E0B",
            "warning_hover": "#D97706",
            "bg_main":     "#F0F4F8",
            "bg_card":     "#FFFFFF",
            "text_primary": "#1E293B",
            "text_secondary": "#64748B",
            "text_hint":   "#94A3B8",
            "border":      "#E2E8F0",
        }

        self._load_icons()
        self._build_ui()
        self._build_tabs()

        self.protocol("WM_DELETE_WINDOW", self.on_closing)

    # ── 图标加载 ──

    def _load_icons(self):
        """加载 PNG 图标 — 同时保存 CTkImage（标签/按钮）和 PhotoImage（Canvas/行内）"""
        self.icons = {}          # CTkImage 给 CTkLabel
        self.icons_photo = {}    # PhotoImage 给 tk.Canvas / tk.Label
        self.icons_small_photo = {}

        icon_map = {
            "robot":        ("robot_mascot_small.png", 120, 120),
            "robot_large":  ("robot_mascot.png", 200, 200),
            "file_image":   ("file_image.png", 48, 48),
            "file_video":   ("file_video.png", 48, 48),
            "file_audio":   ("file_audio.png", 48, 48),
            "file_document":("file_document.png", 48, 48),
            "file_spreadsheet":("file_spreadsheet.png", 48, 48),
            "file_code":    ("file_code.png", 48, 48),
            "file_archive": ("file_archive.png", 48, 48),
            "file_folder":  ("file_folder.png", 48, 48),
            "mod_rename":   ("mod_rename.png", 48, 48),
            "mod_classify": ("mod_classify.png", 48, 48),
            "mod_cleanup":  ("mod_cleanup.png", 48, 48),
            "mod_export":   ("mod_export.png", 48, 48),
            "mod_file_ops": ("mod_file_ops.png", 48, 48),
            "action_undo":  ("action_undo.png", 24, 24),
            "action_browse":("action_browse.png", 24, 24),
            "action_apply": ("action_apply.png", 24, 24),
            "action_preview":("action_preview.png", 24, 24),
            "mini_robot":   ("mini_robot.png", 64, 64),
        }

        for key, (filename, w, h) in icon_map.items():
            path = os.path.join(ICON_DIR, filename)
            if os.path.exists(path):
                try:
                    pil_img = Image.open(path)
                    # CTkImage
                    self.icons[key] = ctk.CTkImage(
                        light_image=pil_img, dark_image=pil_img,
                        size=(w, h)
                    )
                    # PhotoImage
                    self.icons_photo[key] = ImageTk.PhotoImage(
                        pil_img.resize((w, h), Image.LANCZOS)
                    )
                except Exception:
                    self.icons[key] = None
                    self.icons_photo[key] = None
            else:
                self.icons[key] = None
                self.icons_photo[key] = None

        # 小图标（文件列表 24x24）
        small_keys = [
            "file_image", "file_video", "file_audio",
            "file_document", "file_spreadsheet",
            "file_code", "file_archive", "file_folder",
        ]
        for key in small_keys:
            path = os.path.join(ICON_DIR, f"{key}.png")
            if os.path.exists(path):
                try:
                    pil_img = Image.open(path).resize((24, 24), Image.LANCZOS)
                    self.icons_small_photo[key] = ImageTk.PhotoImage(pil_img)
                except Exception:
                    self.icons_small_photo[key] = None
            else:
                self.icons_small_photo[key] = None

        # 扩展名→图标键映射
        self.ext_icon_map = {".jpg": "file_image", ".jpeg": "file_image",
            ".png": "file_image", ".gif": "file_image", ".bmp": "file_image",
            ".webp": "file_image",
            ".mp4": "file_video", ".avi": "file_video", ".mov": "file_video",
            ".mkv": "file_video", ".wmv": "file_video", ".flv": "file_video",
            ".mp3": "file_audio", ".wav": "file_audio", ".flac": "file_audio",
            ".aac": "file_audio", ".ogg": "file_audio",
            ".doc": "file_document", ".docx": "file_document", ".txt": "file_document",
            ".pdf": "file_document", ".md": "file_document", ".rtf": "file_document",
            ".xls": "file_spreadsheet", ".xlsx": "file_spreadsheet", ".csv": "file_spreadsheet",
            ".py": "file_code", ".js": "file_code", ".html": "file_code",
            ".css": "file_code", ".java": "file_code", ".cpp": "file_code",
            ".zip": "file_archive", ".rar": "file_archive", ".7z": "file_archive",
            ".tar": "file_archive", ".gz": "file_archive"}

    def get_file_icon_photo(self, filename):
        """返回 24x24 PhotoImage 用于文件列表行"""
        ext = os.path.splitext(filename)[1].lower()
        key = self.ext_icon_map.get(ext, "file_document")
        return self.icons_small_photo.get(key)

    def get_icon_ctk(self, key):
        """返回 CTkImage 用于 CTkLabel"""
        return self.icons.get(key)

    # ── 主 UI ──

    def _build_ui(self):
        self.configure(fg_color=self.COLORS["bg_main"])

        # 顶部标题栏
        top_bar = ctk.CTkFrame(self, fg_color="white", height=52, corner_radius=0)
        top_bar.pack(fill=tk.X)
        top_bar.pack_propagate(False)

        ctk.CTkLabel(top_bar, text="📂  轻松文件整理助手",
                     font=("Microsoft YaHei", 17, "bold"),
                     text_color=self.COLORS["primary"]
                     ).pack(side=tk.LEFT, padx=24)

        # 主内容区
        main = ctk.CTkFrame(self, fg_color=self.COLORS["bg_main"], corner_radius=0)
        main.pack(fill=tk.BOTH, expand=True)

        # 左侧预览区
        self.left_frame = ctk.CTkFrame(main, fg_color="white", corner_radius=8)
        self.left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True,
                             padx=10, pady=10)

        # 右侧操作面板
        self.right_frame = ctk.CTkFrame(main, fg_color="white", corner_radius=8)
        self.right_frame.pack(side=tk.RIGHT, fill=tk.BOTH,
                              padx=(0, 10), pady=10)
        self.right_frame.configure(width=480)
        self.right_frame.pack_propagate(False)

        # 底部日志
        self._build_log()

    def _build_log(self):
        log_frame = ctk.CTkFrame(self, fg_color="white", corner_radius=8)
        log_frame.pack(fill=tk.X, padx=10, pady=(0, 10))

        header = ctk.CTkFrame(log_frame, fg_color="transparent", height=32)
        header.pack(fill=tk.X)
        header.pack_propagate(False)
        ctk.CTkLabel(header, text="📋 操作日志",
                     font=("Microsoft YaHei", 11, "bold"),
                     text_color=self.COLORS["text_primary"]
                     ).pack(side=tk.LEFT, padx=14)

        self.log_text = ctk.CTkTextbox(log_frame, height=80,
                                       font=("Consolas", 10),
                                       fg_color="#F8FAFC",
                                       text_color=self.COLORS["text_secondary"],
                                       corner_radius=6)
        self.log_text.pack(fill=tk.X, padx=10, pady=(0, 10))

    def _build_tabs(self):
        from tabs_rename import build_tab as build_rename
        from tabs_classify import build_tab as build_classify
        from tabs_cleanup import build_tab as build_cleanup
        from tabs_export import build_tab as build_export
        from tabs_file_ops import build_tab as build_file_ops

        self._build_preview_area()
        self._build_action_panel()

        self._module_builders = {
            "rename":  build_rename,
            "classify": build_classify,
            "cleanup": build_cleanup,
            "export":  build_export,
            "file_ops": build_file_ops,
        }
        self._switch_module("rename")

    # ═══════════════════════════════════════
    # 左侧预览区
    # ═══════════════════════════════════════

    def _build_preview_area(self):
        f = self.left_frame

        # ── 标题行 ──
        header = ctk.CTkFrame(f, fg_color="transparent")
        header.pack(fill=tk.X, padx=16, pady=(14, 6))

        ctk.CTkLabel(header, text="📂 预览区",
                     font=("Microsoft YaHei", 16, "bold"),
                     text_color=self.COLORS["text_primary"]
                     ).pack(side=tk.LEFT)

        self.undo_btn = ctk.CTkButton(header, text="↩ 撤销",
                                       font=("Microsoft YaHei", 11),
                                       fg_color=self.COLORS["warning"],
                                       hover_color=self.COLORS["warning_hover"],
                                       corner_radius=6, width=80, height=30,
                                       command=self.undo)
        self.undo_btn.pack(side=tk.RIGHT)

        # ── 文件夹选择 ──
        path_frame = ctk.CTkFrame(f, fg_color="transparent")
        path_frame.pack(fill=tk.X, padx=16, pady=(4, 8))

        ctk.CTkLabel(path_frame, text="目标文件夹：",
                     font=("Microsoft YaHei", 11),
                     text_color=self.COLORS["text_primary"]
                     ).pack(side=tk.LEFT)

        self.path_display = ctk.CTkEntry(path_frame,
                                          placeholder_text="请选择文件夹...",
                                          font=("Microsoft YaHei", 10),
                                          corner_radius=6,
                                          state="readonly")
        self.path_display.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=6)

        ctk.CTkButton(path_frame, text="浏览文件夹",
                      font=("Microsoft YaHei", 10),
                      fg_color=self.COLORS["primary"],
                      hover_color=self.COLORS["primary_hover"],
                      corner_radius=6, width=110, height=32,
                      command=self.browse_folder
                      ).pack(side=tk.LEFT)

        # ── 拖拽区 ──
        self._build_drop_zone(f)

        # ── 文件类型图标 ──
        self._build_file_type_bar(f)

        # ── 文件列表 ──
        self._build_file_list(f)

    def _build_drop_zone(self, parent):
        drop_outer = ctk.CTkFrame(parent, fg_color="transparent")
        drop_outer.pack(fill=tk.X, padx=16, pady=(0, 8))

        self.drop_canvas = tk.Canvas(drop_outer, height=130,
                                     bg="#F0F6FF", highlightthickness=0,
                                     cursor="hand2")
        self.drop_canvas.pack(fill=tk.X)
        self.drop_canvas.bind("<Configure>", lambda e: self._draw_drop_area())

    def _draw_drop_area(self):
        self.drop_canvas.delete("all")
        w = self.drop_canvas.winfo_width() - 4
        h = self.drop_canvas.winfo_height() - 4
        if w < 20 or h < 20:
            return

        self.drop_canvas.create_rectangle(
            2, 2, w + 2, h + 2,
            outline=self.COLORS["primary"], dash=(6, 4),
            width=2, fill="#F0F6FF")

        cx, cy = w // 2 + 2, h // 2 + 2

        robot = self.icons_photo.get("robot")
        if robot:
            self.drop_canvas.create_image(cx - 100, cy, image=robot, tags="drop")

        self.drop_canvas.create_text(
            cx + 20, cy - 15,
            text="拖拽文件或文件夹到此处",
            font=("Microsoft YaHei", 13),
            fill="#1E293B", tags="drop", anchor=tk.W)

        self.drop_canvas.create_text(
            cx + 20, cy + 15,
            text="或 点击浏览文件",
            font=("Microsoft YaHei", 10),
            fill=self.COLORS["primary"], tags="drop", anchor=tk.W)

        def on_click(e):
            self.browse_folder()
        self.drop_canvas.tag_bind("drop", "<Button-1>", on_click)

    def _build_file_type_bar(self, parent):
        bar_outer = ctk.CTkFrame(parent, fg_color="#F8FAFC", corner_radius=6)
        bar_outer.pack(fill=tk.X, padx=0, pady=(0, 6))

        types = [
            ("file_image", "图片", "#EF4444"),
            ("file_video", "视频", "#3B82F6"),
            ("file_audio", "音频", "#F59E0B"),
            ("file_document", "文档", "#06B6D4"),
            ("file_spreadsheet", "表格", "#22C55E"),
        ]

        inner = ctk.CTkFrame(bar_outer, fg_color="transparent")
        inner.pack(padx=16, pady=6)

        for icon_key, label_text, color in types:
            item = ctk.CTkFrame(inner, fg_color="transparent")
            item.pack(side=tk.LEFT, padx=6)

            icon_ctk = self.icons.get(icon_key)
            if icon_ctk:
                ctk.CTkLabel(item, image=icon_ctk, text="",
                             fg_color="transparent"
                             ).pack(side=tk.LEFT)

            ctk.CTkLabel(item, text=label_text,
                         font=("Microsoft YaHei", 10),
                         text_color=color,
                         fg_color="transparent"
                         ).pack(side=tk.LEFT, padx=3)

    def _build_file_list(self, parent):
        list_outer = ctk.CTkFrame(parent, fg_color="transparent")
        list_outer.pack(fill=tk.BOTH, expand=True, padx=16, pady=(0, 12))

        # 表头
        hdr = ctk.CTkFrame(list_outer, fg_color="#F1F5F9", corner_radius=4)
        hdr.pack(fill=tk.X)

        cols = [("", 30), ("类型", 36), ("文件名称", 200),
                ("", 20), ("新名称 ✨", 220), ("状态", 60)]
        for text, width in cols:
            ctk.CTkLabel(hdr, text=text,
                         font=("Microsoft YaHei", 9, "bold"),
                         text_color=self.COLORS["text_primary"],
                         width=max(1, width // 6)
                         ).pack(side=tk.LEFT, padx=4, pady=4)

        # 滚动容器
        container = ctk.CTkFrame(list_outer, fg_color="transparent")
        container.pack(fill=tk.BOTH, expand=True)

        self.file_canvas = tk.Canvas(container, bg="white",
                                     highlightthickness=0, bd=0)
        self.file_scrollbar = ctk.CTkScrollbar(container, orientation="vertical",
                                                command=self.file_canvas.yview)
        self.file_inner = tk.Frame(self.file_canvas, bg="white")

        self.file_inner.bind("<Configure>",
                             lambda e: self.file_canvas.configure(
                                 scrollregion=self.file_canvas.bbox("all")))
        self.file_canvas.create_window((0, 0), window=self.file_inner, anchor=tk.NW)
        self.file_canvas.config(yscrollcommand=self.file_scrollbar.set)

        self.file_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.file_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # 状态栏
        status_frame = ctk.CTkFrame(parent, fg_color="transparent")
        status_frame.pack(fill=tk.X, padx=16, pady=(0, 12))

        self.status_label = ctk.CTkLabel(status_frame,
                                          text="💡 请选择文件夹开始浏览文件",
                                          font=("Microsoft YaHei", 11),
                                          text_color=self.COLORS["text_secondary"])
        self.status_label.pack(side=tk.LEFT)

        self.file_vars = {}
        self.file_items = []

    # ═══════════════════════════════════════
    # 右侧操作面板
    # ═══════════════════════════════════════

    def _build_action_panel(self):
        panel = self.right_frame

        ctk.CTkLabel(panel, text="🛠 操作面板",
                     font=("Microsoft YaHei", 16, "bold"),
                     text_color=self.COLORS["text_primary"]
                     ).pack(anchor=tk.W, padx=20, pady=(16, 0))

        cards_data = [
            ("mod_rename",   "批量改名", "rename"),
            ("mod_classify", "整理分类", "classify"),
            ("mod_cleanup",  "清理去重", "cleanup"),
            ("mod_export",   "数据导出", "export"),
            ("mod_file_ops", "文件操作", "file_ops"),
        ]

        cards_outer = ctk.CTkFrame(panel, fg_color="transparent")
        cards_outer.pack(fill=tk.X, padx=16, pady=(12, 16))

        self.card_buttons = {}

        row1 = ctk.CTkFrame(cards_outer, fg_color="transparent")
        row1.pack(fill=tk.X, pady=(0, 6))
        for i in range(3):
            self._create_card(row1, cards_data[i][0], cards_data[i][1],
                              cards_data[i][2])

        row2 = ctk.CTkFrame(cards_outer, fg_color="transparent")
        row2.pack(fill=tk.X)
        for i in range(3, 5):
            self._create_card(row2, cards_data[i][0], cards_data[i][1],
                              cards_data[i][2])
        ctk.CTkFrame(row2, fg_color="transparent"
                     ).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=4)

        # 分隔线 + 规则标题
        sep = ctk.CTkFrame(panel, fg_color=self.COLORS["border"],
                           height=1, corner_radius=0)
        sep.pack(fill=tk.X, padx=20, pady=0)

        rule_header = ctk.CTkFrame(panel, fg_color="transparent")
        rule_header.pack(fill=tk.X, padx=20, pady=(10, 6))

        self.rule_title = ctk.CTkLabel(rule_header, text="批量改名规则",
                                       font=("Microsoft YaHei", 13, "bold"),
                                       text_color=self.COLORS["text_primary"])
        self.rule_title.pack(side=tk.LEFT)

        # CTkScrollableFrame = 自带滚动的框架！
        self.rule_frame = ctk.CTkScrollableFrame(panel, fg_color="transparent",
                                                  corner_radius=0)
        self.rule_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 16))

    def _create_card(self, parent, icon_key, text, module):
        card = ctk.CTkFrame(parent, fg_color="white", corner_radius=8,
                            border_width=2, border_color=self.COLORS["border"],
                            cursor="hand2")
        card.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=4, pady=4)

        icon_ctk = self.icons.get(icon_key)
        if icon_ctk:
            ctk.CTkLabel(card, image=icon_ctk, text="",
                         fg_color="transparent"
                         ).pack(pady=(10, 4))
        else:
            ctk.CTkLabel(card, text="📁",
                         font=("Microsoft YaHei", 22),
                         fg_color="transparent"
                         ).pack(pady=(10, 4))

        lbl = ctk.CTkLabel(card, text=text, font=("Microsoft YaHei", 10),
                           text_color=self.COLORS["text_primary"],
                           fg_color="transparent")
        lbl.pack(pady=(0, 10))

        def on_click(e=None, m=module):
            self._on_module_click(m)
        for w in (card, lbl):
            w.bind("<Button-1>", on_click)

        self.card_buttons[module] = (card, lbl)

        if module == "rename":
            self._highlight_card("rename")

    def _on_module_click(self, module):
        self.current_module.set(module)
        self._highlight_card(module)
        self._switch_module(module)

    def _switch_module(self, module):
        for w in self.rule_frame.winfo_children():
            w.destroy()
        if module in self._module_builders:
            self._module_builders[module](self)

        titles = {
            "rename":  "批量改名规则",
            "classify": "整理分类规则",
            "cleanup": "清理去重选项",
            "export":  "数据导出设置",
            "file_ops": "文件操作选项",
        }
        self.rule_title.configure(text=titles.get(module, "操作选项"))

    def _highlight_card(self, module):
        for m, (card, lbl) in self.card_buttons.items():
            if m == module:
                card.configure(border_color=self.COLORS["primary"],
                               fg_color="#EFF6FF")
                lbl.configure(text_color=self.COLORS["primary"])
            else:
                card.configure(border_color=self.COLORS["border"],
                               fg_color="white")
                lbl.configure(text_color=self.COLORS["text_primary"])

    # ── 文件浏览 ──

    def browse_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.path_display.configure(state="normal")
            self.path_display.delete(0, "end")
            self.path_display.insert(0, folder)
            self.path_display.configure(state="readonly")
            self.load_folder(folder)

    def load_folder(self, folder):
        if not os.path.isdir(folder):
            return
        self.clear_file_list()
        try:
            for name in sorted(os.listdir(folder)):
                full_path = os.path.join(folder, name)
                if os.path.isfile(full_path) and not name.startswith("."):
                    self.add_file_to_list(name, full_path)
            self.log(f"✅ 已加载文件夹: {folder}，共 {len(self.file_items)} 个文件")
        except Exception as e:
            self.log(f"❌ 加载文件夹失败: {str(e)}")

    def add_file_to_list(self, filename, filepath):
        row = tk.Frame(self.file_inner, bg="white")
        row.pack(fill=tk.X, pady=1)

        var = tk.BooleanVar(value=True)
        cb = tk.Checkbutton(row, variable=var, bg="white",
                            activebackground="white", bd=0)
        cb.pack(side=tk.LEFT, padx=4)
        self.file_vars[filename] = var

        icon_photo = self.get_file_icon_photo(filename)
        if icon_photo:
            img = tk.Label(row, image=icon_photo, bg="white")
            img.image = icon_photo
            img.pack(side=tk.LEFT, padx=2)
        else:
            tk.Label(row, text="📄", font=("Microsoft YaHei", 12),
                     bg="white").pack(side=tk.LEFT, padx=2)

        tk.Label(row, text=filename, font=("Microsoft YaHei", 10),
                 bg="white", fg=self.COLORS["text_primary"],
                 anchor=tk.W, width=28).pack(side=tk.LEFT, padx=6)

        tk.Label(row, text="→", font=("Microsoft YaHei", 12),
                 bg="white", fg=self.COLORS["text_hint"]
                 ).pack(side=tk.LEFT, padx=4)

        new_lbl = tk.Label(row, text=filename, font=("Microsoft YaHei", 10),
                           bg="white", fg=self.COLORS["primary"],
                           anchor=tk.W, width=30)
        new_lbl.pack(side=tk.LEFT, padx=6)

        st_lbl = tk.Label(row, text="待处理", font=("Microsoft YaHei", 8),
                          bg="white", fg=self.COLORS["text_hint"])
        st_lbl.pack(side=tk.LEFT, padx=2)

        self.file_items.append({
            "name": filename,
            "path": filepath,
            "var": var,
            "label": new_lbl,
            "status": st_lbl,
        })
        self._update_status()

    def clear_file_list(self):
        for w in self.file_inner.winfo_children():
            w.destroy()
        self.file_vars.clear()
        self.file_items.clear()
        self._update_status()

    def refresh_file_list(self, new_names=None):
        for item in self.file_items:
            if new_names and item["name"] in new_names:
                item["label"].config(text=new_names[item["name"]],
                                     fg=self.COLORS["success"])
                item["status"].config(text="✅ 重命名", fg=self.COLORS["success"])
            else:
                item["label"].config(text=item["name"], fg=self.COLORS["primary"])
                item["status"].config(text="待处理", fg=self.COLORS["text_hint"])
        self._update_status()

    def _update_status(self):
        count = sum(1 for f in self.file_items if f["var"].get())
        total = len(self.file_items)
        if total == 0:
            self.status_label.configure(text="💡 请选择文件夹开始浏览文件")
        else:
            self.status_label.configure(text=f"📁 已选择 {count}/{total} 个文件")

    # ── 路径同步 ──

    def register_path_entry(self, entry):
        if entry not in self._path_entries:
            self._path_entries.append(entry)

    def sync_paths(self, source_entry, path):
        for entry in self._path_entries:
            if entry is not source_entry:
                entry.delete(0, "end")
                entry.insert(0, path)

    # ── 日志 ──

    def log(self, msg):
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_text.insert("end", f"[{timestamp}] {msg}\n")
        self.log_text.see("end")

    # ── 撤销 ──

    def push_undo(self, op_type, desc, pairs):
        self.undo_history.append({"type": op_type, "desc": desc, "pairs": pairs})
        self.log(f"📝 操作已记录，可撤销: {desc}")

    def undo(self, op_type=None):
        if not self.undo_history:
            messagebox.showinfo("提示", "没有可撤销的操作")
            return 0
        idx = -1
        for i in range(len(self.undo_history) - 1, -1, -1):
            if op_type is None or self.undo_history[i]["type"] == op_type:
                idx = i
                break
        if idx == -1:
            messagebox.showinfo("提示", f"没有可撤销的「{op_type}」操作")
            return 0
        entry = self.undo_history.pop(idx)
        count = 0
        for old, new in entry["pairs"]:
            try:
                if entry["type"] == "create_folder":
                    if os.path.exists(new):
                        shutil.rmtree(new)
                        count += 1
                elif entry["type"] == "delete":
                    pass
                else:
                    if os.path.exists(new):
                        os.rename(new, old)
                        count += 1
            except Exception as e:
                self.log(f"❌ 撤销失败: {os.path.basename(new)} - {str(e)}")
        self.log(f"↩ 撤销操作: {entry['desc']}，已恢复 {count} 项")
        return count

    # ── 配置 ──

    def _load_config(self):
        default = {"rename_prefixes": [], "rename_suffixes": []}
        if os.path.exists(CONFIG_PATH):
            try:
                with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass
        return default

    def save_config(self, updates=None):
        if updates:
            self.config.update(updates)
        try:
            with open(CONFIG_PATH, "w", encoding="utf-8") as f:
                json.dump(self.config, f, ensure_ascii=False, indent=2)
        except Exception as e:
            self.log(f"❌ 保存配置失败: {str(e)}")

    def on_closing(self):
        self.save_config()
        self.destroy()
