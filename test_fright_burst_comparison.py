"""Fright Sound Burst Comparison Suite:
Strictly reuses the yellow-orange 3-wedge sound mark from Bonk.
Tests:
Mode A: Forward-radiating sound wave (fanning up-left away from beak, 8px air gap, guaranteed no clipping x>=2).
Mode B: Direct Bonk icon orientation (floating in the air in front-above beak).
Includes mouse poke interaction simulation.
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

C_BURST_YELLOW = "#ffd100"  # Bright golden-yellow rim
C_BURST_ORANGE = "#ff9800"  # Warm deep orange core
C_BURST_DARK = "#4a3b2c"    # 1px outline for clarity

def draw_forward_burst(im, beak_tip=(16, 35), stage=1):
    """Mode A: Sound wedges radiating forward and upward out of the beak.
    Maintains a 7~10px air gap from beak shell.
    Strictly stays within x >= 2 (no boundary clipping).
    """
    if stage == 0:
        return im
    im = im.copy()
    d = ImageDraw.Draw(im)
    bx, by = beak_tip

    # Stage 1: sound burst emerging in front of beak (gap ~7px)
    # Stage 2: sound burst resonant and expanding (gap ~9px)
    if stage == 1:
        ox = bx - 7   # x = 9
        oy = by - 8   # y = 27
        s = 0.75
    elif stage == 2:
        ox = bx - 8   # x = 8
        oy = by - 10  # y = 25
        s = 0.90
    else:
        ox = bx - 7
        oy = by - 8
        s = 0.80

    # 1. TOP WEDGE (steeply upward, slightly tilting left towards sky)
    top_outer = [
        (ox - 1 * s, oy - 2 * s),
        (ox + 3 * s, oy - 2 * s),
        (ox + 1 * s, oy - 14 * s),
        (ox - 3 * s, oy - 13 * s)
    ]
    top_inner = [
        (ox, oy - 3 * s),
        (ox + 2 * s, oy - 3 * s),
        (ox + 1 * s, oy - 12 * s),
        (ox - 2 * s, oy - 11 * s)
    ]

    # 2. MID WEDGE (angled ~40 deg up-left, longest wedge)
    # Ends at ox - 6.5*s => when ox=8, s=0.9: 8 - 5.85 = 2.15 (safe from x=0!)
    mid_outer = [
        (ox - 1 * s, oy),
        (ox + 1 * s, oy + 3 * s),
        (ox - 6.5 * s, oy - 6 * s),
        (ox - 6.5 * s, oy - 10 * s)
    ]
    mid_inner = [
        (ox - 1 * s, oy + 1 * s),
        (ox, oy + 2 * s),
        (ox - 5.5 * s, oy - 6 * s),
        (ox - 5.5 * s, oy - 9 * s)
    ]

    # 3. BOT WEDGE (forward-left, lower angle)
    # Ends at ox - 6*s => when ox=8, s=0.9: 8 - 5.4 = 2.6 (safe from x=0!)
    bot_outer = [
        (ox, oy + 5 * s),
        (ox + 3 * s, oy + 6 * s),
        (ox - 6 * s, oy + 4 * s),
        (ox - 5.5 * s, oy + 1 * s)
    ]
    bot_inner = [
        (ox, oy + 5 * s),
        (ox + 2 * s, oy + 6 * s),
        (ox - 5 * s, oy + 4 * s),
        (ox - 4.5 * s, oy + 2 * s)
    ]

    for outer, inner in [(top_outer, top_inner), (mid_outer, mid_inner), (bot_outer, bot_inner)]:
        outer_pts = [(round(x), round(y)) for x, y in outer]
        inner_pts = [(round(x), round(y)) for x, y in inner]
        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            d.polygon([(x + dx, y + dy) for x, y in outer_pts], fill=C_BURST_DARK)
        d.polygon(outer_pts, fill=C_BURST_YELLOW)
        d.polygon(inner_pts, fill=C_BURST_ORANGE)

    # Subtle acoustic vibration sparkles in the air between beak and burst
    if stage == 1:
        d.point((bx - 2, by - 3), fill=C_BURST_YELLOW)
    elif stage == 2:
        d.point((bx - 2, by - 3), fill=C_BURST_YELLOW)
        d.point((bx - 4, by - 5), fill=C_BURST_ORANGE)

    return im

def draw_bonk_style_float_burst(im, beak_tip=(16, 35), stage=1):
    """Mode B: Exactly reuses the bonk wedge geometry (radiating up-right),
    placed floating in the airy space above/in front of the beak (x=5, y=14),
    so it does not collide with the beak while maintaining clear distance.
    """
    if stage == 0:
        return im
    im = im.copy()
    d = ImageDraw.Draw(im)
    bx, by = beak_tip

    if stage == 1:
        ox = bx - 10  # x = 6
        oy = by - 16  # y = 19
        s = 0.65
    elif stage == 2:
        ox = bx - 11  # x = 5
        oy = by - 19  # y = 16
        s = 0.85
    else:
        ox = bx - 10
        oy = by - 16
        s = 0.70

    # Bonk wedge geometry (radiating up-right)
    top_outer = [
        (ox - 4 * s, oy - 2 * s),
        (ox - 1 * s, oy - 3 * s),
        (ox, oy - 12 * s),
        (ox - 3 * s, oy - 13 * s),
    ]
    top_inner = [
        (ox - 3 * s, oy - 3 * s),
        (ox - 2 * s, oy - 4 * s),
        (ox - 1 * s, oy - 11 * s),
        (ox - 2 * s, oy - 11 * s),
    ]

    mid_outer = [
        (ox - 1 * s, oy - 1 * s),
        (ox + 1 * s, oy - 3 * s),
        (ox + 11 * s, oy - 8 * s),
        (ox + 13 * s, oy - 4 * s),
        (ox + 9 * s, oy - 2 * s),
    ]
    mid_inner = [
        (ox + 1 * s, oy - 2 * s),
        (ox + 2 * s, oy - 3 * s),
        (ox + 10 * s, oy - 6 * s),
        (ox + 11 * s, oy - 4 * s),
        (ox + 8 * s, oy - 2 * s),
    ]

    bot_outer = [
        (ox + 1 * s, oy + 2 * s),
        (ox + 2 * s, oy + 5 * s),
        (ox + 9 * s, oy + 6 * s),
        (ox + 10 * s, oy + 2 * s),
    ]
    bot_inner = [
        (ox + 2 * s, oy + 3 * s),
        (ox + 3 * s, oy + 4 * s),
        (ox + 8 * s, oy + 5 * s),
        (ox + 9 * s, oy + 3 * s),
    ]

    for outer, inner in [(top_outer, top_inner), (mid_outer, mid_inner), (bot_outer, bot_inner)]:
        outer_pts = [(round(x), round(y)) for x, y in outer]
        inner_pts = [(round(x), round(y)) for x, y in inner]
        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            d.polygon([(x + dx, y + dy) for x, y in outer_pts], fill=C_BURST_DARK)
        d.polygon(outer_pts, fill=C_BURST_YELLOW)
        d.polygon(inner_pts, fill=C_BURST_ORANGE)

    # Connection ripples from mouth
    if stage == 1:
        d.point((bx - 3, by - 4), fill=C_BURST_YELLOW)
    elif stage == 2:
        d.point((bx - 3, by - 4), fill=C_BURST_YELLOW)
        d.point((bx - 5, by - 8), fill=C_BURST_ORANGE)

    return im

def build_comparison_suite():
    # Base Bird Frames
    # 0: Startled (wide eyes, closed mouth)
    f0 = bird_q_optimized(head=(1, -2), body_roll=1, tail_wag=-1, crest="alert", eye="wide", mouth="closed")
    # 1: Snap open beak, shriek! (Beak tip at x=16, y=35)
    f1_base = bird_q_optimized(head=(-1, -1), body_roll=-1, tail_wag=3, crest="alert", eye="wide", mouth="bite")
    # 2: Peak shriek hold!
    f2_base = bird_q_optimized(head=(0, 0), body_roll=-1, tail_wag=2, crest="alert", eye="wide", mouth="bite")
    # 3: Settle back
    f3 = bird_q_optimized(head=(-1, -1), body_roll=0, tail_wag=1, crest="alert", eye="wide", mouth="closed")

    # Mode A: Forward-radiating burst
    f1_a = draw_forward_burst(f1_base, beak_tip=(16, 35), stage=1)
    f2_a = draw_forward_burst(f2_base, beak_tip=(17, 36), stage=2)
    frames_a = [f0, f1_a, f2_a, f3]

    # Mode B: Floating bonk-orientation burst
    f1_b = draw_bonk_style_float_burst(f1_base, beak_tip=(16, 35), stage=1)
    f2_b = draw_bonk_style_float_burst(f2_base, beak_tip=(17, 36), stage=2)
    frames_b = [f0, f1_b, f2_b, f3]

    durations = [140, 160, 220, 300, 350]

    # Save individual frames & GIFs
    # Mode A GIF (3x)
    gif_a = [f.resize((300, 240), Image.NEAREST) for f in [f0, f1_a, f2_a, f3, f3]]
    gif_a[0].save(
        OUT_DIR / "fright_forward_burst_refined_3x.gif",
        save_all=True,
        append_images=gif_a[1:],
        duration=durations,
        loop=0,
        disposal=2
    )

    # Mode B GIF (3x)
    gif_b = [f.resize((300, 240), Image.NEAREST) for f in [f0, f1_b, f2_b, f3, f3]]
    gif_b[0].save(
        OUT_DIR / "fright_bonk_style_float_3x.gif",
        save_all=True,
        append_images=gif_b[1:],
        duration=durations,
        loop=0,
        disposal=2
    )

    # Side-by-side comparison sheet (2 rows, 4 columns)
    comp_w = 100 * 4
    comp_h = 80 * 2 + 10
    comp_img = Image.new("RGBA", (comp_w, comp_h), (245, 247, 250, 255))
    d_comp = ImageDraw.Draw(comp_img)

    for i in range(4):
        comp_img.paste(frames_a[i], (i * 100, 0), frames_a[i])
        comp_img.paste(frames_b[i], (i * 100, 90), frames_b[i])
        if i > 0:
            d_comp.line([(i * 100, 0), (i * 100, comp_h)], fill="#d5dae2")
    d_comp.line([(0, 85), (comp_w, 85)], fill="#b0b8c4", width=2)

    comp_2x = comp_img.resize((comp_w * 2, comp_h * 2), Image.NEAREST)
    comp_2x.save(OUT_DIR / "fright_sound_comparison_2x.png")

    # Mouse Click Interaction Simulation for Mode A (Recommended)
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
        f.paste(frames_a[3], (25, 10), frames_a[3])
        cx = 120 - step * 25
        cy = 30 + step * 8
        f.paste(cursor, (cx, cy), cursor)
        sim_frames.append(f)
        sim_durations.append(150)

    # Click
    click_f = base_bg.copy()
    click_f.paste(frames_a[0], (25, 10), frames_a[0])
    d_click = ImageDraw.Draw(click_f)
    d_click.ellipse((85, 48, 93, 56), fill="#ffd100", outline="#353438")
    click_f.paste(cursor, (80, 42), cursor)
    sim_frames.append(click_f)
    sim_durations.append(130)

    # Reaction (screech with yellow burst)
    for b_idx in [1, 2, 3]:
        f = base_bg.copy()
        f.paste(frames_a[b_idx], (25, 10), frames_a[b_idx])
        f.paste(cursor, (88 + b_idx * 6, 38 - b_idx * 4), cursor)
        sim_frames.append(f)
        sim_durations.append(160)

    # Settle
    f = base_bg.copy()
    f.paste(frames_a[3], (25, 10), frames_a[3])
    sim_frames.append(f)
    sim_durations.append(450)

    sim_2x = [sf.resize((w * 2, h * 2), Image.NEAREST) for sf in sim_frames]
    sim_2x[0].save(
        OUT_DIR / "fright_forward_interaction_2x.gif",
        save_all=True,
        append_images=sim_2x[1:],
        duration=sim_durations,
        loop=0,
        disposal=2
    )

    # Copy to Artifact directory
    if ARTIFACT_DIR.exists():
        comp_2x.save(ARTIFACT_DIR / "fright_sound_comparison_2x.png")
        gif_a[0].save(
            ARTIFACT_DIR / "fright_forward_burst_refined_3x.gif",
            save_all=True,
            append_images=gif_a[1:],
            duration=durations,
            loop=0,
            disposal=2
        )
        gif_b[0].save(
            ARTIFACT_DIR / "fright_bonk_style_float_3x.gif",
            save_all=True,
            append_images=gif_b[1:],
            duration=durations,
            loop=0,
            disposal=2
        )
        sim_2x[0].save(
            ARTIFACT_DIR / "fright_forward_interaction_2x.gif",
            save_all=True,
            append_images=sim_2x[1:],
            duration=sim_durations,
            loop=0,
            disposal=2
        )
        print("Copied all comparison assets to artifact directory.")

    print("Fright sound comparison suite built successfully.")

if __name__ == "__main__":
    build_comparison_suite()
