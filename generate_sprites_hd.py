import os
import math
from PIL import Image, ImageDraw, ImageOps

ASSETS_DIR = os.path.join(os.path.dirname(__file__), "assets", "sprites")
os.makedirs(ASSETS_DIR, exist_ok=True)

BASE_SPRITE_PATH = os.path.join(os.path.dirname(__file__), "assets", "bird_clean_pixel.png")

CANVAS_W = 960
CANVAS_H = 760
TARGET_W = 200
TARGET_H = 160

# Colors for details
C_YELLOW = (241, 238, 109, 255)
C_DARK = (40, 40, 40, 255)
C_CRUMB = (200, 160, 110, 255)
C_NOTE = (80, 185, 255, 255)
C_PINK_MOUTH = (220, 90, 85, 255)

def get_base_bird():
    return Image.open(BASE_SPRITE_PATH).convert("RGBA")

def create_canvas():
    return Image.new("RGBA", (CANVAS_W, CANVAS_H), (0, 0, 0, 0))

def place_bird(bird_img, offset_x=80, offset_y=70, scale_x=1.0, scale_y=1.0):
    canvas = create_canvas()
    bw, bh = bird_img.size
    new_w = int(round(bw * scale_x))
    new_h = int(round(bh * scale_y))
    scaled_bird = bird_img.resize((new_w, new_h), Image.Resampling.BILINEAR if (scale_x != 1.0 or scale_y != 1.0) else Image.Resampling.NEAREST)
    canvas.paste(scaled_bird, (int(offset_x), int(offset_y)), scaled_bird)
    return canvas

def make_blink_bird(base_bird, eye_style="happy"):
    """把眼睛替换为闭眼/眯眼弧线"""
    bird = base_bird.copy()
    # Eye bbox in base bird: [59, 89], [152, 182]
    # Sample face color
    for y in range(152, 183):
        for x in range(59, 90):
            if bird.getpixel((x, y))[3] > 0:
                bird.putpixel((x, y), C_YELLOW)

    # 绘制闭眼弧线
    if eye_style == "happy":
        # ^_^ 弯弯笑眼
        for dx in range(-11, 12):
            x = 74 + dx
            dy = int(round(0.045 * (dx**2)))
            y = 166 - 2 + dy
            for thick in range(4):
                bird.putpixel((x, y + thick), C_DARK)
    elif eye_style == "sleepy":
        # 一字缝
        for dx in range(-10, 11):
            x = 74 + dx
            y = 168
            for thick in range(4):
                bird.putpixel((x, y + thick), C_DARK)
    elif eye_style == "wide":
        # 大眼睛 (受惊)
        draw = ImageDraw.Draw(bird)
        draw.ellipse([64, 153, 86, 179], fill=(20, 20, 20, 255), outline=(10, 10, 10, 255))
        draw.ellipse([70, 156, 76, 162], fill=(255, 255, 255, 255))
    return bird

def make_open_beak_bird(base_bird, mode="sing"):
    """张嘴/唱歌/咬人"""
    bird = base_bird.copy()
    draw = ImageDraw.Draw(bird)
    # Beak is around x=10..60, y=150..195
    if mode == "sing":
        # 嘴唇张开一个小三角
        draw.polygon([(25, 170), (45, 160), (45, 178)], fill=C_PINK_MOUTH)
        draw.line([(25, 170), (45, 160)], fill=C_DARK, width=3)
        draw.line([(25, 170), (45, 178)], fill=C_DARK, width=3)
    elif mode == "bite" or mode == "hiss":
        # 嘴巴大张
        draw.polygon([(18, 168), (48, 152), (48, 184)], fill=C_PINK_MOUTH)
        draw.polygon([(28, 166), (44, 162), (44, 174)], fill=(240, 120, 120, 255)) # 舌头
        draw.line([(18, 168), (48, 152)], fill=C_DARK, width=4)
        draw.line([(18, 168), (48, 184)], fill=C_DARK, width=4)
    elif mode == "chew":
        # 细微开合
        draw.polygon([(30, 172), (45, 166), (45, 176)], fill=C_PINK_MOUTH)
        draw.line([(30, 172), (45, 166)], fill=C_DARK, width=2)
        draw.line([(30, 172), (45, 176)], fill=C_DARK, width=2)
    return bird

def add_crumbs(canvas, bx=100, by=240):
    """添加啃咬碎屑特效"""
    draw = ImageDraw.Draw(canvas)
    crumbs = [
        (bx - 15, by + 10, 6),
        (bx - 28, by + 25, 5),
        (bx - 10, by + 35, 7),
        (bx - 35, by + 12, 4),
        (bx + 5, by + 40, 5),
    ]
    for cx, cy, sz in crumbs:
        draw.rectangle([cx, cy, cx + sz, cy + sz], fill=C_CRUMB, outline=C_DARK)

def add_music_note(canvas, nx=160, ny=100):
    """添加唱歌八分音符"""
    draw = ImageDraw.Draw(canvas)
    # Note head 1
    draw.ellipse([nx, ny + 16, nx + 16, ny + 28], fill=C_NOTE, outline=C_DARK)
    # Note head 2
    draw.ellipse([nx + 28, ny + 10, nx + 44, ny + 22], fill=C_NOTE, outline=C_DARK)
    # Stems
    draw.line([(nx + 13, ny + 20), (nx + 13, ny)], fill=C_DARK, width=4)
    draw.line([(nx + 41, ny + 14), (nx + 41, ny - 6)], fill=C_DARK, width=4)
    # Beam
    draw.line([(nx + 13, ny), (nx + 41, ny - 6)], fill=C_DARK, width=6)
    draw.line([(nx + 13, ny + 2), (nx + 41, ny - 4)], fill=C_NOTE, width=3)

def export_frame(canvas, filename):
    # Downscale smoothly to unified target size (200x160)
    final_img = canvas.resize((TARGET_W, TARGET_H), Image.Resampling.LANCZOS)
    out_path = os.path.join(ASSETS_DIR, filename)
    final_img.save(out_path)
    print(f"Generated HD sprite: {out_path}")

def generate_all_hd():
    base_bird = get_base_bird()
    blink_bird = make_blink_bird(base_bird, "happy")
    sleepy_bird = make_blink_bird(base_bird, "sleepy")
    wide_bird = make_blink_bird(base_bird, "wide")

    # 1. IDLE (站立 & 眨眼)
    c_idle0 = place_bird(base_bird, offset_x=80, offset_y=70)
    export_frame(c_idle0, "idle_0.png")

    c_idle1 = place_bird(blink_bird, offset_x=80, offset_y=70)
    export_frame(c_idle1, "idle_1.png")

    # 2. WADDLE (走来走去迈步小碎步)
    # 迈左步: 身体略微前倾与左右摇晃
    c_wad0 = place_bird(base_bird, offset_x=80, offset_y=67)
    export_frame(c_wad0, "waddle_0.png")

    c_wad1 = place_bird(base_bird, offset_x=80, offset_y=73)
    export_frame(c_wad1, "waddle_1.png")

    # 3. PECK (啄桌面)
    # 头部与喙部向下啄击
    rot_peck0 = base_bird.rotate(-6, resample=Image.Resampling.BICUBIC, center=(350, 450))
    c_peck0 = place_bird(rot_peck0, offset_x=80, offset_y=75)
    export_frame(c_peck0, "peck_0.png")

    rot_peck1 = base_bird.rotate(-14, resample=Image.Resampling.BICUBIC, center=(350, 450))
    c_peck1 = place_bird(rot_peck1, offset_x=70, offset_y=95)
    export_frame(c_peck1, "peck_1.png")

    # 4. MISCHIEF CHEW (啃咬屏幕拆家)
    chew_bird0 = make_open_beak_bird(base_bird, "chew")
    rot_chew0 = chew_bird0.rotate(-8, resample=Image.Resampling.BICUBIC, center=(350, 450))
    c_chew0 = place_bird(rot_chew0, offset_x=75, offset_y=82)
    export_frame(c_chew0, "chew_0.png")

    chew_bird1 = make_open_beak_bird(base_bird, "bite")
    rot_chew1 = chew_bird1.rotate(-12, resample=Image.Resampling.BICUBIC, center=(350, 450))
    c_chew1 = place_bird(rot_chew1, offset_x=70, offset_y=88)
    add_crumbs(c_chew1, bx=140, by=290)
    export_frame(c_chew1, "chew_1.png")

    # 5. COMFORT FLUFF (蓬成毛球 Borb)
    # 身体膨胀变圆，闭眼享受
    c_fluff0 = place_bird(sleepy_bird, offset_x=65, offset_y=60, scale_x=1.06, scale_y=1.08)
    export_frame(c_fluff0, "fluff_0.png")

    c_fluff1 = place_bird(blink_bird, offset_x=60, offset_y=55, scale_x=1.09, scale_y=1.12)
    export_frame(c_fluff1, "fluff_1.png")

    # 6. COMFORT PREEN (理毛)
    # 歪头梳理翅膀
    rot_preen0 = sleepy_bird.rotate(6, resample=Image.Resampling.BICUBIC, center=(350, 400))
    c_preen0 = place_bird(rot_preen0, offset_x=85, offset_y=72)
    export_frame(c_preen0, "preen_0.png")

    rot_preen1 = sleepy_bird.rotate(10, resample=Image.Resampling.BICUBIC, center=(350, 400))
    c_preen1 = place_bird(rot_preen1, offset_x=90, offset_y=75)
    export_frame(c_preen1, "preen_1.png")

    # 7. COMFORT BOW (低头求摸摸)
    # 头部贴近地面，眼睛微闭享受
    rot_bow0 = sleepy_bird.rotate(-15, resample=Image.Resampling.BICUBIC, center=(400, 500))
    c_bow0 = place_bird(rot_bow0, offset_x=70, offset_y=100)
    export_frame(c_bow0, "bow_0.png")

    rot_bow1 = blink_bird.rotate(-20, resample=Image.Resampling.BICUBIC, center=(400, 500))
    c_bow1 = place_bird(rot_bow1, offset_x=65, offset_y=110)
    export_frame(c_bow1, "bow_1.png")

    # 8. EXCITE HOP (雀跃小跳)
    # 原地跳起悬空
    c_hop0 = place_bird(base_bird, offset_x=80, offset_y=70)
    export_frame(c_hop0, "hop_0.png")

    c_hop1 = place_bird(base_bird, offset_x=80, offset_y=28) # 腾空 42px
    export_frame(c_hop1, "hop_1.png")

    # 9. EXCITE BOB (点头狂魔)
    # 头部上下剧烈打节拍
    rot_bob0 = base_bird.rotate(6, resample=Image.Resampling.BICUBIC, center=(350, 450))
    c_bob0 = place_bird(rot_bob0, offset_x=80, offset_y=55)
    export_frame(c_bob0, "bob_0.png")

    rot_bob1 = base_bird.rotate(-12, resample=Image.Resampling.BICUBIC, center=(350, 450))
    c_bob1 = place_bird(rot_bob1, offset_x=75, offset_y=95)
    export_frame(c_bob1, "bob_1.png")

    # 10. EXCITE HEART WINGS (心形翅膀自嗨)
    # 挺胸昂首微张翅膀
    rot_hw0 = base_bird.rotate(4, resample=Image.Resampling.BICUBIC, center=(300, 450))
    c_hw0 = place_bird(rot_hw0, offset_x=75, offset_y=65, scale_x=1.04, scale_y=1.02)
    export_frame(c_hw0, "heart_wings_0.png")

    rot_hw1 = base_bird.rotate(6, resample=Image.Resampling.BICUBIC, center=(300, 450))
    c_hw1 = place_bird(rot_hw1, offset_x=75, offset_y=62, scale_x=1.06, scale_y=1.04)
    export_frame(c_hw1, "heart_wings_1.png")

    # 11. EXCITE SING (唱歌独奏)
    # 昂首张嘴，飘扬音符
    sing_bird0 = make_open_beak_bird(blink_bird, "sing")
    rot_sing0 = sing_bird0.rotate(5, resample=Image.Resampling.BICUBIC, center=(350, 450))
    c_sing0 = place_bird(rot_sing0, offset_x=80, offset_y=60)
    add_music_note(c_sing0, nx=220, ny=90)
    export_frame(c_sing0, "sing_0.png")

    sing_bird1 = make_open_beak_bird(base_bird, "sing")
    rot_sing1 = sing_bird1.rotate(8, resample=Image.Resampling.BICUBIC, center=(350, 450))
    c_sing1 = place_bird(rot_sing1, offset_x=80, offset_y=55)
    add_music_note(c_sing1, nx=240, ny=70)
    export_frame(c_sing1, "sing_1.png")

    # 12. FRIGHT ALERT (警惕拉长身体)
    # 身体紧绷拉长，大眼睛
    c_alert0 = place_bird(wide_bird, offset_x=90, offset_y=50, scale_x=0.92, scale_y=1.10)
    export_frame(c_alert0, "alert_0.png")

    # 13. FRIGHT BITE (闪电咬人)
    # 脖子前伸，大嘴张开
    bite_bird = make_open_beak_bird(wide_bird, "bite")
    rot_bite = bite_bird.rotate(-10, resample=Image.Resampling.BICUBIC, center=(400, 450))
    c_bite = place_bird(rot_bite, offset_x=45, offset_y=75) # 向左冲前 35px
    export_frame(c_bite, "bite_0.png")

    # 14. FRIGHT HISS (炸毛哈气)
    # 身子压低，嘴巴大张
    hiss_bird = make_open_beak_bird(wide_bird, "hiss")
    rot_hiss = hiss_bird.rotate(-6, resample=Image.Resampling.BICUBIC, center=(400, 450))
    c_hiss = place_bird(rot_hiss, offset_x=65, offset_y=90)
    export_frame(c_hiss, "hiss_0.png")

    # 15. FLY (飞行)
    # 翅膀上下拍打姿态
    c_fly0 = place_bird(wide_bird, offset_x=80, offset_y=35, scale_x=1.05, scale_y=0.95)
    export_frame(c_fly0, "fly_0.png")

    c_fly1 = place_bird(wide_bird, offset_x=80, offset_y=65, scale_x=0.95, scale_y=1.05)
    export_frame(c_fly1, "fly_1.png")

if __name__ == "__main__":
    generate_all_hd()
    print("All HD sprites generated successfully!")
