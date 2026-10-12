import os
import math
from PIL import Image, ImageDraw, ImageFont

BASE_DIR = r"D:\pets\2d"
POSES_DIR = os.path.join(BASE_DIR, "official_poses")
SPRITES_DIR = os.path.join(BASE_DIR, "sprites")
os.makedirs(SPRITES_DIR, exist_ok=True)

# Standardized Canvas Dimensions
CANVAS_W = 320
CANVAS_H = 300
GROUND_Y = 250  # Feet baseline Y

# Colors
C_DARK = (28, 24, 26, 255)
C_CRUMB = (205, 160, 115, 255)
C_NOTE = (90, 185, 255, 255)

def create_canvas():
    return Image.new("RGBA", (CANVAS_W, CANVAS_H), (0, 0, 0, 0))

# Load base sprite and flip to Face Right to match all 8 new poses
base_left = Image.open(os.path.join(BASE_DIR, "base.png")).convert("RGBA")
base_right = base_left.transpose(Image.Transpose.FLIP_LEFT_RIGHT)
base_right.save(os.path.join(BASE_DIR, "base_facing_right.png"))

def clean_sprite(img):
    w, h = img.size
    visited = set()
    components = []
    fg = set()
    for y in range(h):
        for x in range(w):
            if img.getpixel((x, y))[3] > 20:
                fg.add((x, y))
    for pt in fg:
        if pt in visited:
            continue
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
    # Keep components with at least 500 pixels (the main body)
    keep_pixels = set()
    for c in components:
        if len(c) >= 500:
            keep_pixels.update(c)
    cleaned = img.copy()
    for y in range(h):
        for x in range(w):
            if (x, y) not in keep_pixels and img.getpixel((x, y))[3] > 0:
                cleaned.putpixel((x, y), (0, 0, 0, 0))
    return cleaned

# Load 8 official poses
raw_poses = {
    "eating": Image.open(os.path.join(POSES_DIR, "01_eating_啄地取食.png")).convert("RGBA"),
    "sleeping": Image.open(os.path.join(POSES_DIR, "02_sleeping_闭目睡觉.png")).convert("RGBA"),
    "fluffy": Image.open(os.path.join(POSES_DIR, "03_fluffy_毛发蓬松.png")).convert("RGBA"),
    "preening": Image.open(os.path.join(POSES_DIR, "04_preening_整理羽毛.png")).convert("RGBA"),
    "bowing": Image.open(os.path.join(POSES_DIR, "05_bowing_低头求摸.png")).convert("RGBA"),
    "alert": Image.open(os.path.join(POSES_DIR, "06_alert_警觉.png")).convert("RGBA"),
    "hissing": Image.open(os.path.join(POSES_DIR, "07_hissing_哈气.png")).convert("RGBA"),
    "flying": Image.open(os.path.join(POSES_DIR, "08_flying_飞行.png")).convert("RGBA"),
}
poses = {k: clean_sprite(v) for k, v in raw_poses.items()}

# Helper to place a sprite so its bottom sits on GROUND_Y, centered in X
def place_on_ground(sprite, offset_x=0, offset_y=0, scale=1.0):
    c = create_canvas()
    w, h = sprite.size
    if scale != 1.0:
        nw, nh = int(round(w * scale)), int(round(h * scale))
        sprite = sprite.resize((nw, nh), Image.Resampling.LANCZOS)
        w, h = nw, nh
    x = int((CANVAS_W - w) / 2 + offset_x)
    y = int(GROUND_Y - h + offset_y)
    c.paste(sprite, (x, y), sprite)
    return c

# Scale factor for base_right so it matches the official sheet scale (~0.44x)
scale_base = 0.45
base_scaled = base_right.resize((int(base_right.width * scale_base), int(base_right.height * scale_base)), Image.Resampling.LANCZOS)

# Build all 27 frames
frames = {}

# 1. IDLE (日常站立 & 官方闭目睡觉)
frames["idle_0"] = place_on_ground(base_scaled, offset_x=-10)
frames["idle_1"] = place_on_ground(poses["sleeping"], offset_x=0)

# 2. WADDLE (走来走去迈步小碎步)
frames["waddle_0"] = place_on_ground(base_scaled, offset_x=-10, offset_y=-4)
frames["waddle_1"] = place_on_ground(base_scaled, offset_x=-6, offset_y=2)

# 3. PECK (官方啄地取食 Eating)
frames["peck_0"] = place_on_ground(poses["bowing"], offset_x=0)
frames["peck_1"] = place_on_ground(poses["eating"], offset_x=10)

# 4. MISCHIEF CHEW (啃咬拆家带碎屑)
chew_c0 = place_on_ground(poses["eating"], offset_x=10)
chew_c1 = place_on_ground(poses["eating"], offset_x=10)
draw = ImageDraw.Draw(chew_c1)
# Add crumbs at beak (front right)
crumbs = [(260, 240, 6), (275, 230, 5), (280, 248, 7), (265, 255, 5)]
for cx, cy, sz in crumbs:
    draw.rectangle([cx, cy, cx + sz, cy + sz], fill=C_CRUMB, outline=C_DARK)
frames["chew_0"] = chew_c0
frames["chew_1"] = chew_c1

# 5. COMFORT FLUFF (官方毛发蓬松 Fluffy Borb)
frames["fluff_0"] = place_on_ground(poses["sleeping"], offset_x=0)
frames["fluff_1"] = place_on_ground(poses["fluffy"], offset_x=0)

# 6. COMFORT PREEN (官方整理羽毛 Preening)
frames["preen_0"] = place_on_ground(base_scaled, offset_x=-10)
frames["preen_1"] = place_on_ground(poses["preening"], offset_x=0)

# 7. COMFORT BOW (官方低头求摸 Head Bowing)
frames["bow_0"] = place_on_ground(poses["sleeping"], offset_x=0)
frames["bow_1"] = place_on_ground(poses["bowing"], offset_x=0)

# 8. EXCITE HOP (雀跃小跳)
frames["hop_0"] = place_on_ground(base_scaled, offset_x=-10)
frames["hop_1"] = place_on_ground(base_scaled, offset_x=-10, offset_y=-35) # 腾空 35px

# 9. EXCITE BOB (点头打节拍狂魔)
frames["bob_0"] = place_on_ground(base_scaled, offset_x=-10, offset_y=10)
frames["bob_1"] = place_on_ground(poses["alert"], offset_x=0, offset_y=-10)

# 10. EXCITE HEART WINGS (心形翅膀自嗨)
hw0 = base_scaled.copy()
frames["heart_wings_0"] = place_on_ground(hw0, offset_x=-10)
frames["heart_wings_1"] = place_on_ground(poses["fluffy"], offset_x=0)

# 11. EXCITE SING (唱歌独奏飘音符)
sing0 = place_on_ground(poses["alert"], offset_x=0)
sing1 = place_on_ground(poses["alert"], offset_x=0)
draw_sing = ImageDraw.Draw(sing1)
# Note above head
nx, ny = 220, 45
draw_sing.ellipse([nx, ny + 12, nx + 14, ny + 22], fill=C_NOTE, outline=C_DARK, width=2)
draw_sing.ellipse([nx + 20, ny + 8, nx + 34, ny + 18], fill=C_NOTE, outline=C_DARK, width=2)
draw_sing.line([(nx + 11, ny + 15), (nx + 11, ny)], fill=C_DARK, width=3)
draw_sing.line([(nx + 31, ny + 11), (nx + 31, ny - 4)], fill=C_DARK, width=3)
draw_sing.line([(nx + 11, ny), (nx + 31, ny - 4)], fill=C_DARK, width=4)
frames["sing_0"] = sing0
frames["sing_1"] = sing1

# 12. FRIGHT ALERT (官方警觉 Alert)
frames["alert_0"] = place_on_ground(poses["alert"], offset_x=0)

# 13. FRIGHT BITE (闪电反咬)
frames["bite_0"] = place_on_ground(poses["hissing"], offset_x=25) # 身体前冲

# 14. FRIGHT HISS (官方哈气 Hissing)
frames["hiss_0"] = place_on_ground(poses["hissing"], offset_x=0)

# 15. FLY (官方飞行 Flying)
frames["fly_0"] = place_on_ground(poses["flying"], offset_x=0, offset_y=-30) # 高飞
# Frame 1: flap glide
fly1 = poses["flying"].copy()
frames["fly_1"] = place_on_ground(fly1, offset_x=0, offset_y=-10)

# Save all frames to D:\pets\2d\sprites\
for fname, img in frames.items():
    out_path = os.path.join(SPRITES_DIR, f"{fname}.png")
    img.save(out_path)
    print(f"Saved sprite: {out_path}")

# -------------------------------------------------------------
# Generate Master Contact Sheet with Official Poses
# -------------------------------------------------------------
def make_contact_sheet():
    font_path = r"C:\Windows\Fonts\msyh.ttc"
    try:
        font_main = ImageFont.truetype(font_path, 22)
        font_sub = ImageFont.truetype(font_path, 13)
        font_card = ImageFont.truetype(font_path, 14)
        font_badge = ImageFont.truetype(font_path, 11)
    except Exception:
        font_main = font_sub = font_card = font_badge = ImageFont.load_default()

    categories = [
        ("发呆眨眼 (Idle/Sleep)", ["idle_0", "idle_1"], "官方闭目睡觉"),
        ("走来走去 (Waddle)", ["waddle_0", "waddle_1"], "动态迈步巡逻"),
        ("啄啄桌面 (Peck)", ["peck_0", "peck_1"], "官方啄地取食"),
        ("啃咬拆家 (Chew)", ["chew_0", "chew_1"], "碎屑飞扬特效"),
        ("蓬成毛球 (Fluff)", ["fluff_0", "fluff_1"], "官方毛发蓬松"),
        ("理理羽毛 (Preen)", ["preen_0", "preen_1"], "官方整理羽毛"),
        ("低头求摸 (Bow)", ["bow_0", "bow_1"], "官方低头求摸"),
        ("雀跃小跳 (Hop)", ["hop_0", "hop_1"], "腾空起跳动作"),
        ("点头打节拍 (Bob)", ["bob_0", "bob_1"], "上下剧烈打点"),
        ("心形翅膀 (Heart)", ["heart_wings_0", "heart_wings_1"], "膨胀自嗨姿态"),
        ("独唱唱歌 (Sing)", ["sing_0", "sing_1"], "张嘴飘扬音符"),
        ("警惕拉长 (Alert)", ["alert_0"], "官方警觉姿态"),
        ("闪电反咬 (Bite)", ["bite_0"], "前冲反咬鼠标"),
        ("张嘴哈气 (Hiss)", ["hiss_0"], "官方哈气威慑"),
        ("展翅飞行 (Fly)", ["fly_0", "fly_1"], "官方展翅飞翔"),
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

    # Title
    draw.text((40, 22), "原始灰玄凤鹦鹉 2D 像素桌宠全新官方动作总览表", fill=(45, 40, 42, 255), font=font_main)
    draw.text((40, 58), "全面融合 8 组官方手绘像素姿态 (啄地/闭目/蓬毛/理毛/低头/警觉/哈气/飞行) | 目录: D:\\pets\\2d", fill=(110, 100, 105, 255), font=font_sub)

    for idx, (title, f_list, tag) in enumerate(categories):
        c = idx % cols
        r = idx // cols
        bx = 30 + c * thumb_w
        by = header_h + 30 + r * thumb_h

        draw.rounded_rectangle([bx + 6, by + 6, bx + thumb_w - 6, by + thumb_h - 6], radius=12, fill=(255, 255, 255, 255), outline=(220, 212, 202, 255), width=2)
        draw.text((bx + 16, by + 14), title, fill=(50, 45, 48, 255), font=font_card)

        # Badge
        badge_color = (190, 80, 60, 255) if "官方" in tag else (70, 130, 180, 255)
        draw.text((bx + thumb_w - 85, by + 16), tag, fill=badge_color, font=font_badge)

        if len(f_list) == 1:
            img = frames[f_list[0]].resize((190, 180), Image.Resampling.LANCZOS)
            sheet.paste(img, (bx + 40, by + 55), img)
        else:
            img0 = frames[f_list[0]].resize((135, 128), Image.Resampling.LANCZOS)
            img1 = frames[f_list[1]].resize((135, 128), Image.Resampling.LANCZOS)
            sheet.paste(img0, (bx + 10, by + 75), img0)
            sheet.paste(img1, (bx + 125, by + 75), img1)
            draw.text((bx + 55, by + 235), "第 1 帧", fill=(160, 145, 135, 255), font=font_badge)
            draw.text((bx + 170, by + 235), "第 2 帧", fill=(160, 145, 135, 255), font=font_badge)

    sheet_path = os.path.join(BASE_DIR, "preview_sheet.png")
    sheet.save(sheet_path)
    print(f"Master preview sheet saved to: {sheet_path}")

make_contact_sheet()

# -------------------------------------------------------------
# Generate Interactive Looping Web Preview
# -------------------------------------------------------------
html_content = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<title>🐤 玄凤鹦鹉 官方多姿态动态预览器</title>
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
    grid-template-columns: repeat(auto-fill, minmax(230px, 1fr));
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
    margin-bottom: 8px;
    color: #4a3f35;
  }
  .tag {
    display: inline-block;
    padding: 2px 8px;
    border-radius: 4px;
    font-size: 11px;
    margin-bottom: 10px;
  }
  .tag-official { background: #fae4df; color: #b8402c; }
  .tag-dynamic { background: #e0eef8; color: #2c6eb8; }
  .preview-box {
    width: 200px;
    height: 190px;
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
  <h1>🐤 原始灰玄凤鹦鹉 官方多姿态动态预览器</h1>
  <p class="subtitle">已完全融合 8 组官方像素原画姿态 | 路径：<code>D:\\pets\\2d\\sprites\\</code></p>

  <div class="controls">
    <button class="btn" onclick="toggleFlip()">🔄 水平镜像翻转 (测试左右走动)</button>
    <button class="btn" onclick="toggleSpeed(1)">1x 正常播放</button>
    <button class="btn" onclick="toggleSpeed(0.5)">0.5x 慢动作</button>
  </div>

  <div class="grid" id="grid"></div>

<script>
const data = [
  { title: "发呆眨眼 (Idle/Sleep)", frames: ["idle_0", "idle_1"], interval: 450, tag: "官方闭目睡觉" },
  { title: "摇晃溜达 (Waddle)", frames: ["waddle_0", "waddle_1"], interval: 200, tag: "迈步巡逻" },
  { title: "啄地取食 (Peck/Eat)", frames: ["peck_0", "peck_1"], interval: 220, tag: "官方啄地取食" },
  { title: "拆家啃咬 (Chew)", frames: ["chew_0", "chew_1"], interval: 160, tag: "碎屑飞扬" },
  { title: "毛发蓬松 (Fluffy Borb)", frames: ["fluff_0", "fluff_1"], interval: 350, tag: "官方毛发蓬松" },
  { title: "整理羽毛 (Preen)", frames: ["preen_0", "preen_1"], interval: 300, tag: "官方整理羽毛" },
  { title: "低头求摸 (Head Bow)", frames: ["bow_0", "bow_1"], interval: 320, tag: "官方低头求摸" },
  { title: "雀跃小跳 (Hop)", frames: ["hop_0", "hop_1"], interval: 180, tag: "腾空小跳" },
  { title: "打节拍点头 (Bob)", frames: ["bob_0", "bob_1"], interval: 160, tag: "剧烈点头" },
  { title: "心形翅膀 (Heart Wings)", frames: ["heart_wings_0", "heart_wings_1"], interval: 240, tag: "求偶自嗨" },
  { title: "独唱唱歌 (Sing)", frames: ["sing_0", "sing_1"], interval: 220, tag: "飞舞音符" },
  { title: "警觉拉长 (Alert)", frames: ["alert_0"], interval: 1000, tag: "官方警觉姿态" },
  { title: "闪电反咬 (Bite)", frames: ["bite_0"], interval: 1000, tag: "前冲反咬" },
  { title: "张嘴哈气 (Hiss)", frames: ["hiss_0"], interval: 1000, tag: "官方张嘴哈气" },
  { title: "展翅飞行 (Fly)", frames: ["fly_0", "fly_1"], interval: 140, tag: "官方展翅飞行" },
];

let speedMultiplier = 1.0;
let isFlipped = false;

function buildUI() {
  const grid = document.getElementById("grid");
  grid.innerHTML = "";
  data.forEach((item, idx) => {
    const isOff = item.tag.includes("官方");
    const card = document.createElement("div");
    card.className = "card" + (isFlipped ? " flipped" : "");
    card.innerHTML = `
      <div class="card-title">${item.title}</div>
      <div class="tag ${isOff ? 'tag-official' : 'tag-dynamic'}">${item.tag}</div>
      <div class="preview-box">
        <img id="img-${idx}" src="sprites/${item.frames[0]}.png" />
      </div>
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

with open(os.path.join(BASE_DIR, "preview.html"), "w", encoding="utf-8") as f:
    f.write(html_content)

print("Integration complete! Preview files ready.")
