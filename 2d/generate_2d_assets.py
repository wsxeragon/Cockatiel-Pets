import os
import math
from PIL import Image, ImageDraw, ImageFont

BASE_DIR = r"D:\pets\2d"
SPRITES_DIR = os.path.join(BASE_DIR, "sprites")
os.makedirs(SPRITES_DIR, exist_ok=True)

SOURCE_CUTOUT = r"D:\pets\assets\test_clean_turnaround.png"

# Canvas dimensions
CANVAS_W = 600
CANVAS_H = 650

# Colors for details matching the pixel art
C_YELLOW = (248, 230, 84, 255)
C_DARK = (28, 24, 26, 255)
C_CRUMB = (205, 160, 115, 255)
C_NOTE = (90, 185, 255, 255)
C_PINK_MOUTH = (215, 115, 110, 255)

def get_base():
    return Image.open(SOURCE_CUTOUT).convert("RGBA")

def create_canvas():
    return Image.new("RGBA", (CANVAS_W, CANVAS_H), (0, 0, 0, 0))

def place_sprite(sprite, offset_x=70, offset_y=60, scale_x=1.0, scale_y=1.0):
    canvas = create_canvas()
    sw, sh = sprite.size
    nw = int(round(sw * scale_x))
    nh = int(round(sh * scale_y))
    resample = Image.Resampling.BILINEAR if (scale_x != 1.0 or scale_y != 1.0) else Image.Resampling.NEAREST
    scaled = sprite.resize((nw, nh), resample)
    canvas.paste(scaled, (int(offset_x), int(offset_y)), scaled)
    return canvas

def make_blink_sprite(base, eye_style="happy"):
    """替换眼睛区域为闭眼/眯眼弧线"""
    bird = base.copy()
    # Eye bbox in base: X: [40, 81], Y: [120, 196]
    # Sample yellow color near eye (x=60, y=110)
    for y in range(120, 196):
        for x in range(40, 82):
            if bird.getpixel((x, y))[3] > 0:
                bird.putpixel((x, y), C_YELLOW)

    cx = 61
    cy = 158
    if eye_style == "happy":
        # 弯弯笑眼弧线 ^_^
        for dx in range(-16, 17):
            x = cx + dx
            dy = int(round(0.045 * (dx**2)))
            y = cy - 4 + dy
            for thick in range(6):
                bird.putpixel((x, y + thick), C_DARK)
    elif eye_style == "sleepy":
        # 半眯眼一字线
        for dx in range(-15, 16):
            x = cx + dx
            y = cy
            for thick in range(6):
                bird.putpixel((x, y + thick), C_DARK)
    elif eye_style == "wide":
        # 受到惊吓的大圆眼
        draw = ImageDraw.Draw(bird)
        draw.ellipse([cx - 20, cy - 22, cx + 20, cy + 22], fill=C_DARK)
        draw.ellipse([cx - 8, cy - 14, cx + 4, cy - 2], fill=(255, 255, 255, 255))
    return bird

def make_open_beak(base, mode="sing"):
    """张嘴/唱歌/咬人"""
    bird = base.copy()
    draw = ImageDraw.Draw(bird)
    # Beak tip is at x=0..40, y=180..240
    if mode == "sing":
        draw.polygon([(18, 205), (38, 195), (38, 222)], fill=C_PINK_MOUTH)
        draw.line([(18, 205), (38, 195)], fill=C_DARK, width=4)
        draw.line([(18, 205), (38, 222)], fill=C_DARK, width=4)
    elif mode == "bite" or mode == "hiss":
        draw.polygon([(10, 200), (45, 185), (45, 230)], fill=C_PINK_MOUTH)
        draw.polygon([(20, 200), (40, 195), (40, 218)], fill=(240, 130, 130, 255))
        draw.line([(10, 200), (45, 185)], fill=C_DARK, width=5)
        draw.line([(10, 200), (45, 230)], fill=C_DARK, width=5)
    elif mode == "chew":
        draw.polygon([(24, 208), (40, 200), (40, 218)], fill=C_PINK_MOUTH)
        draw.line([(24, 208), (40, 200)], fill=C_DARK, width=3)
        draw.line([(24, 208), (40, 218)], fill=C_DARK, width=3)
    return bird

def add_crumbs(canvas, bx=90, by=270):
    draw = ImageDraw.Draw(canvas)
    crumbs = [
        (bx - 20, by + 10, 8),
        (bx - 36, by + 30, 7),
        (bx - 12, by + 45, 9),
        (bx - 45, by + 15, 6),
        (bx + 8,  by + 50, 7),
    ]
    for cx, cy, sz in crumbs:
        draw.rectangle([cx, cy, cx + sz, cy + sz], fill=C_CRUMB, outline=C_DARK, width=2)

def add_music_note(canvas, nx=110, ny=110):
    draw = ImageDraw.Draw(canvas)
    # Double Note
    draw.ellipse([nx, ny + 20, nx + 22, ny + 36], fill=C_NOTE, outline=C_DARK, width=2)
    draw.ellipse([nx + 36, ny + 12, nx + 58, ny + 28], fill=C_NOTE, outline=C_DARK, width=2)
    draw.line([(nx + 18, ny + 25), (nx + 18, ny - 2)], fill=C_DARK, width=5)
    draw.line([(nx + 54, ny + 18), (nx + 54, ny - 10)], fill=C_DARK, width=5)
    draw.line([(nx + 18, ny - 2), (nx + 54, ny - 10)], fill=C_DARK, width=7)
    draw.line([(nx + 18, ny), (nx + 54, ny - 8)], fill=C_NOTE, width=4)

def generate_all_2d():
    base = get_base()
    # Save base directly
    base.save(os.path.join(BASE_DIR, "base.png"))

    blink = make_blink_sprite(base, "happy")
    sleepy = make_blink_sprite(base, "sleepy")
    wide = make_blink_sprite(base, "wide")

    frames = {}

    # 1. IDLE (日常站立 & 眨眼)
    frames["idle_0"] = place_sprite(base, 70, 60)
    frames["idle_1"] = place_sprite(blink, 70, 60)

    # 2. WADDLE (走来走去迈步小碎步)
    frames["waddle_0"] = place_sprite(base, 70, 56)
    frames["waddle_1"] = place_sprite(base, 70, 64)

    # 3. PECK (低头啄地)
    rot_p0 = base.rotate(-7, resample=Image.Resampling.BICUBIC, center=(250, 400))
    frames["peck_0"] = place_sprite(rot_p0, 65, 75)
    rot_p1 = base.rotate(-15, resample=Image.Resampling.BICUBIC, center=(250, 400))
    frames["peck_1"] = place_sprite(rot_p1, 55, 95)

    # 4. MISCHIEF CHEW (啃咬拆家带碎屑)
    chew0 = make_open_beak(base, "chew")
    rot_c0 = chew0.rotate(-8, resample=Image.Resampling.BICUBIC, center=(250, 400))
    frames["chew_0"] = place_sprite(rot_c0, 65, 75)
    chew1 = make_open_beak(base, "bite")
    rot_c1 = chew1.rotate(-12, resample=Image.Resampling.BICUBIC, center=(250, 400))
    c_chew1 = place_sprite(rot_c1, 60, 85)
    add_crumbs(c_chew1, bx=110, by=280)
    frames["chew_1"] = c_chew1

    # 5. COMFORT FLUFF (蓬成毛球 Borb)
    frames["fluff_0"] = place_sprite(sleepy, 55, 50, scale_x=1.06, scale_y=1.07)
    frames["fluff_1"] = place_sprite(blink, 50, 45, scale_x=1.09, scale_y=1.10)

    # 6. COMFORT PREEN (理毛)
    rot_pr0 = sleepy.rotate(6, resample=Image.Resampling.BICUBIC, center=(250, 380))
    frames["preen_0"] = place_sprite(rot_pr0, 75, 62)
    rot_pr1 = sleepy.rotate(10, resample=Image.Resampling.BICUBIC, center=(250, 380))
    frames["preen_1"] = place_sprite(rot_pr1, 80, 65)

    # 7. COMFORT BOW (低头求抚摸)
    rot_b0 = sleepy.rotate(-16, resample=Image.Resampling.BICUBIC, center=(300, 450))
    frames["bow_0"] = place_sprite(rot_b0, 55, 100)
    rot_b1 = blink.rotate(-22, resample=Image.Resampling.BICUBIC, center=(300, 450))
    frames["bow_1"] = place_sprite(rot_b1, 50, 115)

    # 8. EXCITE HOP (雀跃小跳)
    frames["hop_0"] = place_sprite(base, 70, 60)
    frames["hop_1"] = place_sprite(base, 70, 16) # 腾空 44px

    # 9. EXCITE BOB (点头狂魔打节拍)
    rot_bob0 = base.rotate(7, resample=Image.Resampling.BICUBIC, center=(250, 400))
    frames["bob_0"] = place_sprite(rot_bob0, 75, 45)
    rot_bob1 = base.rotate(-13, resample=Image.Resampling.BICUBIC, center=(250, 400))
    frames["bob_1"] = place_sprite(rot_bob1, 65, 88)

    # 10. EXCITE HEART WINGS (心形翅膀自嗨)
    rot_hw0 = base.rotate(5, resample=Image.Resampling.BICUBIC, center=(220, 380))
    frames["heart_wings_0"] = place_sprite(rot_hw0, 68, 54, scale_x=1.04, scale_y=1.02)
    rot_hw1 = base.rotate(7, resample=Image.Resampling.BICUBIC, center=(220, 380))
    frames["heart_wings_1"] = place_sprite(rot_hw1, 68, 50, scale_x=1.06, scale_y=1.04)

    # 11. EXCITE SING (唱歌独奏飘音符)
    sing0 = make_open_beak(blink, "sing")
    rot_s0 = sing0.rotate(5, resample=Image.Resampling.BICUBIC, center=(250, 400))
    c_sing0 = place_sprite(rot_s0, 70, 52)
    add_music_note(c_sing0, nx=150, ny=90)
    frames["sing_0"] = c_sing0

    sing1 = make_open_beak(base, "sing")
    rot_s1 = sing1.rotate(9, resample=Image.Resampling.BICUBIC, center=(250, 400))
    c_sing1 = place_sprite(rot_s1, 70, 46)
    add_music_note(c_sing1, nx=170, ny=70)
    frames["sing_1"] = c_sing1

    # 12. FRIGHT ALERT (警惕拉长身体)
    frames["alert_0"] = place_sprite(wide, 80, 40, scale_x=0.92, scale_y=1.10)

    # 13. FRIGHT BITE (闪电反咬)
    bite = make_open_beak(wide, "bite")
    rot_bite = bite.rotate(-11, resample=Image.Resampling.BICUBIC, center=(300, 400))
    frames["bite_0"] = place_sprite(rot_bite, 35, 70) # 闪电向前冲

    # 14. FRIGHT HISS (张嘴哈气)
    hiss = make_open_beak(wide, "hiss")
    rot_hiss = hiss.rotate(-7, resample=Image.Resampling.BICUBIC, center=(300, 400))
    frames["hiss_0"] = place_sprite(rot_hiss, 55, 85)

    # 15. FLY (飞行)
    frames["fly_0"] = place_sprite(wide, 70, 25, scale_x=1.05, scale_y=0.94)
    frames["fly_1"] = place_sprite(wide, 70, 65, scale_x=0.95, scale_y=1.06)

    # Save all frames to D:\pets\2d\sprites\
    for name, img in frames.items():
        out_path = os.path.join(SPRITES_DIR, f"{name}.png")
        img.save(out_path)
        print(f"Saved: {out_path}")

    # Generate High-Resolution Master Preview Contact Sheet
    generate_contact_sheet(frames)
    generate_html_preview()

def generate_contact_sheet(frames):
    """生成整齐美观的全动作预览大图 (Preview Sheet)"""
    font_path = r"C:\Windows\Fonts\msyh.ttc"
    try:
        font_main = ImageFont.truetype(font_path, 22)
        font_sub = ImageFont.truetype(font_path, 13)
        font_card = ImageFont.truetype(font_path, 14)
        font_badge = ImageFont.truetype(font_path, 11)
    except Exception:
        font_main = font_sub = font_card = font_badge = ImageFont.load_default()

    categories = [
        ("发呆眨眼 (Idle)", ["idle_0", "idle_1"]),
        ("走来走去 (Waddle)", ["waddle_0", "waddle_1"]),
        ("啄啄桌面 (Peck)", ["peck_0", "peck_1"]),
        ("啃咬拆家 (Chew)", ["chew_0", "chew_1"]),
        ("蓬成毛球 (Fluff)", ["fluff_0", "fluff_1"]),
        ("理理羽毛 (Preen)", ["preen_0", "preen_1"]),
        ("低头求摸 (Bow)", ["bow_0", "bow_1"]),
        ("雀跃小跳 (Hop)", ["hop_0", "hop_1"]),
        ("点头打节拍 (Bob)", ["bob_0", "bob_1"]),
        ("心形翅膀 (Heart)", ["heart_wings_0", "heart_wings_1"]),
        ("独唱唱歌 (Sing)", ["sing_0", "sing_1"]),
        ("警惕拉长 (Alert)", ["alert_0"]),
        ("闪电反咬 (Bite)", ["bite_0"]),
        ("张嘴哈气 (Hiss)", ["hiss_0"]),
        ("展翅飞行 (Fly)", ["fly_0", "fly_1"]),
    ]

    cols = 5
    rows = 3
    thumb_w = 270
    thumb_h = 285
    header_h = 95
    sheet_w = cols * thumb_w + 60
    sheet_h = rows * thumb_h + header_h + 60

    sheet = Image.new("RGBA", (sheet_w, sheet_h), (242, 236, 228, 255))
    draw = ImageDraw.Draw(sheet)

    # Header title
    draw.text((40, 22), "原始灰玄凤鹦鹉 2D 像素桌宠全动作预览表", fill=(45, 40, 42, 255), font=font_main)
    draw.text((40, 58), "基于全新像素原画提取制作 | 15 类行为状态 / 27 组动画关键帧 | 存储目录: D:\\pets\\2d", fill=(110, 100, 105, 255), font=font_sub)

    for idx, (title, f_list) in enumerate(categories):
        c = idx % cols
        r = idx // cols
        bx = 30 + c * thumb_w
        by = header_h + 30 + r * thumb_h

        # Card background
        draw.rounded_rectangle([bx + 6, by + 6, bx + thumb_w - 6, by + thumb_h - 6], radius=12, fill=(255, 255, 255, 255), outline=(220, 212, 202, 255), width=2)

        # Title label
        draw.text((bx + 16, by + 14), title, fill=(50, 45, 48, 255), font=font_card)

        if len(f_list) == 1:
            draw.text((bx + thumb_w - 75, by + 16), "瞬时单帧", fill=(150, 130, 120, 255), font=font_badge)
            img = frames[f_list[0]]
            thumb = img.resize((190, 205), Image.Resampling.LANCZOS)
            sheet.paste(thumb, (bx + 40, by + 50), thumb)
        else:
            draw.text((bx + thumb_w - 75, by + 16), "双帧循环", fill=(80, 140, 190, 255), font=font_badge)
            # Show both frame 0 and frame 1 slightly overlapped or side-by-side
            img0 = frames[f_list[0]].resize((140, 150), Image.Resampling.LANCZOS)
            img1 = frames[f_list[1]].resize((140, 150), Image.Resampling.LANCZOS)
            sheet.paste(img0, (bx + 12, by + 65), img0)
            sheet.paste(img1, (bx + 118, by + 65), img1)
            draw.text((bx + 60, by + 235), "第 1 帧", fill=(160, 145, 135, 255), font=font_badge)
            draw.text((bx + 165, by + 235), "第 2 帧", fill=(160, 145, 135, 255), font=font_badge)

    sheet_path = os.path.join(BASE_DIR, "preview_sheet.png")
    sheet.save(sheet_path)
    print(f"Master preview sheet saved to: {sheet_path}")

def generate_html_preview():
    """生成一个可以直接在浏览器里查看所有动作流畅播放的预览网页"""
    html_content = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<title>🐤 玄凤鹦鹉 2D 像素桌宠素材动态预览器</title>
<style>
  body {
    margin: 0;
    padding: 24px;
    background: #f4ede4;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Microsoft YaHei", sans-serif;
    color: #333;
  }
  h1 { margin: 0 0 8px; color: #2c2523; font-size: 24px; }
  p.subtitle { margin: 0 0 24px; color: #7a6e65; font-size: 14px; }
  .grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
    gap: 16px;
  }
  .card {
    background: #fff;
    border-radius: 12px;
    padding: 16px;
    box-shadow: 0 4px 12px rgba(0,0,0,0.05);
    text-align: center;
    border: 1px solid #e8ded4;
    transition: transform 0.2s;
  }
  .card:hover { transform: translateY(-3px); }
  .card-title {
    font-weight: bold;
    font-size: 15px;
    margin-bottom: 12px;
    color: #4a3f35;
  }
  .preview-box {
    width: 180px;
    height: 195px;
    margin: 0 auto;
    position: relative;
    background: radial-gradient(circle, #faf6f0 40%, #ede3d5 100%);
    border-radius: 8px;
    display: flex;
    align-items: center;
    justify-content: center;
    overflow: hidden;
  }
  .preview-box img {
    max-width: 100%;
    max-height: 100%;
    image-rendering: auto;
  }
  .badge {
    font-size: 11px;
    color: #8c7b6d;
    margin-top: 8px;
  }
  .controls {
    margin-bottom: 20px;
    background: #fff;
    padding: 12px 18px;
    border-radius: 8px;
    display: inline-block;
  }
  .btn {
    background: #e8ded4;
    border: none;
    padding: 6px 14px;
    border-radius: 6px;
    cursor: pointer;
    font-size: 13px;
    margin-right: 8px;
  }
  .btn:hover { background: #d8ceC4; }
  .flipped img { transform: scaleX(-1); }
</style>
</head>
<body>
  <h1>🐤 原始灰玄凤鹦鹉 2D 素材动态预览器</h1>
  <p class="subtitle">素材保存路径：<code>D:\\pets\\2d\\sprites\\</code> | 点击右上方按钮可切换朝向测试</p>

  <div class="controls">
    <button class="btn" onclick="toggleFlip()">🔄 水平镜像翻转 (测试左右走动)</button>
    <button class="btn" onclick="toggleSpeed(1)">1x 正常速度</button>
    <button class="btn" onclick="toggleSpeed(0.5)">0.5x 慢速慢放</button>
  </div>

  <div class="grid" id="grid"></div>

<script>
const data = [
  { title: "发呆眨眼 (Idle)", frames: ["idle_0", "idle_1"], interval: 400 },
  { title: "摇晃溜达 (Waddle)", frames: ["waddle_0", "waddle_1"], interval: 200 },
  { title: "啄啄桌面 (Peck)", frames: ["peck_0", "peck_1"], interval: 180 },
  { title: "拆家啃咬 (Chew)", frames: ["chew_0", "chew_1"], interval: 160 },
  { title: "蓬成毛球 (Fluff)", frames: ["fluff_0", "fluff_1"], interval: 350 },
  { title: "理理羽毛 (Preen)", frames: ["preen_0", "preen_1"], interval: 300 },
  { title: "低头求摸 (Bow)", frames: ["bow_0", "bow_1"], interval: 320 },
  { title: "雀跃小跳 (Hop)", frames: ["hop_0", "hop_1"], interval: 180 },
  { title: "打节拍点头 (Bob)", frames: ["bob_0", "bob_1"], interval: 160 },
  { title: "心形翅膀 (Heart)", frames: ["heart_wings_0", "heart_wings_1"], interval: 240 },
  { title: "独唱唱歌 (Sing)", frames: ["sing_0", "sing_1"], interval: 220 },
  { title: "警惕拉长 (Alert)", frames: ["alert_0"], interval: 1000 },
  { title: "闪电反咬 (Bite)", frames: ["bite_0"], interval: 1000 },
  { title: "张嘴哈气 (Hiss)", frames: ["hiss_0"], interval: 1000 },
  { title: "展翅飞行 (Fly)", frames: ["fly_0", "fly_1"], interval: 140 },
];

let speedMultiplier = 1.0;
let isFlipped = false;

function buildUI() {
  const grid = document.getElementById("grid");
  grid.innerHTML = "";
  data.forEach((item, idx) => {
    const card = document.createElement("div");
    card.className = "card" + (isFlipped ? " flipped" : "");
    card.innerHTML = `
      <div class="card-title">${item.title}</div>
      <div class="preview-box">
        <img id="img-${idx}" src="sprites/${item.frames[0]}.png" />
      </div>
      <div class="badge">${item.frames.length > 1 ? item.frames.length + " 帧循环动画" : "单帧瞬时姿态"}</div>
    `;
    grid.appendChild(card);

    if (item.frames.length > 1) {
      let cur = 0;
      setInterval(() => {
        cur = (cur + 1) % item.frames.length;
        const imgEl = document.getElementById(`img-${idx}`);
        if (imgEl) imgEl.src = `sprites/${item.frames[cur]}.png`;
      }, item.interval / speedMultiplier);
    }
  });
}

function toggleFlip() {
  isFlipped = !isFlipped;
  document.querySelectorAll('.card').forEach(el => {
    el.classList.toggle('flipped', isFlipped);
  });
}

function toggleSpeed(s) {
  speedMultiplier = s;
  buildUI();
}

buildUI();
</script>
</body>
</html>
"""
    html_path = os.path.join(BASE_DIR, "preview.html")
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html_content)
    print(f"Interactive preview HTML generated: {html_path}")

if __name__ == "__main__":
    generate_all_2d()
    print("All 2D assets generated successfully!")
