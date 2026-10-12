import os
from PIL import Image, ImageDraw, ImageFont

BASE_DIR = r"D:\pets"
POSES_DIR = os.path.join(BASE_DIR, "2d", "official_poses")
SPRITES_DIR = os.path.join(BASE_DIR, "assets", "sprites")
os.makedirs(SPRITES_DIR, exist_ok=True)

# Standardized Master Canvas Dimensions
CANVAS_W = 280
CANVAS_H = 240
GROUND_Y = 220  # Feet baseline Y

# Colors
C_DARK = (28, 24, 26, 255)
C_WHITE = (245, 245, 245, 255)
C_CRUMB = (205, 160, 115, 255)
C_NOTE = (90, 185, 255, 255)
C_ZZZ = (140, 185, 220, 255)

def create_canvas():
    return Image.new("RGBA", (CANVAS_W, CANVAS_H), (0, 0, 0, 0))

# Load the 8 official poses and flip horizontally to face LEFT (matching original pet)
def load_pose(filename):
    p = os.path.join(POSES_DIR, filename)
    im = Image.open(p).convert("RGBA")
    # Clean small artifacts / text remnants (components < 200 pixels)
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
    # Keep components >= 300 pixels
    keep = set()
    for c in components:
        if len(c) >= 300:
            keep.update(c)
    cleaned = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    for pt in keep:
        cleaned.putpixel(pt, im.getpixel(pt))
    # Flip to face Left
    return cleaned.transpose(Image.Transpose.FLIP_LEFT_RIGHT)

raw_poses = {
    "eating": load_pose("01_eating_啄地取食.png"),
    "sleeping": load_pose("02_sleeping_闭目睡觉.png"),
    "fluffy": load_pose("03_fluffy_毛发蓬松.png"),
    "preening": load_pose("04_preening_整理羽毛.png"),
    "bowing": load_pose("05_bowing_低头求摸.png"),
    "alert": load_pose("06_alert_警觉.png"),
    "hissing": load_pose("07_hissing_哈气.png"),
    "flying": load_pose("08_flying_飞行.png"),
}

# Helper to place a sprite with its feet resting on GROUND_Y
def place_sprite(sprite, offset_x=0, offset_y=0):
    c = create_canvas()
    w, h = sprite.size
    x = int(offset_x)
    y = int(GROUND_Y - h + offset_y)
    c.paste(sprite, (x, y), sprite)
    return c

# Alignments (offset_x) for each pose so the bird is well-centered and feet naturally anchored
# On CANVAS_W = 280:
POSES = {
    "sleeping": place_sprite(raw_poses["sleeping"], offset_x=45),
    "fluffy": place_sprite(raw_poses["fluffy"], offset_x=50),
    "preening": place_sprite(raw_poses["preening"], offset_x=40),
    "alert": place_sprite(raw_poses["alert"], offset_x=45),
    "eating": place_sprite(raw_poses["eating"], offset_x=12),
    "bowing": place_sprite(raw_poses["bowing"], offset_x=22),
    "hissing": place_sprite(raw_poses["hissing"], offset_x=40),
    "flying": place_sprite(raw_poses["flying"], offset_x=35, offset_y=-35),
}

# Create Neutral Standing with OPEN Eyes (derived from sleeping pose by drawing the open eye)
standing_open = POSES["sleeping"].copy()
# In POSES["sleeping"], eye is located at x ~ 121, y ~ 64
# Draw crisp pixel eye (black pupil with white highlight)
eye_cx, eye_cy = 120, 64
for dy in range(-3, 4):
    for dx in range(-3, 4):
        if dx*dx + dy*dy <= 9:
            standing_open.putpixel((eye_cx + dx, eye_cy + dy), C_DARK)
standing_open.putpixel((eye_cx - 1, eye_cy - 1), C_WHITE)
standing_open.putpixel((eye_cx, eye_cy - 1), C_WHITE)

# Generate All 36 Frames
frames = {}

# 1. IDLE (站立睁眼 & 闭眼发呆)
frames["idle_0"] = standing_open
frames["idle_1"] = POSES["sleeping"]

# 2. WADDLE (走来走去碎步)
w0 = standing_open
# waddle_1: foot step forward (shift 1px up and 2px left)
w1 = create_canvas()
w1.paste(standing_open, (-2, -1), standing_open)
w2 = standing_open
# waddle_3: other foot step forward (shift 1px down and 2px right)
w3 = create_canvas()
w3.paste(standing_open, (2, 1), standing_open)
frames["waddle_0"] = w0
frames["waddle_1"] = w1
frames["waddle_2"] = w2
frames["waddle_3"] = w3

# 3. PECK (官方啄地取食)
frames["peck_0"] = POSES["bowing"]
frames["peck_1"] = POSES["eating"]

# 4. CHEW (啃咬拆家带碎屑)
chew_c0 = POSES["eating"]
chew_c1 = POSES["eating"].copy()
draw_chew = ImageDraw.Draw(chew_c1)
# Add wood/seed crumbs near beak (at left around x=18..35, y=210..225)
crumbs = [(22, 212, 4), (16, 218, 3), (28, 222, 5), (34, 215, 3)]
for cx, cy, sz in crumbs:
    draw_chew.rectangle([cx, cy, cx + sz, cy + sz], fill=C_CRUMB, outline=C_DARK)
frames["chew_0"] = chew_c0
frames["chew_1"] = chew_c1

# 5. FLUFF (官方毛发蓬松)
frames["fluff_0"] = POSES["sleeping"]
frames["fluff_1"] = POSES["fluffy"]

# 6. PREEN (官方整理羽毛)
frames["preen_0"] = standing_open
frames["preen_1"] = POSES["preening"]

# 7. BOW (官方低头求摸)
frames["bow_0"] = place_sprite(raw_poses["bowing"], offset_x=22, offset_y=-8)
frames["bow_1"] = POSES["bowing"]

# 8. HOP (雀跃小跳)
frames["hop_0"] = standing_open
# hop_1: airborne 22px
hop_c1 = create_canvas()
hop_c1.paste(standing_open, (0, -22), standing_open)
frames["hop_1"] = hop_c1

# 9. BOB (点头打节拍狂魔)
bob_c0 = create_canvas()
bob_c0.paste(standing_open, (0, 8), standing_open)
frames["bob_0"] = bob_c0
frames["bob_1"] = POSES["alert"]

# 10. HEART WINGS (心形翅膀自嗨)
frames["heart_wings_0"] = standing_open
frames["heart_wings_1"] = POSES["fluffy"]

# 11. SING (独唱飘音符)
sing0 = POSES["alert"]
sing1 = POSES["alert"].copy()
draw_s1 = ImageDraw.Draw(sing1)
# Note 1 above head
nx, ny = 95, 25
draw_s1.ellipse([nx, ny + 10, nx + 10, ny + 18], fill=C_NOTE, outline=C_DARK, width=2)
draw_s1.line([(nx + 8, ny + 12), (nx + 8, ny)], fill=C_DARK, width=2)
draw_s1.line([(nx + 8, ny), (nx + 16, ny + 3)], fill=C_DARK, width=3)

sing2 = POSES["alert"].copy()
draw_s2 = ImageDraw.Draw(sing2)
# Double Note above head
nx, ny = 85, 18
draw_s2.ellipse([nx, ny + 12, nx + 10, ny + 20], fill=C_NOTE, outline=C_DARK, width=2)
draw_s2.ellipse([nx + 16, ny + 8, nx + 26, ny + 16], fill=C_NOTE, outline=C_DARK, width=2)
draw_s2.line([(nx + 8, ny + 14), (nx + 8, ny)], fill=C_DARK, width=2)
draw_s2.line([(nx + 24, ny + 10), (nx + 24, ny - 4)], fill=C_DARK, width=2)
draw_s2.line([(nx + 8, ny), (nx + 24, ny - 4)], fill=C_DARK, width=3)

frames["sing_0"] = sing0
frames["sing_1"] = sing1
frames["sing_2"] = sing2

# 12. ALERT (官方警觉)
frames["alert_0"] = POSES["alert"]

# 13. BITE (闪电反咬)
bite0 = create_canvas()
bite0.paste(raw_poses["hissing"], (30, int(GROUND_Y - raw_poses["hissing"].height)), raw_poses["hissing"])
bite1 = create_canvas()
bite1.paste(raw_poses["hissing"], (18, int(GROUND_Y - raw_poses["hissing"].height)), raw_poses["hissing"])
frames["bite_0"] = bite0
frames["bite_1"] = bite1

# 14. HISS (官方哈气)
frames["hiss_0"] = POSES["hissing"]

# 15. FLY (官方飞行)
fly0 = POSES["flying"]
# fly_1: flap mid
fly1 = create_canvas()
fly1.paste(raw_poses["flying"], (35, int(GROUND_Y - raw_poses["flying"].height - 20)), raw_poses["flying"])
# fly_2: flap down
fly2 = create_canvas()
fly2.paste(raw_poses["flying"], (35, int(GROUND_Y - raw_poses["flying"].height - 35)), raw_poses["flying"])
frames["fly_0"] = fly0
frames["fly_1"] = fly1
frames["fly_2"] = fly2

# 16. SLEEP (安静睡觉)
sleep0 = POSES["sleeping"]
sleep1 = POSES["sleeping"].copy()
draw_sl1 = ImageDraw.Draw(sleep1)
# Draw z z Z
zx, zy = 185, 45
draw_sl1.line([(zx, zy), (zx + 10, zy), (zx, zy + 12), (zx + 10, zy + 12)], fill=C_ZZZ, width=2)
draw_sl1.line([(zx + 16, zy - 15), (zx + 28, zy - 15), (zx + 16, zy), (zx + 28, zy)], fill=C_ZZZ, width=3)
frames["sleep_0"] = sleep0
frames["sleep_1"] = sleep1

# 17. WAKE (醒来伸展)
wake0 = standing_open
wake1 = POSES["alert"]
frames["wake_0"] = wake0
frames["wake_1"] = wake1

# Save all frames into D:\pets\assets\sprites\
for fname, img in frames.items():
    out_path = os.path.join(SPRITES_DIR, f"{fname}.png")
    img.save(out_path)

print(f"Successfully generated and saved {len(frames)} authentic pixel frames into: {SPRITES_DIR}")

# Generate Contact Sheet Preview (D:\pets\2d\official_pixel_sheet.png)
COLS = 6
ROWS = (len(frames) + COLS - 1) // COLS
CARD_W, CARD_H = 200, 180
SHEET_W = 40 + COLS * (CARD_W + 12)
SHEET_H = 100 + ROWS * (CARD_H + 30)

sheet = Image.new("RGBA", (SHEET_W, SHEET_H), (245, 238, 230, 255))
draw_s = ImageDraw.Draw(sheet)

try:
    f_title = ImageFont.truetype("msyh.ttc", 22)
    f_sub = ImageFont.truetype("msyh.ttc", 13)
    f_lbl = ImageFont.truetype("msyh.ttc", 12)
except Exception:
    f_title = f_sub = f_lbl = ImageFont.load_default()

draw_s.text((30, 24), "🐤 原始灰玄凤鹦鹉 官方全姿态正统逐帧像素总览表", fill=(45, 36, 32), font=f_title)
draw_s.text((30, 58), "采用原版整帧像素网格规范 | 100% 整数像素对齐 | 无旋转撕裂 | 目录: D:\\pets\\assets\\sprites", fill=(120, 110, 105), font=f_sub)

sorted_keys = list(frames.keys())
for i, key in enumerate(sorted_keys):
    r = i // COLS
    c = i % COLS
    x = 30 + c * (CARD_W + 12)
    y = 95 + r * (CARD_H + 30)
    
    # Card background
    draw_s.rectangle([x, y, x + CARD_W, y + CARD_H], fill=(255, 255, 255), outline=(225, 215, 205), width=1)
    draw_s.text((x + 8, y + 6), key, fill=(50, 42, 38), font=f_lbl)
    
    # Scale frame to fit card (280x240 -> ~160x137)
    img = frames[key]
    scale = 0.65
    nw, nh = int(CANVAS_W * scale), int(CANVAS_H * scale)
    scaled_f = img.resize((nw, nh), Image.Resampling.NEAREST)
    sheet.paste(scaled_f, (x + int((CARD_W - nw) / 2), y + 22), scaled_f)

out_sheet = os.path.join(BASE_DIR, "2d", "official_pixel_sheet.png")
sheet.save(out_sheet)
print(f"Saved master contact sheet to: {out_sheet}")
