import os
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

BASE_DIR = Path(r"D:\pets\2d-new")
NEW_DIR = BASE_DIR / "sprites"
ORIG_DIR = BASE_DIR / "sprites_original"

# Pairs to compare
COMPARISONS = [
    ("低头求摸 (Bow)", "bow_1.png", "【原版】普通闭眼下探", "【优化版】惬意眯眯笑眼(^_^)与腮红微红"),
    ("外八字踱步 (Waddle)", "waddle_1.png", "【原版】仅脚底平移", "【优化版】左右重心摇摆鸭子步+尾巴甩动"),
    ("空中飞行 (Fly)", "fly_0.png", "【原版】双脚下垂伸直", "【优化版】两只小爪紧缩进肚皮圆流线"),
    ("母鸡蹲睡觉 (Sleep)", "sleep_0.png", "【原版】露出脚掌蹲坐", "【优化版】彻底收脚进肚皮(农民揣团子)"),
    ("啄地顿挫 (Peck)", "peck_1.png", "【原版】匀速探头", "【优化版】触地顿挫尾部微弹打击感"),
    ("欢快独唱 (Sing)", "sing_1.png", "【原版】普通展翅吹口哨", "【优化版】经典心形翅膀(Heart Wings)合体"),
]

CARD_W = 550
CARD_H = 175
COLS = 2
ROWS = (len(COMPARISONS) + COLS - 1) // COLS

SHEET_W = 60 + COLS * (CARD_W + 25)
SHEET_H = 120 + ROWS * (CARD_H + 20)

sheet = Image.new("RGBA", (SHEET_W, SHEET_H), (245, 238, 230, 255))
d = ImageDraw.Draw(sheet)

try:
    font_title = ImageFont.truetype("msyh.ttc", 22)
    font_sub = ImageFont.truetype("msyh.ttc", 13)
    font_card = ImageFont.truetype("msyh.ttc", 13)
    font_bold = ImageFont.truetype("msyhbd.ttc", 14)
except Exception:
    font_title = font_sub = font_card = font_bold = ImageFont.load_default()

d.text((35, 25), "🐤 现有萌系 Q 版桌宠 第一版动画优化审核对比总览", fill=(45, 36, 32), font=font_title)
d.text((35, 60), "保持 100x80 经典麻糬萌系体型不变 | 注入生物习性与微表情灵魂细节 | 目录: D:\\pets\\2d-new\\sprites", fill=(120, 110, 105), font=font_sub)

for idx, (title, fname, desc_orig, desc_new) in enumerate(COMPARISONS):
    r = idx // COLS
    c = idx % COLS
    x = 35 + c * (CARD_W + 20)
    y = 100 + r * (CARD_H + 20)

    # Card background
    d.rectangle([x, y, x + CARD_W, y + CARD_H], fill=(255, 255, 255), outline=(225, 215, 205), width=1)
    d.text((x + 14, y + 10), title, fill=(45, 36, 32), font=font_bold)

    # 1. Original sprite (100x80 scaled 1.3x to 130x104)
    orig_path = ORIG_DIR / fname
    if orig_path.exists():
        im_o = Image.open(orig_path)
        im_o_scaled = im_o.resize((120, 96), Image.Resampling.NEAREST)
        d.rectangle([x + 14, y + 36, x + 14 + 120, y + 36 + 96], fill=(248, 244, 238))
        sheet.paste(im_o_scaled, (x + 14, y + 36), im_o_scaled)
        d.text((x + 14, y + 138), "原版", fill=(130, 120, 115), font=font_card)

    # Arrow separator
    d.text((x + 148, y + 74), "➜", fill=(210, 80, 60), font=font_bold)

    # 2. Optimized sprite
    new_path = NEW_DIR / fname
    if new_path.exists():
        im_n = Image.open(new_path)
        im_n_scaled = im_n.resize((120, 96), Image.Resampling.NEAREST)
        d.rectangle([x + 175, y + 36, x + 175 + 120, y + 36 + 96], fill=(244, 248, 244))
        sheet.paste(im_n_scaled, (x + 175, y + 36), im_n_scaled)
        d.text((x + 175, y + 138), "优化版", fill=(50, 140, 60), font=font_bold)

    # Description text on the right
    d.text((x + 305, y + 42), desc_orig, fill=(140, 130, 125), font=font_card)
    d.text((x + 305, y + 85), desc_new, fill=(40, 120, 50), font=font_card)

out_path = BASE_DIR / "comparison_preview.png"
sheet.save(out_path)
print(f"Saved comparison sheet to {out_path}")
