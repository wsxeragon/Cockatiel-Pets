import os
import math
from PIL import Image, ImageDraw, ImageFont

BASE_DIR = r"D:\pets"
POSES_DIR = os.path.join(BASE_DIR, "2d", "official_poses")
SPRITES_DIR = os.path.join(BASE_DIR, "assets", "sprites")

CANVAS_W = 280
CANVAS_H = 240
GROUND_Y = 220

# Palette matching the official pixel art
C_DARK = (28, 24, 26, 255)
C_WHITE = (245, 245, 245, 255)
C_BEAK = (175, 140, 130, 255)
C_BEAK_LIGHT = (205, 175, 165, 255)
C_MOUTH_DARK = (22, 14, 18, 255)
C_TONGUE = (225, 115, 120, 255)
C_YELLOW = (248, 230, 84, 255)
C_NOTE = (90, 185, 255, 255)
C_GREY_WING = (124, 115, 115, 255)
C_GREY_LIGHT = (165, 155, 155, 255)
C_GREY_DARK = (80, 72, 75, 255)
C_GREY_BODY = (142, 136, 134, 255)

def create_canvas():
    return Image.new("RGBA", (CANVAS_W, CANVAS_H), (0, 0, 0, 0))

def load_clean_pose(filename):
    p = os.path.join(POSES_DIR, filename)
    im = Image.open(p).convert("RGBA")
    w, h = im.size
    visited = set()
    components = []
    fg = set()
    for y in range(h):
        for x in range(w):
            if im.getpixel((x, y))[3] > 20:
                fg.add((x, y))
    for pt in fg:
        if pt in visited: continue
        comp = []
        q = [pt]
        visited.add(pt)
        while q:
            cx, cy = q.pop()
            comp.append((cx, cy))
            for dx, dy in [(-1,0), (1,0), (0,-1), (0,1), (-1,-1), (1,1), (-1,1), (1,-1)]:
                nx, ny = cx + dx, cy + dy
                if (nx, ny) in fg and (nx, ny) not in visited:
                    visited.add((nx, ny))
                    q.append((nx, ny))
        components.append(comp)
    keep = set()
    for c in components:
        if len(c) >= 300:
            keep.update(c)
    cleaned = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    for pt in keep:
        cleaned.putpixel(pt, im.getpixel(pt))
    return cleaned.transpose(Image.Transpose.FLIP_LEFT_RIGHT)

alert_raw = load_clean_pose("06_alert_警觉.png")
hiss_raw = load_clean_pose("07_hissing_哈气.png")
fly_raw = load_clean_pose("08_flying_飞行.png")

# --- 1. BEAK ANIMATION FOR SINGING (sing_0, sing_1, sing_2) ---
def place_on_ground(sprite, offset_x=45, offset_y=0):
    c = create_canvas()
    x = int(offset_x)
    y = int(GROUND_Y - sprite.height + offset_y)
    c.paste(sprite, (x, y), sprite)
    return c, x, y

alert_canvas, ax, ay = place_on_ground(alert_raw, offset_x=45)

# sing_0: Closed beak (蓄力)
sing_0 = alert_canvas.copy()

# sing_1: Open beak (微张露舌 + 单音符)
sing_1 = alert_canvas.copy()
draw1 = ImageDraw.Draw(sing_1)
bx = ax + 2
by = ay + 87
# Dark oral cavity inside beak
draw1.polygon([(bx + 2, by), (bx + 18, by + 1), (bx + 16, by + 7), (bx + 2, by + 5)], fill=C_MOUTH_DARK)
# Pink tongue
draw1.ellipse([bx + 6, by + 2, bx + 13, by + 6], fill=C_TONGUE)
# Lower beak dropped down
draw1.polygon([(bx + 1, by + 5), (bx + 15, by + 7), (bx + 14, by + 13), (bx + 2, by + 11)], fill=C_BEAK, outline=C_DARK)
draw1.line([(bx + 3, by + 7), (bx + 12, by + 8)], fill=C_BEAK_LIGHT, width=1)
# Musical note 1 floating
nx, ny = 95, 25
draw1.ellipse([nx, ny + 10, nx + 10, ny + 18], fill=C_NOTE, outline=C_DARK, width=2)
draw1.line([(nx + 8, ny + 12), (nx + 8, ny)], fill=C_DARK, width=2)
draw1.line([(nx + 8, ny), (nx + 16, ny + 3)], fill=C_DARK, width=3)

# sing_2: Wide open beak (大张欢唱 + 双音符)
sing_2 = alert_canvas.copy()
draw2 = ImageDraw.Draw(sing_2)
draw2.polygon([(bx + 1, by), (bx + 20, by + 1), (bx + 17, by + 11), (bx + 1, by + 9)], fill=C_MOUTH_DARK)
draw2.ellipse([bx + 5, by + 4, bx + 14, by + 9], fill=C_TONGUE)
draw2.polygon([(bx, by + 9), (bx + 16, by + 11), (bx + 14, by + 17), (bx + 1, by + 15)], fill=C_BEAK, outline=C_DARK)
draw2.line([(bx + 2, by + 11), (bx + 13, by + 13)], fill=C_BEAK_LIGHT, width=1)
nx, ny = 85, 18
draw2.ellipse([nx, ny + 12, nx + 10, ny + 20], fill=C_NOTE, outline=C_DARK, width=2)
draw2.ellipse([nx + 16, ny + 8, nx + 26, ny + 16], fill=C_NOTE, outline=C_DARK, width=2)
draw2.line([(nx + 8, ny + 14), (nx + 8, ny)], fill=C_DARK, width=2)
draw2.line([(nx + 24, ny + 10), (nx + 24, ny - 4)], fill=C_DARK, width=2)
draw2.line([(nx + 8, ny), (nx + 24, ny - 4)], fill=C_DARK, width=3)

sing_0.save(os.path.join(SPRITES_DIR, "sing_0.png"))
sing_1.save(os.path.join(SPRITES_DIR, "sing_1.png"))
sing_2.save(os.path.join(SPRITES_DIR, "sing_2.png"))

# --- 2. HISSING (hiss_0, hiss_1) ---
hiss_canvas, hx, hy = place_on_ground(hiss_raw, offset_x=40)
hiss_0 = hiss_canvas.copy()
draw_h0 = ImageDraw.Draw(hiss_0)
draw_h0.polygon([(hx + 40, hy + 90), (hx + 56, hy + 92), (hx + 52, hy + 98), (hx + 38, hy + 96)], fill=C_BEAK, outline=C_DARK)
hiss_0.save(os.path.join(SPRITES_DIR, "hiss_0.png"))
hiss_1 = hiss_canvas.copy()
hiss_1.save(os.path.join(SPRITES_DIR, "hiss_1.png"))

# --- 3. FLAPPING WINGS FOR FLIGHT ---
FLY_BASE_Y = 160
fly_x = 35
fly_y = FLY_BASE_Y - fly_raw.height + 35  # ~ y=2

# 3.1 fly_0: Official Upstroke Wings (High up)
fly_0 = create_canvas()
fly_0.paste(fly_raw, (fly_x, fly_y), fly_raw)
fly_0.save(os.path.join(SPRITES_DIR, "fly_0.png"))

# Build clean seamless flight fuselage (Head, Neck, Torso, Tail, Feet)
# Follow the natural spine curve:
fuselage = fly_raw.copy()
w, h = fuselage.size
for y in range(h):
    for x in range(w):
        if x >= 55:
            spine_y = 92 + (x - 55) * 0.52
            if y < spine_y:
                fuselage.putpixel((x, y), (0, 0, 0, 0))

draw_fuse = ImageDraw.Draw(fuselage)
# Outline and smooth the back spine
for x in range(55, 145):
    sy = int(92 + (x - 55) * 0.52)
    fuselage.putpixel((x, sy), C_DARK)
    fuselage.putpixel((x, sy + 1), C_GREY_DARK)

# 3.2 fly_1: Level Glide Wings (Horizontal rearward sweep)
fly_1 = create_canvas()
draw_f1 = ImageDraw.Draw(fly_1)

# Far Wing (above spine, extending back-horizontal)
far_wing_mid = [
    (fly_x + 75, fly_y + 88),
    (fly_x + 115, fly_y + 65),
    (fly_x + 165, fly_y + 60),
    (fly_x + 195, fly_y + 68),
    (fly_x + 175, fly_y + 90),
    (fly_x + 120, fly_y + 95),
]
draw_f1.polygon(far_wing_mid, fill=C_GREY_DARK, outline=C_DARK)

# Paste fuselage in front of far wing
fly_1.paste(fuselage, (fly_x, fly_y), fuselage)

# Near Wing (horizontal swept wing with smooth curved leading edge)
near_wing_mid = [
    (fly_x + 62, fly_y + 94),
    (fly_x + 95, fly_y + 82),
    (fly_x + 145, fly_y + 78),
    (fly_x + 188, fly_y + 84),
    (fly_x + 192, fly_y + 94),
    (fly_x + 155, fly_y + 112),
    (fly_x + 110, fly_y + 118),
    (fly_x + 65, fly_y + 108),
]
draw_f1.polygon(near_wing_mid, fill=C_GREY_WING, outline=C_DARK)

# White flight feather bar along middle of near wing
white_bar_mid = [
    (fly_x + 85, fly_y + 90),
    (fly_x + 135, fly_y + 86),
    (fly_x + 168, fly_y + 90),
    (fly_x + 148, fly_y + 102),
    (fly_x + 98, fly_y + 104),
]
draw_f1.polygon(white_bar_mid, fill=C_WHITE, outline=C_DARK)

# Flight feather ribs
for fx, fy1, fy2 in [(120, 92, 108), (140, 90, 105), (160, 88, 100), (175, 87, 95)]:
    draw_f1.line([(fly_x + fx, fly_y + fy1), (fly_x + fx + 12, fly_y + fy2)], fill=C_GREY_DARK, width=2)

fly_1.save(os.path.join(SPRITES_DIR, "fly_1.png"))

# 3.3 fly_2: Downstroke Wings (Wings angled down along flank, body lifted by 4px)
fly_2 = create_canvas()
draw_f2 = ImageDraw.Draw(fly_2)
lift_dy = -4

# Far Wing (pushed down behind body)
far_wing_down = [
    (fly_x + 85, fly_y + lift_dy + 108),
    (fly_x + 125, fly_y + lift_dy + 122),
    (fly_x + 165, fly_y + lift_dy + 140),
    (fly_x + 155, fly_y + lift_dy + 152),
    (fly_x + 115, fly_y + lift_dy + 135),
]
draw_f2.polygon(far_wing_down, fill=C_GREY_DARK, outline=C_DARK)

# Paste fuselage (its clean rounded spine remains beautifully visible!)
fly_2.paste(fuselage, (fly_x, fly_y + lift_dy), fuselage)

# Near Wing (pushed down from shoulder, sweeping down across the flank)
near_wing_down = [
    (fly_x + 62, fly_y + lift_dy + 98),
    (fly_x + 92, fly_y + lift_dy + 112),
    (fly_x + 130, fly_y + lift_dy + 138),
    (fly_x + 160, fly_y + lift_dy + 162),
    (fly_x + 150, fly_y + lift_dy + 172),
    (fly_x + 118, fly_y + lift_dy + 155),
    (fly_x + 82, fly_y + lift_dy + 132),
    (fly_x + 62, fly_y + lift_dy + 110),
]
draw_f2.polygon(near_wing_down, fill=C_GREY_WING, outline=C_DARK)

# White wing bar on downstroke wing
white_bar_down = [
    (fly_x + 80, fly_y + lift_dy + 112),
    (fly_x + 112, fly_y + lift_dy + 128),
    (fly_x + 138, fly_y + lift_dy + 148),
    (fly_x + 128, fly_y + lift_dy + 158),
    (fly_x + 92, fly_y + lift_dy + 130),
]
draw_f2.polygon(white_bar_down, fill=C_WHITE, outline=C_DARK)

# Scalloped flight feather lines
for fx, fy1, fy2 in [(95, 120, 134), (115, 132, 148), (135, 148, 165)]:
    draw_f2.line([(fly_x + fx, fly_y + lift_dy + fy1), (fly_x + fx + 10, fly_y + lift_dy + fy2)], fill=C_GREY_DARK, width=2)

fly_2.save(os.path.join(SPRITES_DIR, "fly_2.png"))

print("Enhanced frames successfully built and saved!")

# Generate Master Comparison Sheet
sheet = Image.new("RGBA", (900, 560), (245, 238, 230, 255))
draw_s = ImageDraw.Draw(sheet)

try:
    f_title = ImageFont.truetype("msyh.ttc", 20)
    f_sub = ImageFont.truetype("msyh.ttc", 13)
    f_lbl = ImageFont.truetype("msyh.ttc", 12)
except Exception:
    f_title = f_sub = f_lbl = ImageFont.load_default()

draw_s.text((30, 20), "🐤 飞行翅膀煽动 & 唱歌嘴壳一张一合 专项升级总览", fill=(45, 36, 32), font=f_title)
draw_s.text((30, 50), "飞行动画三态(高展->平展->下压) | 唱歌张合三态(闭合->微张露舌->大张欢唱) | 目录: D:\\pets\\assets\\sprites", fill=(120, 110, 105), font=f_sub)

cards = [
    ("sing_0", "唱歌-嘴闭合蓄力", sing_0),
    ("sing_1", "唱歌-嘴壳微张露舌", sing_1),
    ("sing_2", "唱歌-大张欢唱高音", sing_2),
    ("fly_0", "飞行-双翼高展 (Up)", fly_0),
    ("fly_1", "飞行-双翼平展 (Glide)", fly_1),
    ("fly_2", "飞行-双翼下压 (Down)", fly_2),
]

for idx, (cid, clbl, cimg) in enumerate(cards):
    row = idx // 3
    col = idx % 3
    x = 30 + col * 280
    y = 85 + row * 225
    draw_s.rectangle([x, y, x + 265, y + 210], fill=(255, 255, 255), outline=(225, 215, 205), width=1)
    draw_s.text((x + 12, y + 8), f"{cid} : {clbl}", fill=(45, 36, 32), font=f_lbl)
    
    scaled = cimg.resize((int(cimg.width * 0.65), int(cimg.height * 0.65)), Image.Resampling.NEAREST)
    draw_s.rectangle([x + 42, y + 30, x + 42 + scaled.width, y + 30 + scaled.height], fill=(248, 244, 238))
    sheet.paste(scaled, (x + 42, y + 30), scaled)

out_sheet = os.path.join(BASE_DIR, "2d", "flapping_singing_preview.png")
sheet.save(out_sheet)
print(f"Comparison sheet saved to: {out_sheet}")
