"""Updated test script: Fright notes with greater distance from beak shell.
Singing notes untouched.
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

def draw_distant_beak_notes(im, beak_tip=(13, 35), stage=1):
    """Draw music notes with clear, airy distance from the beak shell."""
    im = im.copy()
    d = ImageDraw.Draw(im)
    bx, by = beak_tip

    outline = "#2b2a2e"
    c_blue = "#54c2eb"
    c_gold = "#ffd200"

    if stage == 1:
        # Note 1: Floating clearly away from the beak
        # Beak tip is at bx=13, by=35.
        # Place note center at x=4..7, y=18..23 -> around 12-15px away!
        nx = 2
        ny = by - 16  # y around 19

        # Single eighth note ♪
        d.rectangle((nx + 4, ny, nx + 6, ny + 9), fill=outline)
        d.ellipse((nx, ny + 6, nx + 6, ny + 11), fill=outline)
        d.polygon([(nx + 5, ny), (nx + 10, ny - 2), (nx + 11, ny), (nx + 6, ny + 3)], fill=outline)

        d.rectangle((nx + 5, ny + 1, nx + 5, ny + 8), fill=c_blue)
        d.ellipse((nx + 1, ny + 7, nx + 5, ny + 10), fill=c_blue)
        d.point((nx + 2, ny + 8), fill="#ffffff")

        # Subtle sound pulse ripples between beak and note
        d.line([(bx - 3, by - 3), (bx - 2, by - 5)], fill="#ffd200")
        d.point((bx - 5, by - 8), fill="#ffd200")

    elif stage == 2:
        # Note 1 has floated even further up-left:
        nx1 = 1
        ny1 = by - 23  # y around 12

        d.rectangle((nx1 + 4, ny1, nx1 + 6, ny1 + 9), fill=outline)
        d.ellipse((nx1, ny1 + 6, nx1 + 6, ny1 + 11), fill=outline)
        d.polygon([(nx1 + 5, ny1), (nx1 + 10, ny1 - 2), (nx1 + 11, ny1), (nx1 + 6, ny1 + 3)], fill=outline)

        d.rectangle((nx1 + 5, ny1 + 1, nx1 + 5, ny1 + 8), fill=c_blue)
        d.ellipse((nx1 + 1, ny1 + 7, nx1 + 5, ny1 + 10), fill=c_blue)
        d.point((nx1 + 2, ny1 + 8), fill="#ffffff")

        # Note 2: Trailing second note (golden), also keeping distance from beak (x=7, y=21)
        nx2 = 7
        ny2 = by - 14  # y around 21

        d.rectangle((nx2 + 3, ny2, nx2 + 4, ny2 + 6), fill=outline)
        d.ellipse((nx2, ny2 + 4, nx2 + 4, ny2 + 8), fill=outline)
        d.point((nx2 + 4, ny2), fill=outline)

        d.point((nx2 + 3, ny2 + 1), fill=c_gold)
        d.point((nx2 + 3, ny2 + 2), fill=c_gold)
        d.point((nx2 + 3, ny2 + 3), fill=c_gold)
        d.ellipse((nx2 + 1, ny2 + 5, nx2 + 3, ny2 + 7), fill=c_gold)
        d.point((nx2 + 2, ny2 + 5), fill="#ffffff")

        # Tiny ripple arc near mouth
        d.point((bx - 3, by - 2), fill="#54c2eb")

    return im

def build_distant_note_frames():
    # 4 Frames:
    # Frame 0: 受惊蓄力 (Startled)
    f0 = bird_q_optimized(
        head=(1, -2), body_roll=1, tail_wag=-1,
        crest="alert", eye="wide", mouth="closed"
    )

    # Frame 1: 张嘴尖叫发声 (Shriek - note pops out with clear distance in front of beak)
    # Head at head=(-4, -1), beak tip is at x=13, y=35
    f1_base = bird_q_optimized(
        head=(-4, -1), body_roll=-2, tail_wag=3,
        crest="alert", eye="wide", mouth="bite"
    )
    f1 = draw_distant_beak_notes(f1_base, beak_tip=(13, 35), stage=1)

    # Frame 2: 发声共鸣 (Peak Vocalization - notes float higher & further away)
    f2_base = bird_q_optimized(
        head=(-3, 0), body_roll=-1, tail_wag=2,
        crest="alert", eye="wide", mouth="bite"
    )
    f2 = draw_distant_beak_notes(f2_base, beak_tip=(14, 36), stage=2)

    # Frame 3: 叫罢收身戒备 (Settle & Alert)
    f3 = bird_q_optimized(
        head=(-1, -1), body_roll=0, tail_wag=1,
        crest="alert", eye="wide", mouth="closed"
    )

    frames = [f0, f1, f2, f3]

    for idx, f in enumerate(frames):
        f.save(OUT_DIR / f"distant_note_{idx}.png")

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
    sheet_2x.save(OUT_DIR / "distant_note_spritesheet_2x.png")

    # Animated GIF (3x)
    durations = [140, 160, 220, 300, 350]
    gif_frames = [f0, f1, f2, f3, f3]
    scaled_gif = [f.resize((300, 240), Image.NEAREST) for f in gif_frames]
    scaled_gif[0].save(
        OUT_DIR / "fright_distant_note_3x.gif",
        save_all=True,
        append_images=scaled_gif[1:],
        duration=durations,
        loop=0,
        disposal=2
    )

    # Mouse Interaction Simulation GIF (2x)
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

    # Reaction
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
        OUT_DIR / "fright_distant_note_interaction_2x.gif",
        save_all=True,
        append_images=sim_2x[1:],
        duration=sim_durations,
        loop=0,
        disposal=2
    )

    # Copy to artifacts directory
    if ARTIFACT_DIR.exists():
        sheet_2x.save(ARTIFACT_DIR / "distant_note_spritesheet_2x.png")
        scaled_gif[0].save(
            ARTIFACT_DIR / "fright_distant_note_3x.gif",
            save_all=True,
            append_images=scaled_gif[1:],
            duration=durations,
            loop=0,
            disposal=2
        )
        sim_2x[0].save(
            ARTIFACT_DIR / "fright_distant_note_interaction_2x.gif",
            save_all=True,
            append_images=sim_2x[1:],
            duration=sim_durations,
            loop=0,
            disposal=2
        )
        print("Copied distant note assets to artifacts directory.")

    print("Generated distant note preview successfully.")

if __name__ == "__main__":
    build_distant_note_frames()
