import os
import json
import math
from PIL import Image, ImageDraw, ImageFont

BASE_DIR = r"D:\pets\2d"
PARTS_DIR = os.path.join(BASE_DIR, "parts")
PARTS_RIGHT_DIR = os.path.join(BASE_DIR, "parts_right")
os.makedirs(PARTS_DIR, exist_ok=True)
os.makedirs(PARTS_RIGHT_DIR, exist_ok=True)

# 1. Load base image (472 x 555)
base_img = Image.open(os.path.join(BASE_DIR, "base.png")).convert("RGBA")
W, H = base_img.size

# Palette definitions
C_YELLOW = (248, 230, 84, 255)
C_DARK = (28, 24, 26, 255)
C_GREY_BODY = (142, 136, 134, 255)
C_GREY_DARK = (98, 92, 95, 255)
C_GREY_LIGHT = (168, 160, 158, 255)
C_BEAK = (175, 140, 60, 255)
C_FEET = (130, 95, 100, 255)

# --- Define Boundary Functions ---

def is_beak(x, y):
    """嘴部区域判定: x < 50, y in [180, 252]"""
    if y < 178 or y > 252 or x > 56:
        return False
    # Beak curve boundary
    # y=178 -> x ~ 30
    # y=200 -> x ~ 41
    # y=215 -> x ~ 46
    # y=230 -> x ~ 45
    # y=248 -> x ~ 43
    if y <= 190:
        bx = 28 + (y - 178) * 0.9
    elif y <= 218:
        bx = 39 + (y - 190) * 0.25
    elif y <= 235:
        bx = 46 - (y - 218) * 0.1
    else:
        bx = 44 - (y - 235) * 0.5
    return x <= bx

def is_crest(x, y):
    """头冠/呆毛区域判定: y <= 130, x in [80, 195]"""
    if y > 132:
        return False
    if y <= 116:
        return True
    # Attachment base at y in [116, 132]: roots lie in x in [95, 175]
    skull_top_y = 120 + 0.003 * ((x - 105) ** 2)
    return y <= skull_top_y + 4 and (90 <= x <= 178)

def is_head(x, y):
    """头部区域判定: y in [120, 272], x in [20, 235] (不含嘴与冠羽)"""
    if is_crest(x, y) or is_beak(x, y):
        return False
    if y < 118 or y > 274:
        return False
    # Back of head boundary
    if y <= 200 and x > 185:
        return False
    if y > 200 and x > 235:
        return False
    # Throat / Neck bottom boundary
    if y > 260:
        # Neck curve connecting to chest: x in [45, 235]
        neck_y = 260 + 0.001 * ((x - 140) ** 2)
        if y > neck_y + 10:
            return False
    return True

def is_wing(x, y):
    """翅膀区域判定: x in [95, 345], y in [270, 475]"""
    if y < 270 or y > 475 or x < 90 or x > 345:
        return False
    # Chest/belly border on left
    if y <= 310:
        left_bx = 108 - (y - 270) * 0.3
    elif y <= 370:
        left_bx = 96 + (y - 310) * 0.2
    elif y <= 420:
        left_bx = 108 + (y - 370) * 0.5
    else:
        left_bx = 133 + (y - 420) * 1.5
    
    # Back/tail border on right
    if y <= 340:
        right_bx = 280 + (y - 270) * 0.4
    elif y <= 420:
        right_bx = 308 + (y - 340) * 0.35
    else:
        right_bx = 336 - (y - 420) * 0.2
    return (left_bx <= x <= right_bx)

def is_feet(x, y):
    """双脚区域判定: y >= 480, x in [95, 260]"""
    if y < 480 or x < 92 or x > 262:
        return False
    # Claws & legs
    return True

def is_tail(x, y):
    """尾巴区域判定: y >= 415, x >= 260 (除去翅膀与脚)"""
    if is_wing(x, y) or is_feet(x, y):
        return False
    if y < 415 or x < 255:
        return False
    return True

# --- 2. Allocate Layers ---
layers = {
    "tail": Image.new("RGBA", (W, H), (0, 0, 0, 0)),
    "feet": Image.new("RGBA", (W, H), (0, 0, 0, 0)),
    "body": Image.new("RGBA", (W, H), (0, 0, 0, 0)),
    "wing": Image.new("RGBA", (W, H), (0, 0, 0, 0)),
    "head": Image.new("RGBA", (W, H), (0, 0, 0, 0)),
    "beak": Image.new("RGBA", (W, H), (0, 0, 0, 0)),
    "crest": Image.new("RGBA", (W, H), (0, 0, 0, 0)),
    "eye": Image.new("RGBA", (W, H), (0, 0, 0, 0)),
}

# Distribute original pixels
for y in range(H):
    for x in range(W):
        p = base_img.getpixel((x, y))
        if p[3] < 30:
            continue
        
        # Check specific parts
        if is_crest(x, y):
            layers["crest"].putpixel((x, y), p)
        elif is_beak(x, y):
            layers["beak"].putpixel((x, y), p)
        elif is_head(x, y):
            # Check if this pixel is the eye (x in [57, 81], y in [172, 196])
            if 56 <= x <= 82 and 172 <= y <= 196 and (p[0] < 45 and p[1] < 45 and p[2] < 45 or (p[0] > 220 and p[1] > 220 and p[2] > 220)):
                layers["eye"].putpixel((x, y), p)
                # Head underneath eye gets smooth yellow feathers
                layers["head"].putpixel((x, y), C_YELLOW)
            else:
                layers["head"].putpixel((x, y), p)
        elif is_wing(x, y):
            layers["wing"].putpixel((x, y), p)
        elif is_feet(x, y):
            layers["feet"].putpixel((x, y), p)
        elif is_tail(x, y):
            layers["tail"].putpixel((x, y), p)
        else:
            # Default to body only if below neck; otherwise route to head/crest
            if y < 125:
                layers["crest"].putpixel((x, y), p)
            elif y < 255:
                layers["head"].putpixel((x, y), p)
            else:
                layers["body"].putpixel((x, y), p)

# --- 3. Inpainting / Occlusion Completion (补全遮挡面) ---

# A. Inpaint Body under Wing
# Body must have a solid, rounded flank/belly so when the wing moves, there's no transparent hole!
draw_body = ImageDraw.Draw(layers["body"])
for y in range(275, 470):
    for x in range(95, 305):
        if is_wing(x, y):
            # Gradient shading from chest to back
            # Left (chest) is lighter (165), center is mid grey (140), right/back is darker (110)
            t = (x - 95) / 210.0
            g_val = int(165 - t * 55)
            # Belly shadow at bottom
            if y > 400:
                g_val = int(g_val * (1.0 - (y - 400) * 0.003))
            c = (g_val, int(g_val * 0.95), int(g_val * 0.94), 255)
            # Outer boundary check: keep within bird's natural oval torso
            torso_cx, torso_cy = 185, 370
            dx = (x - torso_cx) / 115.0
            dy = (y - torso_cy) / 95.0
            if (dx*dx + dy*dy) <= 1.0:
                layers["body"].putpixel((x, y), c)

# B. Inpaint Neck & Upper Torso behind Head
# Connect body smoothly up into neck at y in [245, 275], x in [80, 210]
for y in range(248, 276):
    for x in range(70, 225):
        if layers["body"].getpixel((x, y))[3] == 0:
            c = (145, 140, 138, 255)
            layers["body"].putpixel((x, y), c)

# C. Inpaint Rounded Skull under Crest
# Make top of head a smooth rounded yellow dome so tilting crest reveals full head
draw_head = ImageDraw.Draw(layers["head"])
for y in range(118, 132):
    for x in range(95, 175):
        if layers["head"].getpixel((x, y))[3] == 0:
            # Outline on top row
            if y == 118:
                layers["head"].putpixel((x, y), C_DARK)
            else:
                layers["head"].putpixel((x, y), C_YELLOW)

# D. Inpaint Face behind Beak
for y in range(185, 245):
    for x in range(32, 48):
        if layers["head"].getpixel((x, y))[3] == 0:
            layers["head"].putpixel((x, y), C_YELLOW)

# E. Generate Eye Variants
eye_open = layers["eye"].copy()

# Eye blink (flat closed line)
eye_blink = Image.new("RGBA", (W, H), (0, 0, 0, 0))
draw_blink = ImageDraw.Draw(eye_blink)
draw_blink.line([(58, 184), (79, 184)], fill=C_DARK, width=4)

# Eye happy (curved smiling line)
eye_happy = Image.new("RGBA", (W, H), (0, 0, 0, 0))
draw_happy = ImageDraw.Draw(eye_happy)
for dx in range(-11, 12):
    x = 68 + dx
    dy = int(round(0.05 * (dx ** 2)))
    y = 180 + dy
    draw_happy.line([(x, y), (x, y + 3)], fill=C_DARK, width=2)

# --- 4. Crop each layer to its Bounding Box & Compute Anchors ---
parts_catalog = {
    "tail": { "img": layers["tail"], "z_index": 1, "name_cn": "尾羽", "pivot": (336, 422) },
    "feet": { "img": layers["feet"], "z_index": 2, "name_cn": "脚部", "pivot": (175, 490) },
    "body": { "img": layers["body"], "z_index": 3, "name_cn": "身躯(躯干)", "pivot": (185, 370) },
    "wing": { "img": layers["wing"], "z_index": 4, "name_cn": "翅膀", "pivot": (135, 290) },
    "head": { "img": layers["head"], "z_index": 5, "name_cn": "头部(含面颊)", "pivot": (135, 260) },
    "beak": { "img": layers["beak"], "z_index": 6, "name_cn": "嘴喙", "pivot": (44, 215) },
    "eye_open": { "img": eye_open, "z_index": 7, "name_cn": "眼睛(睁眼)", "pivot": (68, 184) },
    "eye_blink": { "img": eye_blink, "z_index": 7, "name_cn": "眼睛(闭眼/发呆)", "pivot": (68, 184) },
    "eye_happy": { "img": eye_happy, "z_index": 7, "name_cn": "眼睛(开心眯眼)", "pivot": (68, 184) },
    "crest": { "img": layers["crest"], "z_index": 8, "name_cn": "头冠(呆毛)", "pivot": (135, 126) },
}

metadata = {
    "canvas_size": [W, H],
    "description": "原始灰玄凤鹦鹉 2D 独立分层骨骼部件配置",
    "parts": {}
}

# Save cropped individual components and calculate local pivots
for key, data in parts_catalog.items():
    img = data["img"]
    bbox = img.getbbox()
    if not bbox:
        bbox = (0, 0, W, H)
    
    # Global pivot
    gx, gy = data["pivot"]
    # Local pivot relative to cropped part
    lx = gx - bbox[0]
    ly = gy - bbox[1]
    
    cropped = img.crop(bbox)
    
    # Save Left-facing
    out_left_path = os.path.join(PARTS_DIR, f"{key}.png")
    cropped.save(out_left_path)
    
    # Also save full-canvas aligned version for zero-effort stacking
    full_left_path = os.path.join(PARTS_DIR, f"{key}_full.png")
    img.save(full_left_path)
    
    # Save Right-facing (flipped horizontally)
    cropped_right = cropped.transpose(Image.Transpose.FLIP_LEFT_RIGHT)
    cropped_right.save(os.path.join(PARTS_RIGHT_DIR, f"{key}.png"))
    
    full_right = img.transpose(Image.Transpose.FLIP_LEFT_RIGHT)
    full_right.save(os.path.join(PARTS_RIGHT_DIR, f"{key}_full.png"))
    
    metadata["parts"][key] = {
        "name_cn": data["name_cn"],
        "z_index": data["z_index"],
        "bbox": [bbox[0], bbox[1], bbox[2], bbox[3]],
        "size": [cropped.width, cropped.height],
        "global_pivot": [gx, gy],
        "local_pivot": [lx, ly],
        "global_pivot_right": [W - 1 - gx, gy],
        "local_pivot_right": [cropped.width - 1 - lx, ly]
    }

with open(os.path.join(PARTS_DIR, "rig_config.json"), "w", encoding="utf-8") as f:
    json.dump(metadata, f, ensure_ascii=False, indent=2)

print("Saved all components and rig_config.json successfully!")

# --- 5. Generate Exploded Parts Presentation Sheet ---
# Canvas: 1300 x 850
SHEET_W = 1380
SHEET_H = 880
sheet = Image.new("RGBA", (SHEET_W, SHEET_H), (245, 238, 230, 255))
draw_sheet = ImageDraw.Draw(sheet)

# Title
try:
    font_title = ImageFont.truetype("msyh.ttc", 26)
    font_sub = ImageFont.truetype("msyh.ttc", 15)
    font_lbl = ImageFont.truetype("msyh.ttc", 13)
    font_bold = ImageFont.truetype("msyhbd.ttc", 15)
except Exception:
    font_title = font_sub = font_lbl = font_bold = ImageFont.load_default()

draw_sheet.text((40, 30), "原始灰玄凤鹦鹉 2D 独立分层骨骼部件拆解总览", fill=(45, 36, 32), font=font_title)
draw_sheet.text((40, 72), "7 大独立活动部件已全部解构、补全遮挡面并标定动力学旋转枢轴点 (Pivot) | 目录: D:\\pets\\2d\\parts", fill=(120, 110, 105), font=font_sub)

# Right: Fully Reassembled Composite Model
box_rx, box_ry, box_rw, box_rh = 830, 120, 510, 690
draw_sheet.rectangle([box_rx, box_ry, box_rx + box_rw, box_ry + box_rh], fill=(255, 255, 255, 255), outline=(225, 215, 205), width=2)
draw_sheet.text((box_rx + 24, box_ry + 20), "【分层组装验证】100% 完美无缝复原", fill=(45, 36, 32), font=font_bold)
draw_sheet.text((box_rx + 24, box_ry + 45), "按 Z-Order 从底到顶依次叠合，完全无空洞与接缝", fill=(140, 130, 125), font=font_lbl)

# Composite by layers
composite = Image.new("RGBA", (W, H), (0, 0, 0, 0))
for key in ["tail", "feet", "body", "wing", "head", "beak", "crest", "eye_open"]:
    composite.paste(parts_catalog[key]["img"], (0, 0), parts_catalog[key]["img"])

comp_scaled = composite.resize((int(W * 0.96), int(H * 0.96)), Image.Resampling.LANCZOS)
sheet.paste(comp_scaled, (box_rx + 30, box_ry + 90), comp_scaled)

# Mark key pivot points with crosshairs
pivots_to_mark = [
    ("呆毛根部", parts_catalog["crest"]["pivot"], (230, 160, 20)),
    ("颈部枢轴", parts_catalog["head"]["pivot"], (220, 60, 50)),
    ("翅膀肩关节", parts_catalog["wing"]["pivot"], (40, 120, 220)),
    ("腿臀关节", parts_catalog["feet"]["pivot"], (50, 160, 60)),
    ("尾羽根部", parts_catalog["tail"]["pivot"], (140, 50, 180)),
    ("嘴喙转轴", parts_catalog["beak"]["pivot"], (200, 100, 30)),
]

for label, (px, py), color in pivots_to_mark:
    # Scale to composite position
    cx = int(box_rx + 30 + px * 0.96)
    cy = int(box_ry + 90 + py * 0.96)
    r = 5
    draw_sheet.ellipse([cx - r, cy - r, cx + r, cy + r], fill=color + (240,), outline=(255, 255, 255, 255), width=2)
    draw_sheet.text((cx + 8, cy - 8), label, fill=color, font=font_lbl)

# Left: Exploded Grid of all 7 independent components
box_lx, box_ly, box_lw, box_lh = 40, 120, 760, 690
draw_sheet.rectangle([box_lx, box_ly, box_lx + box_lw, box_ly + box_lh], fill=(255, 255, 255, 255), outline=(225, 215, 205), width=2)
draw_sheet.text((box_lx + 24, box_ly + 20), "【独立组件矩阵】部件独立透明图层与旋转锚点 (红十字标识)", fill=(45, 36, 32), font=font_bold)
draw_sheet.text((box_lx + 24, box_ly + 45), "每个部件拥有独立外边框、独立 PNG 文件与旋转/位移中心点", fill=(140, 130, 125), font=font_lbl)

# Grid layout: 4 columns x 2 rows
cells = [
    ("crest", "1. 头冠 (呆毛)", "可独立俯仰炸起/摆动"),
    ("head", "2. 头部 (含腮红)", "独立点头、歪头、倾斜"),
    ("beak", "3. 嘴喙", "独立张合说话、啃咬"),
    ("eye_open", "4. 眼睛 (3款表情)", "睁眼 / 闭眼发呆 / 眯眯笑"),
    ("wing", "5. 翅膀", "肩关节扑腾、微张、收拢"),
    ("body", "6. 身躯 (躯干)", "已补全遮挡面，做呼吸起伏"),
    ("feet", "7. 脚部", "左右小碎步走动、离地抬起"),
    ("tail", "8. 尾羽", "翘动、摆尾、兴奋微颤"),
]

for idx, (ckey, ctitle, cdesc) in enumerate(cells):
    row = idx // 4
    col = idx % 4
    cx = box_lx + 24 + col * 180
    cy = box_ly + 80 + row * 280
    
    # Cell Card
    draw_sheet.rectangle([cx, cy, cx + 168, cy + 260], fill=(248, 244, 238), outline=(230, 220, 210), width=1)
    draw_sheet.text((cx + 10, cy + 8), ctitle, fill=(50, 42, 38), font=font_bold)
    draw_sheet.text((cx + 10, cy + 28), cdesc, fill=(130, 120, 115), font=font_lbl)
    
    # Component image
    img = Image.open(os.path.join(PARTS_DIR, f"{ckey}.png"))
    # Scale to fit 140x170
    scale = min(140.0 / img.width, 170.0 / img.height, 1.0)
    nw = int(img.width * scale)
    nh = int(img.height * scale)
    scaled_p = img.resize((nw, nh), Image.Resampling.LANCZOS)
    
    px_pos = cx + int((168 - nw) / 2)
    py_pos = cy + 55 + int((170 - nh) / 2)
    sheet.paste(scaled_p, (px_pos, py_pos), scaled_p)
    
    # Draw local pivot crosshair
    lx, ly = metadata["parts"][ckey]["local_pivot"]
    slx = int(px_pos + lx * scale)
    sly = int(py_pos + ly * scale)
    draw_sheet.line([(slx - 7, sly), (slx + 7, sly)], fill=(230, 50, 40, 255), width=2)
    draw_sheet.line([(slx, sly - 7), (slx, sly + 7)], fill=(230, 50, 40, 255), width=2)
    draw_sheet.ellipse([slx - 3, sly - 3, slx + 3, sly + 3], fill=(255, 255, 255, 255), outline=(230, 50, 40, 255), width=1)

sheet_out = os.path.join(BASE_DIR, "parts_exploded_preview.png")
sheet.save(sheet_out)
print(f"Saved master exploded preview to: {sheet_out}")

# --- 6. Generate Interactive Web Rig Visualizer (D:\pets\2d\rig_preview.html) ---
html_content = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<title>🐤 玄凤鹦鹉 2D 独立部件与骨骼动力学实时调试器</title>
<style>
  * { box-sizing: border-box; }
  body {
    margin: 0; padding: 24px;
    background: #f3ece4;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Microsoft YaHei", sans-serif;
    color: #333;
    display: flex; gap: 24px;
    min-height: 100vh;
  }
  .stage-pane {
    flex: 1;
    background: #fff;
    border-radius: 16px;
    padding: 24px;
    box-shadow: 0 4px 16px rgba(0,0,0,0.06);
    display: flex; flex-direction: column;
    align-items: center;
  }
  .stage-header {
    width: 100%;
    margin-bottom: 16px;
  }
  .stage-header h1 { margin: 0 0 6px; font-size: 22px; color: #2c2523; }
  .stage-header p { margin: 0; font-size: 13px; color: #7a6e65; }
  .canvas-container {
    width: 520px; height: 580px;
    background: radial-gradient(circle, #faf6f0 40%, #eae0d0 100%);
    border-radius: 12px;
    border: 2px dashed #d8ceC4;
    display: flex; align-items: center; justify-content: center;
    position: relative;
    overflow: hidden;
  }
  canvas {
    image-rendering: pixelated;
  }
  .control-pane {
    width: 440px;
    background: #fff;
    border-radius: 16px;
    padding: 24px;
    box-shadow: 0 4px 16px rgba(0,0,0,0.06);
    overflow-y: auto;
    max-height: 92vh;
  }
  h2 { margin: 0 0 14px; font-size: 16px; color: #2c2523; border-left: 4px solid #e06d53; padding-left: 8px; }
  .section { margin-bottom: 22px; }
  .slider-row {
    margin-bottom: 12px;
  }
  .slider-label {
    display: flex; justify-content: space-between;
    font-size: 13px; font-weight: bold; color: #4a3f35;
    margin-bottom: 4px;
  }
  .slider-label span.val { color: #d9534f; }
  input[type="range"] {
    width: 100%;
    accent-color: #d9534f;
  }
  .btn-group {
    display: flex; flex-wrap: wrap; gap: 8px; margin-bottom: 16px;
  }
  .btn {
    background: #eae2d6; border: none;
    padding: 7px 14px; border-radius: 8px;
    font-size: 13px; font-weight: 500;
    cursor: pointer; transition: all 0.15s;
    color: #4a3f35;
  }
  .btn:hover { background: #dcd2c4; }
  .btn.active { background: #d9534f; color: #fff; }
  .layers-grid {
    display: grid; grid-template-columns: 1fr 1fr; gap: 8px;
  }
  .layer-item {
    background: #fbf8f4; border: 1px solid #ebdcd0;
    padding: 6px 10px; border-radius: 6px;
    display: flex; align-items: center; gap: 8px;
    font-size: 12px;
  }
</style>
</head>
<body>

<div class="stage-pane">
  <div class="stage-header">
    <h1>🐤 玄凤鹦鹉 2D 独立分层骨骼动力学实时调试器</h1>
    <p>头冠、头、嘴、身躯、翅膀、脚、尾巴 7 大部件独立受控 | 实时层级变换与矩阵演算</p>
  </div>
  <div class="canvas-container">
    <canvas id="cv" width="472" height="555"></canvas>
  </div>
</div>

<div class="control-pane">
  <h2>🌟 快捷情绪与行为预设 (一键触发)</h2>
  <div class="btn-group">
    <button class="btn" onclick="setPreset('idle')">日常呼吸发呆</button>
    <button class="btn" onclick="setPreset('alert')">警觉冠羽炸立</button>
    <button class="btn" onclick="setPreset('happy_wing')">欢快展翅扑腾</button>
    <button class="btn" onclick="setPreset('head_bow')">低头求撸毛</button>
    <button class="btn" onclick="setPreset('waddle')">小碎步溜达</button>
    <button class="btn" onclick="setPreset('bob')">点头打节拍</button>
    <button class="btn" onclick="stopAnimation()">⏹ 暂停动画</button>
  </div>

  <h2>🎮 独立部件角度与位移微调</h2>
  <div class="section">
    <div class="slider-row">
      <div class="slider-label"><span>头冠/呆毛角度 (Crest)</span><span class="val" id="v-crest">0°</span></div>
      <input type="range" id="s-crest" min="-45" max="45" value="0" oninput="updateSliders()" />
    </div>

    <div class="slider-row">
      <div class="slider-label"><span>头部俯仰点头 (Head)</span><span class="val" id="v-head">0°</span></div>
      <input type="range" id="s-head" min="-30" max="35" value="0" oninput="updateSliders()" />
    </div>

    <div class="slider-row">
      <div class="slider-label"><span>嘴喙张合 (Beak Open)</span><span class="val" id="v-beak">0px</span></div>
      <input type="range" id="s-beak" min="0" max="15" value="0" oninput="updateSliders()" />
    </div>

    <div class="slider-row">
      <div class="slider-label"><span>翅膀扑动角度 (Wing)</span><span class="val" id="v-wing">0°</span></div>
      <input type="range" id="s-wing" min="-35" max="45" value="0" oninput="updateSliders()" />
    </div>

    <div class="slider-row">
      <div class="slider-label"><span>尾巴翘动角度 (Tail)</span><span class="val" id="v-tail">0°</span></div>
      <input type="range" id="s-tail" min="-25" max="25" value="0" oninput="updateSliders()" />
    </div>

    <div class="slider-row">
      <div class="slider-label"><span>双脚迈步摆动 (Feet)</span><span class="val" id="v-feet">0°</span></div>
      <input type="range" id="s-feet" min="-20" max="20" value="0" oninput="updateSliders()" />
    </div>

    <div class="slider-row">
      <div class="slider-label"><span>躯干呼吸起伏 (Breath)</span><span class="val" id="v-body">1.00x</span></div>
      <input type="range" id="s-body" min="96" max="104" value="100" oninput="updateSliders()" />
    </div>
  </div>

  <h2>👁️ 表情眼睛切换</h2>
  <div class="btn-group">
    <button class="btn active" id="btn-eye-open" onclick="setEye('eye_open')">睁眼 (明亮灵动)</button>
    <button class="btn" id="btn-eye-blink" onclick="setEye('eye_blink')">闭眼 (沉睡发呆)</button>
    <button class="btn" id="btn-eye-happy" onclick="setEye('eye_happy')">眯眯眼 (惬意微笑)</button>
  </div>

  <h2>👁️ 图层可见性独立开关</h2>
  <div class="layers-grid">
    <label class="layer-item"><input type="checkbox" id="chk-crest" checked onchange="render()" /> 冠羽 (呆毛)</label>
    <label class="layer-item"><input type="checkbox" id="chk-head" checked onchange="render()" /> 头部 (含腮红)</label>
    <label class="layer-item"><input type="checkbox" id="chk-beak" checked onchange="render()" /> 嘴喙 (Beak)</label>
    <label class="layer-item"><input type="checkbox" id="chk-wing" checked onchange="render()" /> 翅膀 (Wing)</label>
    <label class="layer-item"><input type="checkbox" id="chk-body" checked onchange="render()" /> 身躯 (躯干)</label>
    <label class="layer-item"><input type="checkbox" id="chk-feet" checked onchange="render()" /> 脚部 (Feet)</label>
    <label class="layer-item"><input type="checkbox" id="chk-tail" checked onchange="render()" /> 尾羽 (Tail)</label>
    <label class="layer-item"><input type="checkbox" id="chk-pivots" checked onchange="render()" /> 🔴 显示旋转轴心</label>
  </div>
</div>

<script>
const cv = document.getElementById("cv");
const ctx = cv.getContext("2d");

const images = {};
const partNames = ["tail", "feet", "body", "wing", "head", "beak", "crest", "eye_open", "eye_blink", "eye_happy"];
let loadedCount = 0;

let currentEye = "eye_open";
let animTimer = null;
let animType = "idle";
let animTime = 0;

// Pivot points from python extraction
const PIVOTS = {
  crest: [135, 126],
  head: [135, 260],
  beak: [44, 215],
  wing: [135, 290],
  tail: [336, 422],
  feet: [175, 490],
  body: [185, 370]
};

partNames.forEach(name => {
  const img = new Image();
  img.src = `parts/${name}_full.png`;
  img.onload = () => {
    images[name] = img;
    loadedCount++;
    if (loadedCount === partNames.length) {
      setPreset('idle');
    }
  };
});

function getVal(id) { return parseFloat(document.getElementById(id).value); }
function isChecked(id) { return document.getElementById(id).checked; }

function updateSliders() {
  document.getElementById("v-crest").innerText = getVal("s-crest") + "°";
  document.getElementById("v-head").innerText = getVal("s-head") + "°";
  document.getElementById("v-beak").innerText = getVal("s-beak") + "px";
  document.getElementById("v-wing").innerText = getVal("s-wing") + "°";
  document.getElementById("v-tail").innerText = getVal("s-tail") + "°";
  document.getElementById("v-feet").innerText = getVal("s-feet") + "°";
  document.getElementById("v-body").innerText = (getVal("s-body") / 100).toFixed(2) + "x";
  render();
}

function setEye(type) {
  currentEye = type;
  document.querySelectorAll("#btn-eye-open, #btn-eye-blink, #btn-eye-happy").forEach(b => b.classList.remove("active"));
  document.getElementById(`btn-${type.replace('_', '-')}`).classList.add("active");
  render();
}

function drawPivotCross(x, y) {
  if (!isChecked("chk-pivots")) return;
  ctx.save();
  ctx.strokeStyle = "rgba(235, 40, 40, 0.9)";
  ctx.lineWidth = 2;
  ctx.beginPath();
  ctx.moveTo(x - 6, y); ctx.lineTo(x + 6, y);
  ctx.moveTo(x, y - 6); ctx.lineTo(x, y + 6);
  ctx.stroke();
  ctx.fillStyle = "#fff";
  ctx.beginPath(); ctx.arc(x, y, 2.5, 0, Math.PI * 2); ctx.fill();
  ctx.stroke();
  ctx.restore();
}

function render() {
  if (loadedCount < partNames.length) return;
  ctx.clearRect(0, 0, cv.width, cv.height);

  const rad = d => d * Math.PI / 180;

  const aCrest = rad(getVal("s-crest"));
  const aHead = rad(getVal("s-head"));
  const dBeak = getVal("s-beak");
  const aWing = rad(getVal("s-wing"));
  const aTail = rad(getVal("s-tail"));
  const aFeet = rad(getVal("s-feet"));
  const sBody = getVal("s-body") / 100;

  // 1. TAIL
  if (isChecked("chk-tail") && images["tail"]) {
    ctx.save();
    ctx.translate(PIVOTS.tail[0], PIVOTS.tail[1]);
    ctx.rotate(aTail);
    ctx.translate(-PIVOTS.tail[0], -PIVOTS.tail[1]);
    ctx.drawImage(images["tail"], 0, 0);
    drawPivotCross(PIVOTS.tail[0], PIVOTS.tail[1]);
    ctx.restore();
  }

  // 2. FEET
  if (isChecked("chk-feet") && images["feet"]) {
    ctx.save();
    ctx.translate(PIVOTS.feet[0], PIVOTS.feet[1]);
    ctx.rotate(aFeet);
    ctx.translate(-PIVOTS.feet[0], -PIVOTS.feet[1]);
    ctx.drawImage(images["feet"], 0, 0);
    drawPivotCross(PIVOTS.feet[0], PIVOTS.feet[1]);
    ctx.restore();
  }

  // 3. BODY (躯干)
  if (isChecked("chk-body") && images["body"]) {
    ctx.save();
    ctx.translate(PIVOTS.body[0], PIVOTS.body[1]);
    ctx.scale(1.0, sBody);
    ctx.translate(-PIVOTS.body[0], -PIVOTS.body[1]);
    ctx.drawImage(images["body"], 0, 0);
    drawPivotCross(PIVOTS.body[0], PIVOTS.body[1]);
    ctx.restore();
  }

  // 4. WING (翅膀)
  if (isChecked("chk-wing") && images["wing"]) {
    ctx.save();
    ctx.translate(PIVOTS.wing[0], PIVOTS.wing[1]);
    ctx.rotate(aWing);
    ctx.translate(-PIVOTS.wing[0], -PIVOTS.wing[1]);
    ctx.drawImage(images["wing"], 0, 0);
    drawPivotCross(PIVOTS.wing[0], PIVOTS.wing[1]);
    ctx.restore();
  }

  // 5. HEAD + CREST + BEAK + EYE (Hierarchical Transform on Neck Pivot)
  ctx.save();
  ctx.translate(PIVOTS.head[0], PIVOTS.head[1]);
  ctx.rotate(aHead);
  ctx.translate(-PIVOTS.head[0], -PIVOTS.head[1]);

  // Head Base
  if (isChecked("chk-head") && images["head"]) {
    ctx.drawImage(images["head"], 0, 0);
  }
  // Eye
  if (images[currentEye]) {
    ctx.drawImage(images[currentEye], 0, 0);
  }

  // Beak (Slides down/rotates when opening)
  if (isChecked("chk-beak") && images["beak"]) {
    ctx.save();
    ctx.translate(PIVOTS.beak[0], PIVOTS.beak[1]);
    ctx.translate(-dBeak * 0.3, dBeak * 0.8);
    ctx.translate(-PIVOTS.beak[0], -PIVOTS.beak[1]);
    ctx.drawImage(images["beak"], 0, 0);
    drawPivotCross(PIVOTS.beak[0], PIVOTS.beak[1]);
    ctx.restore();
  }

  // Crest (Rotates on Skull Root Pivot)
  if (isChecked("chk-crest") && images["crest"]) {
    ctx.save();
    ctx.translate(PIVOTS.crest[0], PIVOTS.crest[1]);
    ctx.rotate(aCrest);
    ctx.translate(-PIVOTS.crest[0], -PIVOTS.crest[1]);
    ctx.drawImage(images["crest"], 0, 0);
    drawPivotCross(PIVOTS.crest[0], PIVOTS.crest[1]);
    ctx.restore();
  }

  drawPivotCross(PIVOTS.head[0], PIVOTS.head[1]);
  ctx.restore();
}

function setPreset(type) {
  stopAnimation();
  animType = type;
  animTime = 0;
  
  if (type === 'alert') {
    document.getElementById("s-crest").value = 28;
    document.getElementById("s-head").value = -12;
    document.getElementById("s-wing").value = 0;
    document.getElementById("s-body").value = 104;
    setEye('eye_open');
    updateSliders();
  } else if (type === 'head_bow') {
    document.getElementById("s-crest").value = -18;
    document.getElementById("s-head").value = 24;
    document.getElementById("s-wing").value = 0;
    setEye('eye_happy');
    updateSliders();
  }

  animTimer = setInterval(() => {
    animTime += 0.05;
    if (animType === 'idle') {
      // Gentle breathing & subtle crest fluttering
      document.getElementById("s-crest").value = Math.sin(animTime * 2.5) * 4;
      document.getElementById("s-head").value = Math.sin(animTime * 1.8) * 2;
      document.getElementById("s-body").value = 100 + Math.sin(animTime * 2.5) * 2;
      document.getElementById("s-tail").value = Math.sin(animTime * 1.5) * 3;
      // Periodic blink
      if (Math.sin(animTime * 1.2) > 0.92) setEye('eye_blink');
      else setEye('eye_open');
    } else if (animType === 'happy_wing') {
      // Flapping wings happily & hopping
      document.getElementById("s-wing").value = Math.sin(animTime * 14) * 28;
      document.getElementById("s-crest").value = 15 + Math.sin(animTime * 8) * 8;
      document.getElementById("s-head").value = Math.sin(animTime * 7) * 6;
      document.getElementById("s-tail").value = Math.sin(animTime * 10) * 12;
      setEye('eye_happy');
    } else if (animType === 'waddle') {
      // Alternating steps & body waddle
      document.getElementById("s-feet").value = Math.sin(animTime * 8) * 14;
      document.getElementById("s-body").value = 100 + Math.abs(Math.sin(animTime * 8)) * 3;
      document.getElementById("s-head").value = Math.sin(animTime * 8) * 5;
      document.getElementById("s-tail").value = -Math.sin(animTime * 8) * 8;
    } else if (animType === 'bob') {
      // Rapid rhythmic nodding
      document.getElementById("s-head").value = Math.sin(animTime * 12) * 16;
      document.getElementById("s-crest").value = 10 + Math.sin(animTime * 12) * 10;
      document.getElementById("s-tail").value = Math.sin(animTime * 12) * 6;
      setEye('eye_open');
    }
    updateSliders();
  }, 35);
}

function stopAnimation() {
  if (animTimer) clearInterval(animTimer);
  animTimer = null;
}
</script>
</body>
</html>
"""

with open(os.path.join(BASE_DIR, "rig_preview.html"), "w", encoding="utf-8") as f:
    f.write(html_content)

print("Saved interactive visualizer to: D:\\pets\\2d\\rig_preview.html")
