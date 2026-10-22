import os
import shutil
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ARTIFACT_DIR = Path(r"C:\Users\26893\.gemini\antigravity\brain\5df30705-c1cf-4a9e-883a-019811f74aae")
CLASSIC_DIR = Path(r"D:\pets\assets\sprites_classic")
TRIPLE_DIR = Path(r"D:\pets\assets\sprites_triple")

try:
    font_path = "C:/Windows/Fonts/msyh.ttc"
    f_title = ImageFont.truetype(font_path, 16)
    f_sub = ImageFont.truetype(font_path, 13)
    f_desc = ImageFont.truetype(font_path, 11)
except:
    f_title = f_sub = f_desc = ImageFont.load_default()

def create_side_by_side_action_gif(stems, durations, filename, title_text, left_label="🐰 经典兔耳羽冠", right_label="✨ 灵动三毛羽冠"):
    scale = 3
    W, H = 100 * scale, 80 * scale
    canvas_w = W * 2 + 30
    canvas_h = H + 40
    
    frames = []
    for stem in stems:
        im_classic = Image.open(CLASSIC_DIR / f"{stem}.png").convert("RGBA")
        im_triple = Image.open(TRIPLE_DIR / f"{stem}.png").convert("RGBA")
        
        canvas = Image.new("RGBA", (canvas_w, canvas_h), (247, 247, 250, 255))
        d = ImageDraw.Draw(canvas)
        
        up_c = im_classic.resize((W, H), Image.NEAREST)
        up_t = im_triple.resize((W, H), Image.NEAREST)
        
        # Left: Classic
        canvas.paste(up_c, (10, 30), up_c)
        d.text((15, 8), f"{left_label} - {stem}", fill=(90, 50, 30), font=f_sub)
        
        # Right: Triple
        canvas.paste(up_t, (W + 20, 30), up_t)
        d.text((W + 25, 8), f"{right_label} - {stem}", fill=(20, 80, 130), font=f_sub)
        
        frames.append(canvas)
        
    out_path = ARTIFACT_DIR / filename
    frames[0].save(
        out_path,
        save_all=True,
        append_images=frames[1:],
        duration=durations,
        loop=0,
        disposal=2
    )
    print(f"Generated {filename}")

# 1. Peck (啄地动作对比，4帧)
peck_stems = ["peck_0", "peck_1", "peck_2", "peck_3"]
peck_durs = [240, 200, 240, 300]
create_side_by_side_action_gif(peck_stems, peck_durs, "peck_dual_crest_comparison_3x.gif", "啄地动作羽冠惯性动画对比", "【经典兔耳羽冠】", "【灵动三毛羽冠】")

# 2. Bonk (敲击屏幕动作对比，5帧)
bonk_stems = ["bonk_0", "bonk_1", "bonk_2", "bonk_3", "bonk_4"]
bonk_durs = [200, 180, 220, 240, 320]
create_side_by_side_action_gif(bonk_stems, bonk_durs, "bonk_dual_crest_comparison_3x.gif", "敲击屏幕羽冠惯性动画对比", "【经典兔耳羽冠】", "【灵动三毛羽冠】")

# 3. Preen (理毛动作对比，4帧)
preen_stems = ["preen_0", "preen_1", "preen_2", "preen_3"]
preen_durs = [220, 220, 220, 250]
create_side_by_side_action_gif(preen_stems, preen_durs, "preen_dual_crest_comparison_3x.gif", "转头埋背理毛羽冠对比", "【经典兔耳羽冠】", "【灵动三毛羽冠】")

# 4. Fly (飞行扑翼对比，4帧)
fly_stems = ["fly_0", "fly_1", "fly_2", "fly_3"]
fly_durs = [120, 120, 120, 120]
create_side_by_side_action_gif(fly_stems, fly_durs, "fly_dual_crest_comparison_3x.gif", "振翅飞行流线型羽冠对比", "【经典兔耳羽冠】", "【灵动三毛羽冠】")

# 5. Idle/Waddle (待机与走动对比，8帧)
waddle_stems = [f"waddle_{i}" for i in range(8)]
waddle_durs = [120] * 8
create_side_by_side_action_gif(waddle_stems, waddle_durs, "waddle_dual_crest_comparison_3x.gif", "走动摇摆羽冠对比", "【经典兔耳羽冠】", "【灵动三毛羽冠】")

# 6. Hop (雀跃小跳羽冠惯性对比，4帧)
hop_stems = ["hop_0", "hop_1", "hop_2", "hop_3"]
hop_durs = [130, 160, 130, 110]
create_side_by_side_action_gif(hop_stems, hop_durs, "hop_dual_crest_comparison_3x.gif", "雀跃小跳羽冠动力学与惯性甩鞭对比", "【经典兔耳羽冠】", "【灵动三毛羽冠】")

# 7. Moving Hop Simulation (真实横向跳跃位移对比动画)
def create_moving_hop_dual_simulation(filename="hop_moving_dual_crest_simulation_2x.gif"):
    sim_w, sim_h = 270, 95
    scale = 2
    ground_y = 8
    start_x = 190
    
    # Load 4 frames for classic and triple
    c_frames = [Image.open(CLASSIC_DIR / f"hop_{i}.png").convert("RGBA") for i in range(4)]
    t_frames = [Image.open(TRIPLE_DIR / f"hop_{i}.png").convert("RGBA") for i in range(4)]
    
    # We will build side-by-side or stacked simulation canvas
    # Let's stack them vertically: Top = Classic, Bottom = Triple
    cw = sim_w * scale
    ch = (sim_h * 2 + 35) * scale
    
    sim_steps = [
        # (frame_idx, dx, duration_ms)
        (0, 0, 130),
        (1, -8, 160),
        (2, -4, 130),
        (3, -2, 110),
        (0, 0, 130),
        (1, -8, 160),
        (2, -4, 130),
        (3, -2, 110),
        (0, 0, 130),
        (1, -8, 160),
        (2, -4, 130),
        (3, -2, 110),
        (0, 0, 450) # pause at the end
    ]
    
    base_bg = Image.new("RGBA", (sim_w, sim_h * 2 + 35), (247, 247, 250, 255))
    d_base = ImageDraw.Draw(base_bg)
    # Ground lines
    d_base.line([(0, 80), (sim_w, 80)], fill="#d5dae2", width=1)
    d_base.line([(0, 80 + sim_h + 15), (sim_w, 80 + sim_h + 15)], fill="#d5dae2", width=1)
    # Labels
    d_base.text((10, 4), "🐰 经典兔耳羽冠 (跳跃惯性物理)", fill=(90, 50, 30), font=f_sub)
    d_base.text((10, sim_h + 19), "✨ 灵动三毛羽冠 (跳跃惯性物理)", fill=(20, 80, 130), font=f_sub)
    
    out_frames = []
    durations = []
    cur_x = start_x
    
    for f_idx, dx, dur in sim_steps:
        cur_x += dx
        canvas = base_bg.copy()
        # Paste classic (top)
        c_img = c_frames[f_idx]
        canvas.paste(c_img, (cur_x, ground_y), c_img)
        # Paste triple (bottom)
        t_img = t_frames[f_idx]
        canvas.paste(t_img, (cur_x, ground_y + sim_h + 15), t_img)
        
        scaled_c = canvas.resize((cw, ch), Image.NEAREST)
        out_frames.append(scaled_c)
        durations.append(dur)
        
    out_path = ARTIFACT_DIR / filename
    out_frames[0].save(
        out_path,
        save_all=True,
        append_images=out_frames[1:],
        duration=durations,
        loop=0,
        disposal=2
    )
    print(f"Generated {filename}")

create_moving_hop_dual_simulation()

# 6. Static Card (展示右键菜单与双羽冠全景对比图)
scale = 4
W, H = 100 * scale, 80 * scale
card_w = W * 2 + 40
card_h = H + 80
card = Image.new("RGBA", (card_w, card_h), (247, 247, 250, 255))
d_card = ImageDraw.Draw(card)

im_c = Image.open(CLASSIC_DIR / "idle_0.png").convert("RGBA").resize((W, H), Image.NEAREST)
im_t = Image.open(TRIPLE_DIR / "idle_0.png").convert("RGBA").resize((W, H), Image.NEAREST)

card.paste(im_c, (15, 55), im_c)
card.paste(im_t, (W + 25, 55), im_t)

d_card.text((20, 14), "桌宠右键菜单【羽冠造型切换】已上线", fill=(20, 20, 30), font=f_title)
d_card.text((20, 38), "可在桌宠右键菜单中一键自由热切换，实时生效并自动记忆保存配置", fill=(100, 100, 110), font=f_desc)

d_card.text((25, H + 58), "【经典兔耳羽冠】(经典双叉)", fill=(90, 50, 30), font=f_sub)
d_card.text((W + 35, H + 58), "【灵动三毛羽冠】(反曲重叠)", fill=(20, 80, 130), font=f_sub)

card_out = ARTIFACT_DIR / "dual_crest_menu_showcase_4x.png"
card.save(card_out)
print(f"Generated {card_out.name}")
