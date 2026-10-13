"""Comprehensive generator comparing sound/note placements in front of the beak during fright.
Style 1: Pure crisp Music Notes (♪ ♫ emerging from mouth)
Style 2: Sound Burst Wedges (radiating out from open mouth)
Style 3: Note with subtle sound vibration ripples
"""
from PIL import Image, ImageDraw
from pathlib import Path
import shutil
import sys

sys.path.append(r"D:\pets\2d-new")
from generate_sprites_q_optimized import bird_q_optimized, C

OUT_DIR = Path(r"D:\pets\test_fright_note")
OUT_DIR.mkdir(parents=True, exist_ok=True)
ARTIFACT_DIR = Path(r"C:\Users\26893\.gemini\antigravity\brain\5df30705-c1cf-4a9e-883a-019811f74aae")

def draw_beak_notes_refined(im, mouth_pos=(12, 38), stage=1):
    """Draw crisp musical notes floating out from the mouth opening."""
    im = im.copy()
    d = ImageDraw.Draw(im)
    mx, my = mouth_pos

    outline = "#2b2a2e"
    c_blue = "#54c2eb"
    c_gold = "#ffd200"

    if stage == 1:
        # Note 1 emerging from mouth gap, angled upwards
        nx = max(3, mx - 8)
        ny = my - 13

        # Single eighth note ♪
        d.rectangle((nx + 4, ny, nx + 6, ny + 9), fill=outline)
        d.ellipse((nx, ny + 6, nx + 6, ny + 11), fill=outline)
        d.polygon([(nx + 5, ny), (nx + 10, ny - 2), (nx + 11, ny), (nx + 6, ny + 3)], fill=outline)

        d.rectangle((nx + 5, ny + 1, nx + 5, ny + 8), fill=c_blue)
        d.ellipse((nx + 1, ny + 7, nx + 5, ny + 10), fill=c_blue)
        d.point((nx + 2, ny + 8), fill="#ffffff")

        # Tiny sound pulse dot at mouth
        d.point((mx - 2, my - 2), fill=c_gold)

    elif stage == 2:
        # Note 1 floated higher & further:
        nx1 = max(1, mx - 10)
        ny1 = my - 19

        d.rectangle((nx1 + 4, ny1, nx1 + 6, ny1 + 9), fill=outline)
        d.ellipse((nx1, ny1 + 6, nx1 + 6, ny1 + 11), fill=outline)
        d.polygon([(nx1 + 5, ny1), (nx1 + 10, ny1 - 2), (nx1 + 11, ny1), (nx1 + 6, ny1 + 3)], fill=outline)

        d.rectangle((nx1 + 5, ny1 + 1, nx1 + 5, ny1 + 8), fill=c_blue)
        d.ellipse((nx1 + 1, ny1 + 7, nx1 + 5, ny1 + 10), fill=c_blue)
        d.point((nx1 + 2, ny1 + 8), fill="#ffffff")

        # Note 2: Smaller fresh golden note right at mouth opening
        nx2 = max(4, mx - 5)
        ny2 = my - 9

        d.rectangle((nx2 + 3, ny2, nx2 + 4, ny2 + 6), fill=outline)
        d.ellipse((nx2, ny2 + 4, nx2 + 4, ny2 + 8), fill=outline)
        d.point((nx2 + 4, ny2), fill=outline)

        d.point((nx2 + 3, ny2 + 1), fill=c_gold)
        d.point((nx2 + 3, ny2 + 2), fill=c_gold)
        d.point((nx2 + 3, ny2 + 3), fill=c_gold)
        d.ellipse((nx2 + 1, ny2 + 5, nx2 + 3, ny2 + 7), fill=c_gold)
        d.point((nx2 + 2, ny2 + 5), fill="#ffffff")

    return im

def draw_beak_burst(im, mouth_pos=(12, 38), stage=1):
    """Draw the 3-wedge golden-orange sound burst radiating out of the mouth."""
    im = im.copy()
    d = ImageDraw.Draw(im)
    mx, my = mouth_pos

    s = 0.7 if stage == 1 else 0.95
    # Radiates to the left (out of beak)
    # Wedge 1: upper-left
    top_outer = [(mx - 2, my - 4), (mx - 4, my - 2), (mx - 10 * s, my - 10 * s), (mx - 6 * s, my - 12 * s)]
    top_inner = [(mx - 3, my - 4), (mx - 4, my - 3), (mx - 9 * s, my - 9 * s), (mx - 7 * s, my - 10 * s)]

    # Wedge 2: straight left (longest)
    mid_outer = [(mx - 2, my - 1), (mx - 2, my + 3), (mx - 12 * s, my + 1), (mx - 13 * s, my - 3)]
    mid_inner = [(mx - 3, my), (mx - 3, my + 2), (mx - 11 * s, my + 1), (mx - 11 * s, my - 2)]

    # Wedge 3: lower-left
    bot_outer = [(mx - 1, my + 4), (mx - 3, my + 5), (mx - 9 * s, my + 11 * s), (mx - 6 * s, my + 12 * s)]
    bot_inner = [(mx - 2, my + 5), (mx - 3, my + 6), (mx - 8 * s, my + 10 * s), (mx - 6 * s, my + 11 * s)]

    c_yellow = "#ffd100"
    c_orange = "#ff9800"
    c_dark = "#4a3b2c"

    for outer, inner in [(top_outer, top_inner), (mid_outer, mid_inner), (bot_outer, bot_inner)]:
        outer_pts = [(round(x), round(y)) for x, y in outer]
        inner_pts = [(round(x), round(y)) for x, y in inner]
        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            d.polygon([(x + dx, y + dy) for x, y in outer_pts], fill=c_dark)
        d.polygon(outer_pts, fill=c_yellow)
        d.polygon(inner_pts, fill=c_orange)

    return im

def build_suite():
    # Base bird frames:
    # 0: Startled (crouch back, wide eyes)
    f0 = bird_q_optimized(head=(1, -2), body_roll=1, tail_wag=-1, crest="alert", eye="wide", mouth="closed")
    # 1: Open beak snap!
    f1_base = bird_q_optimized(head=(-6, -1), body_roll=-2, tail_wag=3, crest="alert", eye="wide", mouth="bite")
    # 2: Peak bite hold!
    f2_base = bird_q_optimized(head=(-5, 0), body_roll=-2, tail_wag=3, crest="alert", eye="wide", mouth="bite")
    # 3: Settle
    f3 = bird_q_optimized(head=(-1, -1), body_roll=0, tail_wag=1, crest="alert", eye="wide", mouth="closed")

    # Mouth origin:
    # hx = 33 - 6 - 1 = 26, hy = 32. Mouth is at (hx - 14, hy + 6) = (12, 38)
    m1 = (12, 38)
    m2 = (13, 39)

    # Style 1: Notes
    f1_note = draw_beak_notes_refined(f1_base, mouth_pos=m1, stage=1)
    f2_note = draw_beak_notes_refined(f2_base, mouth_pos=m2, stage=2)
    frames_note = [f0, f1_note, f2_note, f3]

    # Style 2: Sound Burst
    f1_burst = draw_beak_burst(f1_base, mouth_pos=m1, stage=1)
    f2_burst = draw_beak_burst(f2_base, mouth_pos=m2, stage=2)
    frames_burst = [f0, f1_burst, f2_burst, f3]

    for i, f in enumerate(frames_note):
        f.save(OUT_DIR / f"beak_note_{i}.png")
    for i, f in enumerate(frames_burst):
        f.save(OUT_DIR / f"beak_burst_{i}.png")

    # Comparison spritesheet
    sheet = Image.new("RGBA", (400, 170), (245, 247, 250, 255))
    d_s = ImageDraw.Draw(sheet)
    for i, f in enumerate(frames_note):
        sheet.paste(f, (i * 100, 0), f)
        if i > 0:
            d_s.line([(i * 100, 0), (i * 100, 80)], fill="#d5dae2")
    d_s.line([(0, 85), (400, 85)], fill="#b0b7c2", width=2)
    for i, f in enumerate(frames_burst):
        sheet.paste(f, (i * 100, 90), f)
        if i > 0:
            d_s.line([(i * 100, 90), (i * 100, 170)], fill="#d5dae2")

    sheet_2x = sheet.resize((800, 340), Image.NEAREST)
    sheet_2x.save(OUT_DIR / "beak_sound_comparison_2x.png")

    # Animated GIFs
    durations = [140, 160, 220, 300, 350]
    
    # Note GIF
    g_note = [f0, f1_note, f2_note, f3, f3]
    g_note_3x = [f.resize((300, 240), Image.NEAREST) for f in g_note]
    g_note_3x[0].save(
        OUT_DIR / "beak_notes_fright_3x.gif",
        save_all=True,
        append_images=g_note_3x[1:],
        duration=durations,
        loop=0,
        disposal=2
    )

    # Burst GIF
    g_burst = [f0, f1_burst, f2_burst, f3, f3]
    g_burst_3x = [f.resize((300, 240), Image.NEAREST) for f in g_burst]
    g_burst_3x[0].save(
        OUT_DIR / "beak_burst_fright_3x.gif",
        save_all=True,
        append_images=g_burst_3x[1:],
        duration=durations,
        loop=0,
        disposal=2
    )

    # Copy to artifacts directory
    if ARTIFACT_DIR.exists():
        sheet_2x.save(ARTIFACT_DIR / "beak_sound_comparison_2x.png")
        g_note_3x[0].save(
            ARTIFACT_DIR / "beak_notes_fright_3x.gif",
            save_all=True,
            append_images=g_note_3x[1:],
            duration=durations,
            loop=0,
            disposal=2
        )
        g_burst_3x[0].save(
            ARTIFACT_DIR / "beak_burst_fright_3x.gif",
            save_all=True,
            append_images=g_burst_3x[1:],
            duration=durations,
            loop=0,
            disposal=2
        )
        print("Copied beak sound preview assets to artifact directory.")

    print("Beak sound preview suite built successfully.")

if __name__ == "__main__":
    build_suite()
