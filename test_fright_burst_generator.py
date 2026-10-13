"""Refined fright sound burst:
Reusing the yellow-orange 3-wedge sound symbol,
fanning forward out of the mouth, with clear airy distance from the beak and no clipping.
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

def draw_airy_beak_burst(im, beak_tip=(16, 35), stage=1):
    """Draw the 3-wedge golden-orange sound burst floating in the air
    in front of the beak with a clear gap (7~12px separation).
    """
    if stage == 0:
        return im
    im = im.copy()
    d = ImageDraw.Draw(im)
    bx, by = beak_tip

    # Origin of sound emission is shifted forward and up from beak tip
    # stage 1: ~7px away
    # stage 2: ~11px away (sound wave traveled further)
    if stage == 1:
        ox = bx - 6   # x around 10
        oy = by - 7   # y around 28
        s = 0.72
    elif stage == 2:
        ox = bx - 8   # x around 8
        oy = by - 9   # y around 26
        s = 0.90
    else:
        ox = bx - 6
        oy = by - 7
        s = 0.8

    # 3 wedges fanning forward and outwards:
    # 1. Top wedge (angled up-left towards top-left corner)
    top_outer = [
        (ox - 3 * s, oy - 2 * s),
        (ox - 1 * s, oy - 4 * s),
        (ox - 6 * s, oy - 14 * s),
        (ox - 10 * s, oy - 13 * s)
    ]
    top_inner = [
        (ox - 3 * s, oy - 3 * s),
        (ox - 2 * s, oy - 4 * s),
        (ox - 6 * s, oy - 12 * s),
        (ox - 9 * s, oy - 12 * s)
    ]

    # 2. Mid wedge (longest, shooting straight forward-left)
    mid_outer = [
        (ox - 2 * s, oy - 1 * s),
        (ox - 2 * s, oy + 3 * s),
        (ox - 13 * s, oy + 1 * s),
        (ox - 14 * s, oy - 3 * s)
    ]
    mid_inner = [
        (ox - 3 * s, oy),
        (ox - 3 * s, oy + 2 * s),
        (ox - 12 * s, oy + 1 * s),
        (ox - 12 * s, oy - 2 * s)
    ]

    # 3. Bot wedge (angled down-left)
    bot_outer = [
        (ox - 1 * s, oy + 4 * s),
        (ox - 3 * s, oy + 6 * s),
        (ox - 9 * s, oy + 10 * s),
        (ox - 11 * s, oy + 8 * s)
    ]
    bot_inner = [
        (ox - 2 * s, oy + 4 * s),
        (ox - 3 * s, oy + 6 * s),
        (ox - 8 * s, oy + 9 * s),
        (ox - 10 * s, oy + 7 * s)
    ]

    c_yellow = "#ffd100"  # Bright golden-yellow outer
    c_orange = "#ff9800"  # Warm orange inner
    c_dark = "#4a3b2c"    # Dark outline

    for outer, inner in [(top_outer, top_inner), (mid_outer, mid_inner), (bot_outer, bot_inner)]:
        outer_pts = [(round(x), round(y)) for x, y in outer]
        inner_pts = [(round(x), round(y)) for x, y in inner]
        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            d.polygon([(x + dx, y + dy) for x, y in outer_pts], fill=c_dark)
        d.polygon(outer_pts, fill=c_yellow)
        d.polygon(inner_pts, fill=c_orange)

    # Optional subtle sound trajectory sparks between beak tip and burst
    if stage == 1:
        d.point((bx - 2, by - 3), fill="#ffd100")
    elif stage == 2:
        d.point((bx - 2, by - 3), fill="#ffd100")
        d.point((bx - 4, by - 5), fill="#ff9800")

    return im

def build_airy_burst_suite():
    # Base bird frames:
    # 0: Startled (wide eyes, closed mouth)
    f0 = bird_q_optimized(head=(1, -2), body_roll=1, tail_wag=-1, crest="alert", eye="wide", mouth="closed")
    # 1: Snap open beak, shriek! (Beak tip at x=16, y=35)
    f1_base = bird_q_optimized(head=(-1, -1), body_roll=-1, tail_wag=3, crest="alert", eye="wide", mouth="bite")
    # 2: Peak shriek hold!
    f2_base = bird_q_optimized(head=(0, 0), body_roll=-1, tail_wag=2, crest="alert", eye="wide", mouth="bite")
    # 3: Settle back
    f3 = bird_q_optimized(head=(-1, -1), body_roll=0, tail_wag=1, crest="alert", eye="wide", mouth="closed")

    # Draw airy burst
    f1 = draw_airy_beak_burst(f1_base, beak_tip=(16, 35), stage=1)
    f2 = draw_airy_beak_burst(f2_base, beak_tip=(17, 36), stage=2)

    frames = [f0, f1, f2, f3]

    for idx, f in enumerate(frames):
        f.save(OUT_DIR / f"fright_burst_airy_{idx}.png")

    # Spritesheet (2x)
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
    sheet_2x.save(OUT_DIR / "fright_burst_airy_spritesheet_2x.png")

    # Animated GIF (3x)
    durations = [140, 160, 220, 300, 350]
    gif_frames = [f0, f1, f2, f3, f3]
    scaled_gif = [f.resize((300, 240), Image.NEAREST) for f in gif_frames]
    scaled_gif[0].save(
        OUT_DIR / "fright_burst_airy_3x.gif",
        save_all=True,
        append_images=scaled_gif[1:],
        duration=durations,
        loop=0,
        disposal=2
    )

    # Mouse Click Interaction Simulation GIF (2x)
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

    # Click
    click_f = base_bg.copy()
    click_f.paste(frames[0], (25, 10), frames[0])
    d_click = ImageDraw.Draw(click_f)
    d_click.ellipse((85, 48, 93, 56), fill="#ffd100", outline="#353438")
    click_f.paste(cursor, (80, 42), cursor)
    sim_frames.append(click_f)
    sim_durations.append(130)

    # Reaction (shriek with airy yellow burst)
    for b_idx in [1, 2, 3]:
        f = base_bg.copy()
        f.paste(frames[b_idx], (25, 10), frames[b_idx])
        f.paste(cursor, (88 + b_idx * 6, 38 - b_idx * 4), cursor)
        sim_frames.append(f)
        sim_durations.append(160)

    # Settle
    f = base_bg.copy()
    f.paste(frames[3], (25, 10), frames[3])
    sim_frames.append(f)
    sim_durations.append(450)

    sim_2x = [sf.resize((w * 2, h * 2), Image.NEAREST) for sf in sim_frames]
    sim_2x[0].save(
        OUT_DIR / "fright_burst_airy_interaction_2x.gif",
        save_all=True,
        append_images=sim_2x[1:],
        duration=sim_durations,
        loop=0,
        disposal=2
    )

    # Copy to artifacts directory
    if ARTIFACT_DIR.exists():
        sheet_2x.save(ARTIFACT_DIR / "fright_burst_airy_spritesheet_2x.png")
        scaled_gif[0].save(
            ARTIFACT_DIR / "fright_burst_airy_3x.gif",
            save_all=True,
            append_images=scaled_gif[1:],
            duration=durations,
            loop=0,
            disposal=2
        )
        sim_2x[0].save(
            ARTIFACT_DIR / "fright_burst_airy_interaction_2x.gif",
            save_all=True,
            append_images=sim_2x[1:],
            duration=sim_durations,
            loop=0,
            disposal=2
        )
        print("Copied airy burst preview assets to artifact directory.")

    print("Airy burst preview built successfully.")

if __name__ == "__main__":
    build_airy_burst_suite()
