"""生成所有参考图所需的图标资源"""

import os
import math
from PIL import Image, ImageDraw, ImageFont

ICONS_DIR = os.path.join(os.path.dirname(__file__), "icons")
os.makedirs(ICONS_DIR, exist_ok=True)


def _load_font(size=16):
    """尝试加载字体"""
    # FontAwesome 或系统符号字体
    attempts = [
        "/usr/share/fonts/truetype/font-awesome/fontawesome-webfont.ttf",
        "/usr/share/fonts/opentype/font-awesome/fontawesome-regular.ttf",
    ]
    for p in attempts:
        if os.path.exists(p):
            try:
                return ImageFont.truetype(p, size)
            except Exception:
                pass
    try:
        return ImageFont.truetype("DejaVuSans.ttf", size)
    except Exception:
        return ImageFont.load_default()


def draw_rounded_rect(draw, xy, radius, fill=None, outline=None, width=1):
    """绘制圆角矩形"""
    x1, y1, x2, y2 = xy
    draw.rounded_rectangle(xy, radius=radius, fill=fill, outline=outline, width=width)


def draw_circle(draw, cx, cy, r, fill=None, outline=None, width=1):
    """绘制圆形"""
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=fill, outline=outline, width=width)


# ═══════════════════════════════════════════
# 1. 机器人角色插画 (220x220)
# ═══════════════════════════════════════════

def generate_robot():
    """生成可爱的机器人角色插图"""
    size = 220
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    cx, cy = size // 2, size // 2

    # 颜色方案
    body_color = (74, 144, 226)       # 蓝色
    body_light = (100, 170, 240)      # 浅蓝
    accent = (38, 166, 154)           # 蓝绿色
    white = (255, 255, 255)
    dark = (60, 60, 80)
    eye_white = (255, 255, 255)
    eye_pupil = (60, 60, 80)
    gold = (255, 193, 7)

    # ── 身体 (圆角矩形) ──
    body_x1, body_y1 = cx - 60, cy - 30
    body_x2, body_y2 = cx + 60, cy + 50
    draw_rounded_rect(draw, (body_x1, body_y1, body_x2, body_y2),
                      radius=25, fill=body_color)

    # ── 身体高光 ──
    draw_rounded_rect(draw, (body_x1 + 8, body_y1 + 8, body_x2 - 40, body_y1 + 25),
                      radius=10, fill=body_light, width=0)

    # ── 胸部屏幕/仪表盘 ──
    screen_x1, screen_y1 = cx - 25, cy
    screen_x2, screen_y2 = cx + 25, cy + 25
    draw_rounded_rect(draw, (screen_x1, screen_y1, screen_x2, screen_y2),
                      radius=6, fill=(44, 62, 80), width=0)
    # 屏幕上的"笑脸"指示
    draw.arc([screen_x1 + 6, screen_y1 + 6, screen_x2 - 6, screen_y2 - 4],
             0, 180, fill=(0, 230, 118), width=2)

    # ── 头部（大圆形） ──
    head_cy = cy - 55
    draw_circle(draw, cx, head_cy, 45, fill=body_color)

    # ── 头部的发光面罩 ──
    mask_r = 28
    draw_circle(draw, cx, head_cy, mask_r, fill=(30, 136, 229))

    # ── 眼睛 ──
    eye_spacing = 15
    eye_r = 8
    draw_circle(draw, cx - eye_spacing, head_cy, eye_r, fill=eye_white)
    draw_circle(draw, cx + eye_spacing, head_cy, eye_r, fill=eye_white)
    # 瞳孔
    draw_circle(draw, cx - eye_spacing + 2, head_cy - 1, 4, fill=eye_pupil)
    draw_circle(draw, cx + eye_spacing + 2, head_cy - 1, 4, fill=eye_pupil)

    # ── 眼睛高光 ──
    draw_circle(draw, cx - eye_spacing - 2, head_cy - 3, 2, fill=white)
    draw_circle(draw, cx + eye_spacing - 2, head_cy - 3, 2, fill=white)

    # ── 嘴巴 ──
    draw.arc([cx - 10, head_cy + 5, cx + 10, head_cy + 18],
             0, 180, fill=white, width=2)

    # ── 头顶天线 ──
    antenna_top = head_cy - 55
    draw.line([(cx, head_cy - 45), (cx, antenna_top)], fill=accent, width=3)
    # 天线小球
    draw_circle(draw, cx, antenna_top, 6, fill=gold)
    # 天线星星光晕
    for angle in range(0, 360, 45):
        rad = math.radians(angle)
        sx = cx + 12 * math.cos(rad)
        sy = antenna_top + 12 * math.sin(rad)
        draw_circle(draw, sx, sy, 2, fill=(255, 235, 59, 180))

    # ── 手臂 ──
    # 左手（举起来挥手）
    arm_color = (90, 160, 230)
    # 左臂
    draw.rounded_rectangle(
        [body_x1 - 22, cy - 10, body_x1 - 10, cy + 20],
        radius=8, fill=arm_color, width=0
    )
    # 左手掌
    draw_circle(draw, body_x1 - 16, cy - 15, 10, fill=accent)

    # 右臂（拿魔杖）
    draw.rounded_rectangle(
        [body_x2 + 10, cy + 5, body_x2 + 22, cy + 35],
        radius=8, fill=arm_color, width=0
    )
    # 右手掌
    draw_circle(draw, body_x2 + 16, cy, 10, fill=accent)

    # ── 魔杖 ──
    wand_x = body_x2 + 16
    wand_y = cy - 15
    # 魔杖杆
    draw.line([(wand_x + 8, wand_y + 40), (wand_x - 8, wand_y - 5)], fill=gold, width=4)
    # 魔杖头部星星
    star_points = 5
    star_r1 = 14
    star_r2 = 6
    star_cx, star_cy = wand_x - 8, wand_y - 8
    star_coords = []
    for i in range(star_points * 2):
        angle = -math.pi / 2 + i * math.pi / star_points
        r = star_r1 if i % 2 == 0 else star_r2
        star_coords.append((star_cx + r * math.cos(angle), star_cy + r * math.sin(angle)))
    draw.polygon(star_coords, fill=gold)

    # ── 魔杖星光 ──
    sparkle_colors = [(255, 235, 59), (255, 255, 255, 200), (100, 255, 218, 150)]
    for i, sc in enumerate(sparkle_colors):
        sa = (i + 1) * 30
        draw_circle(draw,
                    star_cx + 20 + 15 * math.cos(math.radians(sa)),
                    star_cy - 15 + 15 * math.sin(math.radians(sa)),
                    4 - i, fill=sc)

    # ── 腿部 ──
    leg_w = 14
    leg_h = 22
    draw_rounded_rect(draw, (cx - 25, body_y2 + 2, cx - 10, body_y2 + leg_h),
                      radius=7, fill=body_color)
    draw_rounded_rect(draw, (cx + 10, body_y2 + 2, cx + 25, body_y2 + leg_h),
                      radius=7, fill=body_color)
    # 脚
    draw_rounded_rect(draw, (cx - 30, body_y2 + leg_h - 4, cx - 5, body_y2 + leg_h + 6),
                      radius=5, fill=accent)
    draw_rounded_rect(draw, (cx + 5, body_y2 + leg_h - 4, cx + 30, body_y2 + leg_h + 6),
                      radius=5, fill=accent)

    img.save(os.path.join(ICONS_DIR, "robot.png"))
    print("✓ icons/robot.png")


# ═══════════════════════════════════════════
# 2. 文件类型图标 (48x48)
# ═══════════════════════════════════════════

def generate_file_icons():
    """生成文件类型图标（圆形背景 + 符号）"""
    size = 48
    icons = {
        "image": {"bg": "#FF6B6B", "symbol": "🖼"},     # 红
        "video": {"bg": "#4ECDC4", "symbol": "▶"},      # 青
        "audio": {"bg": "#FF9800", "symbol": "♪"},      # 橙
        "document": {"bg": "#45B7D1", "symbol": "📄"},   # 蓝
        "spreadsheet": {"bg": "#96CEB4", "symbol": "📊"},# 绿
        "code": {"bg": "#7C4DFF", "symbol": "</>"},      # 紫
        "archive": {"bg": "#FF8A65", "symbol": "📦"},    # 橙红
        "folder": {"bg": "#FFC107", "symbol": "📁"},     # 黄
    }

    for name, data in icons.items():
        img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)

        # 解析颜色
        if data["bg"].startswith("#"):
            r, g, b = int(data["bg"][1:3], 16), int(data["bg"][3:5], 16), int(data["bg"][5:7], 16)
        else:
            r, g, b = 100, 100, 100

        # 圆角背景
        draw_rounded_rect(draw, (4, 4, size - 4, size - 4), radius=10,
                          fill=(r, g, b, 230))

        # 高光
        draw_rounded_rect(draw, (8, 8, size - 16, int(size * 0.45)),
                          radius=6, fill=(r + 40, g + 40, b + 40, 120))

        # 用文字绘制符号（大号字体）
        try:
            font_size = 22
            font = ImageFont.truetype("/usr/share/fonts/truetype/freefont/FreeSerif.ttf", font_size)
        except Exception:
            font = ImageFont.load_default()

        # 写在底部（字号不够大就用简单的几何图形）
        if name == "image":
            # 画一个太阳/山脉代表图片
            draw_circle(draw, size // 2, 22, 8, fill=(255, 255, 255, 220))
            # 山脉
            draw.polygon([(10, 38), (20, 22), (28, 34), (38, 18), (44, 38)],
                         fill=(255, 255, 255, 180))
        elif name == "video":
            # 播放三角形
            draw.polygon([(18, 14), (18, 34), (36, 24)], fill=(255, 255, 255, 230))
        elif name == "audio":
            # 音符
            draw_circle(draw, 18, 34, 5, fill=(255, 255, 255, 220))
            draw.line([(22, 34), (22, 14)], fill=(255, 255, 255, 220), width=2)
            draw_circle(draw, 32, 30, 5, fill=(255, 255, 255, 220))
            draw.line([(22, 14), (34, 10)], fill=(255, 255, 255, 180), width=2)
        elif name == "document":
            # 文件折角
            doc_color = (255, 255, 255)
            draw_rounded_rect(draw, (12, 10, 38, 36), radius=3,
                              fill=doc_color, width=0)
            # 文字行
            for i, ly in enumerate([18, 23, 28]):
                draw.line([(16, ly), (34, ly)], fill=(r, g, b), width=1)
            # 折角
            draw.polygon([(34, 10), (34, 16), (38, 16)],
                         fill=(r + 40, g + 40, b + 40))
        elif name == "spreadsheet":
            # 表格
            draw_rounded_rect(draw, (10, 10, 38, 38), radius=4,
                              fill=(255, 255, 255, 230), width=0)
            # 网格
            draw.line([(10, 22), (38, 22)], fill=(r, g, b), width=1)
            draw.line([(10, 30), (38, 30)], fill=(r, g, b), width=1)
            draw.line([(26, 10), (26, 38)], fill=(r, g, b), width=1)
            # 表头着色
            draw_rounded_rect(draw, (10, 10, 38, 20), radius=3,
                              fill=(r, g, b, 100), width=0)
        elif name == "code":
            # 尖括号 </> 
            draw.line([(14, 18), (8, 24), (14, 30)], fill=(255, 255, 255, 230), width=3)
            draw.line([(34, 18), (40, 24), (34, 30)], fill=(255, 255, 255, 230), width=3)
            # 斜杠
            draw.line([(28, 14), (22, 34)], fill=(255, 255, 255, 200), width=2)
        elif name == "archive":
            # 箱子
            draw_rounded_rect(draw, (10, 18, 38, 36), radius=4,
                              fill=(255, 255, 255, 230), width=0)
            draw.arc([12, 12, 36, 24], 180, 0, fill=(255, 255, 255, 200), width=2)
            # 拉链
            draw.line([(18, 18), (18, 36)], fill=(r + 30, g + 20, b + 10, 180), width=2)
            draw.line([(30, 18), (30, 36)], fill=(r + 30, g + 20, b + 10, 180), width=2)
        elif name == "folder":
            # 文件夹
            draw_rounded_rect(draw, (10, 18, 40, 35), radius=3,
                              fill=(255, 255, 255, 230), width=0)
            draw_rounded_rect(draw, (10, 18, 22, 24), radius=2,
                              fill=(255, 255, 255, 150), width=0)
            draw.line([(10, 18), (20, 12), (35, 12), (40, 18)],
                      fill=(255, 255, 255, 200), width=2)

        img.save(os.path.join(ICONS_DIR, f"file_{name}.png"))
    print("✓ icons/file_*.png (8 个文件类型图标)")


# ═══════════════════════════════════════════
# 3. 功能模块图标 (64x64)
# ═══════════════════════════════════════════

def generate_module_icons():
    """生成功能模块图标（卡片大图标，圆底+符号）"""
    size = 64
    icons = {
        "rename": {"bg": (74, 144, 226), "symbol": "✏"},
        "classify": {"bg": (38, 166, 154), "symbol": "📁"},
        "cleanup": {"bg": (255, 152, 0), "symbol": "✦"},
        "export": {"bg": (102, 187, 106), "symbol": "📤"},
        "file_ops": {"bg": (149, 117, 205), "symbol": "⚙"},
    }

    for name, data in icons.items():
        img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        r, g, b = data["bg"]

        # 大圆形背景
        draw_circle(draw, size // 2, size // 2, 28,
                    fill=(r, g, b, 240))

        # 高光
        draw_circle(draw, size // 2 - 6, size // 2 - 8, 12,
                    fill=(r + 50, g + 50, b + 50, 100))

        # 画具体的图形符号
        if name == "rename":
            # 铅笔
            draw.polygon([(24, 38), (32, 22), (38, 26), (28, 42)],
                         fill=(255, 255, 255, 230))
            draw.line([(24, 38), (20, 42)], fill=(255, 255, 255, 200), width=2)
            # 星星
            for i in range(3):
                sa = (i * 30) + 15
                draw_circle(draw,
                            42 + 10 * math.cos(math.radians(sa)),
                            18 + 8 * math.sin(math.radians(sa)),
                            2.5, fill=(255, 235, 59))
        elif name == "classify":
            # 文件夹 + 箭头
            draw_rounded_rect(draw, (16, 24, 48, 42), radius=4,
                              fill=(255, 255, 255, 230), width=0)
            draw_rounded_rect(draw, (16, 24, 28, 30), radius=2,
                              fill=(255, 255, 255, 150), width=0)
            draw.line([(16, 24), (22, 19), (38, 19), (48, 24)],
                      fill=(255, 255, 255, 200), width=3)
            # 箭头
            draw.line([(40, 44), (46, 44), (46, 38)], fill=(255, 255, 255, 220), width=2)
            draw.line([(46, 44), (40, 38)], fill=(255, 255, 255, 220), width=2)
        elif name == "cleanup":
            # 魔法扫帚/星尘
            # 扫帚柄
            draw.line([(26, 44), (40, 18)], fill=(255, 255, 255, 220), width=3)
            # 扫帚毛
            for i in range(5):
                ox = 22 + i * 2
                draw.line([(26, 44), (ox, 48)], fill=(255, 255, 255, 180), width=2)
            # 星星
            star_points = 5
            star_coords = []
            scx, scy = 44, 22
            for i in range(star_points * 2):
                angle = -math.pi / 2 + i * math.pi / star_points
                r = 10 if i % 2 == 0 else 4
                star_coords.append((scx + r * math.cos(angle), scy + r * math.sin(angle)))
            draw.polygon(star_coords, fill=(255, 235, 59))
        elif name == "export":
            # 导出箭头 + 文档
            draw_rounded_rect(draw, (18, 18, 44, 36), radius=4,
                              fill=(255, 255, 255, 230), width=0)
            # 向上箭头
            draw.line([(31, 46), (31, 26)], fill=(255, 255, 255, 230), width=3)
            draw.line([(24, 32), (31, 26), (38, 32)], fill=(255, 255, 255, 230), width=3)
            # 文档文字行
            for i, ly in enumerate([22, 27, 32]):
                draw.line([(22, ly), (38, ly)], fill=(r, g, b), width=1)
        elif name == "file_ops":
            # 齿轮
            draw_circle(draw, size // 2, size // 2, 14,
                        fill=(255, 255, 255, 230))
            # 齿轮齿
            for i in range(8):
                angle = math.radians(i * 45)
                gx = size // 2 + 20 * math.cos(angle)
                gy = size // 2 + 20 * math.sin(angle)
                draw_circle(draw, gx, gy, 5, fill=(255, 255, 255, 200))

        img.save(os.path.join(ICONS_DIR, f"mod_{name}.png"))
    print("✓ icons/mod_*.png (5 个功能模块图标)")


# ═══════════════════════════════════════════
# 4. 小按钮图标 (24x24)
# ═══════════════════════════════════════════

def generate_action_icons():
    """生成小按钮图标"""
    size = 24
    icons = {
        "undo": {"bg": (255, 193, 7), "symbol": "↩"},
        "browse": {"bg": (74, 144, 226), "symbol": "🔍"},
        "apply": {"bg": (76, 175, 80), "symbol": "✓"},
        "preview": {"bg": (38, 166, 154), "symbol": "👁"},
    }

    for name, data in icons.items():
        img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        r, g, b = data["bg"]

        # 圆角背景
        draw_rounded_rect(draw, (2, 2, size - 2, size - 2), radius=6,
                          fill=(r, g, b, 230))

        if name == "undo":
            # 向左箭头
            draw.arc([6, 6, 18, 18], 0, 200, fill=(255, 255, 255, 230), width=3)
            draw.line([(4, 12), (8, 8), (12, 12)], fill=(255, 255, 255, 230), width=2)
        elif name == "browse":
            # 放大镜
            draw_circle(draw, 11, 11, 6, fill=(255, 255, 255, 230))
            draw.line([(16, 16), (21, 21)], fill=(255, 255, 255, 200), width=3)
        elif name == "apply":
            # 勾号
            draw.line([(5, 12), (10, 18), (19, 6)], fill=(255, 255, 255, 230), width=3)
        elif name == "preview":
            # 眼睛
            draw_circle(draw, 12, 12, 7, fill=(255, 255, 255, 230), outline=(0, 0, 0, 40))
            draw_circle(draw, 12, 12, 3, fill=(r, g, b, 180))

        img.save(os.path.join(ICONS_DIR, f"action_{name}.png"))
    print("✓ icons/action_*.png (4 个操作按钮图标)")


# ═══════════════════════════════════════════
# 5. 背景装饰元素
# ═══════════════════════════════════════════

def generate_decorations():
    """生成背景装饰元素（小星星、圆点）"""
    import random

    # 星星装饰 (32x32)
    img = Image.new("RGBA", (32, 32), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    star_points = 5
    coords = []
    cx, cy, outer, inner = 16, 16, 12, 5
    for i in range(star_points * 2):
        angle = -math.pi / 2 + i * math.pi / star_points
        r = outer if i % 2 == 0 else inner
        coords.append((cx + r * math.cos(angle), cy + r * math.sin(angle)))
    draw.polygon(coords, fill=(255, 193, 7, 200))
    img.save(os.path.join(ICONS_DIR, "star.png"))
    print("✓ icons/star.png")

    # 圆点装饰 (16x16)
    img2 = Image.new("RGBA", (16, 16), (0, 0, 0, 0))
    draw2 = ImageDraw.Draw(img2)
    draw_circle(draw2, 8, 8, 5, fill=(100, 180, 255, 150))
    img2.save(os.path.join(ICONS_DIR, "dot.png"))
    print("✓ icons/dot.png")


# ═══════════════════════════════════════════
# 6. 小机器人按钮图标 (64x64) - 用于绿色确认按钮
# ═══════════════════════════════════════════

def generate_mini_robot():
    """生成小机器人图标（用于确认按钮）"""
    size = 64
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    cx, cy = size // 2, size // 2

    # 颜色
    body = (255, 255, 255)
    accent = (74, 144, 226)

    # 身体
    draw_rounded_rect(draw, (cx - 14, cy, cx + 14, cy + 22), radius=8, fill=body)
    # 头
    draw_circle(draw, cx, cy - 10, 16, fill=body)
    # 面罩
    draw_circle(draw, cx, cy - 10, 10, fill=accent)
    # 眼睛
    draw_circle(draw, cx - 5, cy - 12, 2.5, fill=(255, 255, 255))
    draw_circle(draw, cx + 5, cy - 12, 2.5, fill=(255, 255, 255))
    # 天线
    draw.line([(cx, cy - 26), (cx, cy - 18)], fill=accent, width=2)
    draw_circle(draw, cx, cy - 28, 3, fill=(255, 193, 7))
    # 手臂
    draw_rounded_rect(draw, (cx - 22, cy + 2, cx - 16, cy + 12), radius=4, fill=body)
    draw_rounded_rect(draw, (cx + 16, cy + 2, cx + 22, cy + 12), radius=4, fill=body)

    img.save(os.path.join(ICONS_DIR, "mini_robot.png"))
    print("✓ icons/mini_robot.png")


# ═══════════════════════════════════════════
# 主入口
# ═══════════════════════════════════════════

if __name__ == "__main__":
    print("=" * 40)
    print("生成所有图标资源...")
    print("=" * 40)
    print()

    generate_robot()
    print()

    generate_file_icons()
    print()

    generate_module_icons()
    print()

    generate_action_icons()
    print()

    generate_decorations()
    print()

    generate_mini_robot()
    print()

    # 列出生成的文件
    files = [f for f in os.listdir(ICONS_DIR) if f.endswith(".png")]
    print(f"成功生成 {len(files)} 个 PNG 图标:")
    for f in sorted(files):
        fp = os.path.join(ICONS_DIR, f)
        sz = os.path.getsize(fp)
        print(f"  {f:30s} {sz:>6d} 字节")
    print("=" * 40)
