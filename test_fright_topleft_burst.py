"""Fright Sound Wave:
Plan A (Three-directional golden-yellow sound burst: bright yellow outer rim #ffd100, warm orange core #ff9800, dark outline #4a3b2c).
Positioned at the TOP-LEFT of the beak shell (嘴壳左上角).
Animation synchronized with the opening of the mouth (跟随嘴巴展开展示动画):
- Frame 0: 受惊蓄力（闭嘴瞪眼，无声波）
- Frame 1: 嘴壳初张（张口瞬间，声波在嘴壳左上角初现，小尺寸 Stage 1）
- Frame 2: 嘴壳大张（威慑尖叫峰值，嘴壳左上角全盛舒展绽放，全尺寸 Stage 2）
- Frame 3: 叫罢闭嘴（收声警戒，声波散去，进入防御闭嘴姿态）
"""
from PIL import Image, ImageDraw
from pathlib import Path
import shutil
import sys

sys.path.append(r"D:\pets\2d-new")
from generate_sprites_q_optimized import bird_q_optimized, C

OUT_DIR = Path(r"D:\pets\test_fright_burst")
OUT_DIR.mkdir(parents=True, exist_ok=True)
ARTIFACT_DIR = Path(r"C:\Users\26893\.gemini\antigravity\brain\5df30705-c1cf-4a9e-883a-019811f74aae")

C_BURST_YELLOW = "#ffd100"  # Bright golden-yellow outer rim
C_BURST_ORANGE = "#ff9800"  # Warm deep orange inner core
C_BURST_DARK = "#4a3b2c"    # Dark outline for crisp pixel clarity

def draw_topleft_beak_burst(im, beak_tip=(15, 34), stage=1):
    """Draw Plan A sound wedges at the TOP-LEFT of the beak shell (嘴壳左上角).
    Guarantees:
    1. Position is clearly at the top-left of the beak shell.
    2. Airy distance from beak shell (no collision/overlap).
    3. Strictly within canvas boundary (x >= 2, no clipping).
    4. Follows mouth opening progression (stage 1 = emerging, stage 2 = peak burst).
    """
    if stage == 0:
        return im
    im = im.copy()
    d = ImageDraw.Draw(im)
    bx, by = beak_tip

    # Origin placed at the top-left of the beak shell:
    # beak_tip is around (15, 34)
    # stage 1: ox ~ 9.5, oy ~ 24.5, s = 0.65 (emerging)
    # stage 2: ox ~ 8.5, oy ~ 22.0, s = 0.90 (full bloom)
    if stage == 1:
        ox = bx - 5.5   # x = 9.5
        oy = by - 9.5   # y = 24.5
        s = 0.66
    elif stage == 2:
        ox = bx - 6.5   # x = 8.5
        oy = by - 12.0  # y = 22.0
        s = 0.90
    else:
        ox = bx - 6.0
        oy = by - 10.0
        s = 0.75

    # 1. TOP WEDGE (fans upward into the high sky)
    top_outer = [
        (ox - 1 * s, oy - 2 * s),
        (ox + 3 * s, oy - 2 * s),
        (ox + 1.5 * s, oy - 13 * s),
        (ox - 2.5 * s, oy - 12 * s)
    ]
    top_inner = [
        (ox, oy - 3 * s),
        (ox + 2 * s, oy - 3 * s),
        (ox + 1 * s, oy - 11 * s),
        (ox - 1.5 * s, oy - 10 * s)
    ]

    # 2. MID WEDGE (fans towards top-left diagonally, longest wedge)
    # Ends at ox - 6.2*s => when ox=8.5, s=0.9: 8.5 - 5.58 = 2.92 (safely >= 2!)
    mid_outer = [
        (ox - 1 * s, oy),
        (ox + 1 * s, oy + 3 * s),
        (ox - 6.2 * s, oy - 5.5 * s),
        (ox - 6.2 * s, oy - 9.5 * s)
    ]
    mid_inner = [
        (ox - 1 * s, oy + 1 * s),
        (ox, oy + 2 * s),
        (ox - 5.2 * s, oy - 5.5 * s),
        (ox - 5.2 * s, oy - 8.5 * s)
    ]

    # 3. BOT WEDGE (fans left-forward in front of upper beak)
    # Ends at ox - 5.8*s => when ox=8.5, s=0.9: 8.5 - 5.22 = 3.28 (safely >= 3!)
    bot_outer = [
        (ox, oy + 4.5 * s),
        (ox + 3 * s, oy + 5.5 * s),
        (ox - 5.8 * s, oy + 3.5 * s),
        (ox - 5.5 * s, oy + 0.5 * s)
    ]
    bot_inner = [
        (ox, oy + 4.5 * s),
        (ox + 2 * s, oy + 5.5 * s),
        (ox - 4.8 * s, oy + 3.5 * s),
        (ox - 4.5 * s, oy + 1.5 * s)
    ]

    for outer, inner in [(top_outer, top_inner), (mid_outer, mid_inner), (bot_outer, bot_inner)]:
        outer_pts = [(round(x), round(y)) for x, y in outer]
        inner_pts = [(round(x), round(y)) for x, y in inner]
        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            d.polygon([(x + dx, y + dy) for x, y in outer_pts], fill=C_BURST_DARK)
        d.polygon(outer_pts, fill=C_BURST_YELLOW)
        d.polygon(inner_pts, fill=C_BURST_ORANGE)

    # Acoustic trajectory sparkles floating from open beak up to the sound wave
    if stage == 1:
        d.point((round(bx - 2), round(by - 4)), fill=C_BURST_YELLOW)
    elif stage == 2:
        d.point((round(bx - 2), round(by - 4)), fill=C_BURST_YELLOW)
        d.point((round(bx - 4), round(by - 7)), fill=C_BURST_ORANGE)

    return im

def generate_fright_suite():
    # 4 Frames Sequence tightly bound to mouth expansion:
    # Frame 0: 【受惊蓄力】 闭嘴瞪眼，受戳警觉，声波尚未萌发
    f0 = bird_q_optimized(
        head=(1, -2), body_roll=1, tail_wag=-1,
        crest="alert", eye="wide", mouth="closed"
    )

    # Frame 1: 【嘴壳初张】 头部前探，嘴壳张开，声波在嘴壳左上角初萌 (Stage 1)
    f1_base = bird_q_optimized(
        head=(-1, -1), body_roll=-1, tail_wag=3,
        crest="alert", eye="wide", mouth="bite"
    )
    f1 = draw_topleft_beak_burst(f1_base, beak_tip=(15, 34), stage=1)

    # Frame 2: 【嘴壳大张】 尖叫威慑峰值，嘴壳最大张开，声波在嘴壳左上角全盛舒展 (Stage 2)
    f2_base = bird_q_optimized(
        head=(0, 0), body_roll=-1, tail_wag=2,
        crest="alert", eye="wide", mouth="bite"
    )
    f2 = draw_topleft_beak_burst(f2_base, beak_tip=(16, 35), stage=2)

    # Frame 3: 【收声警戒】 嘴巴迅速闭合，余波消散，保持瞪眼立冠防御姿态
    f3 = bird_q_optimized(
        head=(-1, -1), body_roll=0, tail_wag=1,
        crest="alert", eye="wide", mouth="closed"
    )

    frames = [f0, f1, f2, f3]

    # 1. Save PNG frames
    for idx, f in enumerate(frames):
        f.save(OUT_DIR / f"fright_topleft_{idx}.png")

    # 2. Spritesheet (2x) with clean dividers and frame annotations
    sheet_w = 100 * 4
    sheet_h = 80
    sheet = Image.new("RGBA", (sheet_w, sheet_h), (245, 247, 250, 255))
    d_sheet = ImageDraw.Draw(sheet)
    for idx, f in enumerate(frames):
        ox = idx * 100
        sheet.paste(f, (ox, 0), f)
        if idx > 0:
            d_sheet.line([(ox, 0), (ox, sheet_h)], fill="#d5dae2")
    sheet_2x = sheet.resize((sheet_w * 2, sheet_h * 2), Image.NEAREST)
    sheet_2x.save(OUT_DIR / "fright_topleft_spritesheet_2x.png")

    # 3. Animated GIF (3x) showing loop progression
    durations = [140, 160, 240, 320, 360]
    gif_frames = [f0, f1, f2, f3, f3]
    scaled_gif = [f.resize((300, 240), Image.NEAREST) for f in gif_frames]
    scaled_gif[0].save(
        OUT_DIR / "fright_topleft_burst_3x.gif",
        save_all=True,
        append_images=scaled_gif[1:],
        duration=durations,
        loop=0,
        disposal=2
    )

    # 4. Realistic Poke Interaction Simulation (2x)
    # Cursor approaches body -> Clicks body -> Cockatiel startles & shrieks with topleft burst -> Settles
    w, h = 160, 100
    base_bg = Image.new("RGBA", (w, h), (248, 249, 250, 255))
    d_bg = ImageDraw.Draw(base_bg)
    d_bg.line([(0, 87), (w, 87)], fill="#d8dde4", width=1)

    cursor = Image.new("RGBA", (20, 20), (0, 0, 0, 0))
    d_cur = ImageDraw.Draw(cursor)
    arrow_pts = [(0, 0), (0, 14), (4, 11), (7, 16), (9, 15), (6, 10), (11, 10)]
    d_cur.polygon(arrow_pts, fill="#ffffff", outline="#2b2a2e")

    sim_frames = []
    sim_durations = []

    # Approach
    for step in range(3):
        f = base_bg.copy()
        f.paste(frames[3], (25, 10), frames[3])
        cx = 120 - step * 25
        cy = 30 + step * 8
        f.paste(cursor, (cx, cy), cursor)
        sim_frames.append(f)
        sim_durations.append(150)

    # Click body (trigger poke)
    click_f = base_bg.copy()
    click_f.paste(frames[0], (25, 10), frames[0])
    d_click = ImageDraw.Draw(click_f)
    d_click.ellipse((85, 48, 93, 56), fill="#ffd100", outline="#353438")
    click_f.paste(cursor, (80, 42), cursor)
    sim_frames.append(click_f)
    sim_durations.append(130)

    # Reaction (Frame 1: beak opens, sound wave begins at top-left)
    f_react1 = base_bg.copy()
    f_react1.paste(frames[1], (25, 10), frames[1])
    f_react1.paste(cursor, (94, 34), cursor)
    sim_frames.append(f_react1)
    sim_durations.append(160)

    # Reaction (Frame 2: beak wide open, sound wave full bloom at top-left)
    f_react2 = base_bg.copy()
    f_react2.paste(frames[2], (25, 10), frames[2])
    f_react2.paste(cursor, (100, 30), cursor)
    sim_frames.append(f_react2)
    sim_durations.append(220)

    # Reaction (Frame 3: beak closes, settle back)
    f_react3 = base_bg.copy()
    f_react3.paste(frames[3], (25, 10), frames[3])
    f_react3.paste(cursor, (105, 26), cursor)
    sim_frames.append(f_react3)
    sim_durations.append(180)

    # Settle idle
    f_idle = base_bg.copy()
    f_idle.paste(frames[3], (25, 10), frames[3])
    sim_frames.append(f_idle)
    sim_durations.append(450)

    sim_2x = [sf.resize((w * 2, h * 2), Image.NEAREST) for sf in sim_frames]
    sim_2x[0].save(
        OUT_DIR / "fright_topleft_interaction_2x.gif",
        save_all=True,
        append_images=sim_2x[1:],
        duration=sim_durations,
        loop=0,
        disposal=2
    )

    # Copy all to Artifact directory
    if ARTIFACT_DIR.exists():
        sheet_2x.save(ARTIFACT_DIR / "fright_topleft_spritesheet_2x.png")
        scaled_gif[0].save(
            ARTIFACT_DIR / "fright_topleft_burst_3x.gif",
            save_all=True,
            append_images=scaled_gif[1:],
            duration=durations,
            loop=0,
            disposal=2
        )
        sim_2x[0].save(
            ARTIFACT_DIR / "fright_topleft_interaction_2x.gif",
            save_all=True,
            append_images=sim_2x[1:],
            duration=sim_durations,
            loop=0,
            disposal=2
        )
        for idx in range(4):
            shutil.copy(OUT_DIR / f"fright_topleft_{idx}.png", ARTIFACT_DIR / f"fright_topleft_{idx}.png")
        print("Copied all to artifact directory.")

    print("Generated topleft beak burst suite successfully.")

if __name__ == "__main__":
    generate_fright_suite()
