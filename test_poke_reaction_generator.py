"""Preview generator for Cockatiel Poke Reaction (touch body -> bite/react)
with sound / note effects.
Generates:
1. Version A: With custom 3-wedge golden-orange sound burst (from user's uploaded reference)
2. Version B: With bright music note (♪ / ♫) effect
3. Side-by-side comparison GIFs and interactive click-simulation GIF.
"""
from pathlib import Path
from PIL import Image, ImageDraw
import sys
import shutil

sys.path.append(r"D:\pets\2d-new")
from generate_sprites_q_optimized import bird_q_optimized, C

sys.path.append(r"D:\pets")
from test_bonk_with_user_icon import draw_procedural_burst

OUT_DIR = Path(r"D:\pets\test_poke")
OUT_DIR.mkdir(parents=True, exist_ok=True)
ARTIFACT_DIR = Path(r"C:\Users\26893\.gemini\antigravity\brain\5df30705-c1cf-4a9e-883a-019811f74aae")

def draw_music_notes(im, origin=(36, 18), stage=2, color="#64c0eb", outline="#2b2a2e"):
    """Draw vibrant music note(s) 🎵 floating above cockatiel's head."""
    if stage == 0:
        return im
    im = im.copy()
    d = ImageDraw.Draw(im)
    ox, oy = origin

    # Single or double eighth notes
    # Note 1: main note
    nx1 = ox
    ny1 = oy - (2 if stage == 2 else 5)
    
    # Draw double eighth note
    # Outline
    d.rectangle((nx1 + 1, ny1, nx1 + 4, ny1 + 10), fill=outline)
    d.rectangle((nx1 + 8, ny1 - 1, nx1 + 11, ny1 + 9), fill=outline)
    d.polygon([(nx1 + 1, ny1), (nx1 + 10, ny1 - 2), (nx1 + 11, ny1 + 1), (nx1 + 2, ny1 + 3)], fill=outline)
    d.ellipse((nx1 - 3, ny1 + 7, nx1 + 3, ny1 + 13), fill=outline)
    d.ellipse((nx1 + 5, ny1 + 6, nx1 + 11, ny1 + 12), fill=outline)

    # Fill
    d.rectangle((nx1 + 2, ny1 + 1, nx1 + 3, ny1 + 9), fill=color)
    d.rectangle((nx1 + 9, ny1, nx1 + 10, ny1 + 8), fill=color)
    d.polygon([(nx1 + 2, ny1 + 1), (nx1 + 9, ny1 - 1), (nx1 + 10, ny1 + 1), (nx1 + 3, ny1 + 2)], fill=color)
    d.ellipse((nx1 - 2, ny1 + 8, nx1 + 2, ny1 + 12), fill=color)
    d.ellipse((nx1 + 6, ny1 + 7, nx1 + 10, ny1 + 11), fill=color)
    # Highlight
    d.point((nx1 - 1, ny1 + 9), fill="#ffffff")
    d.point((nx1 + 7, ny1 + 8), fill="#ffffff")

    if stage >= 2:
        # Smaller 2nd note floating higher to the right
        nx2 = ox + 15
        ny2 = oy - 8
        d.rectangle((nx2 + 5, ny2 - 1, nx2 + 7, ny2 + 6), fill=outline)
        d.ellipse((nx2 + 1, ny2 + 4, nx2 + 6, ny2 + 9), fill=outline)
        d.polygon([(nx2 + 6, ny2 - 1), (nx2 + 10, ny2 - 3), (nx2 + 10, ny2 - 1), (nx2 + 6, ny2 + 1)], fill=outline)

        d.rectangle((nx2 + 6, ny2, nx2 + 6, ny2 + 5), fill="#ffd100")
        d.ellipse((nx2 + 2, ny2 + 5, nx2 + 5, ny2 + 8), fill="#ffd100")
        d.point((nx2 + 3, ny2 + 6), fill="#ffffff")

    return im

def build_poke_frames(effect_type="burst"):
    """Build the 4-frame poke-reaction sequence.
    effect_type:
      'burst': Uses the user's custom 3-wedge golden-orange sound burst
      'note': Uses floating vibrant musical note(s)
      'none': Base reaction without effect
    """
    # Frame 0: 戳中受惊 (Poke impact: body recoils slightly, eyes go wide)
    f0 = bird_q_optimized(
        head=(1, -2),
        body_roll=1,
        tail_wag=-1,
        crest="alert",
        eye="wide",
        mouth="closed"
    )

    # Frame 1: 迅猛反咬出击 (Fierce Snap! Beak wide open, lunging forward)
    f1 = bird_q_optimized(
        head=(-9, -1),
        body_roll=-3,
        tail_wag=4,
        crest="alert",
        eye="wide",
        mouth="bite"
    )
    # Add effect at peak bite
    if effect_type == "burst":
        f1 = draw_procedural_burst(f1, origin=(36, 17), stage=2, scale=0.9, with_dark_edge=True)
    elif effect_type == "note":
        f1 = draw_music_notes(f1, origin=(36, 17), stage=1)

    # Frame 2: 咬合顿挫 (Chomp & Hold: head reaches forward, mouth bites, full effect resonance)
    f2 = bird_q_optimized(
        head=(-6, 0),
        body_roll=-2,
        tail_wag=3,
        crest="alert",
        eye="wide",
        mouth="bite"
    )
    if effect_type == "burst":
        f2 = draw_procedural_burst(f2, origin=(37, 16), stage=3, scale=1.05, with_dark_edge=True)
    elif effect_type == "note":
        f2 = draw_music_notes(f2, origin=(36, 15), stage=2)

    # Frame 3: 戒备收身 (Recoil / Hiss warning: settle back, effect dissipates)
    f3 = bird_q_optimized(
        head=(-2, -1),
        body_roll=0,
        tail_wag=1,
        crest="alert",
        eye="open",
        mouth="closed"
    )

    return [f0, f1, f2, f3]

def generate_preview_suite():
    frames_burst = build_poke_frames("burst")
    frames_note = build_poke_frames("note")

    # Save individual frames
    for idx, f in enumerate(frames_burst):
        f.save(OUT_DIR / f"poke_burst_{idx}.png")
    for idx, f in enumerate(frames_note):
        f.save(OUT_DIR / f"poke_note_{idx}.png")

    # 1. Comparison Spritesheet (Burst vs Note)
    sheet_w = 100 * 4
    sheet_h = 80 * 2 + 10
    sheet = Image.new("RGBA", (sheet_w, sheet_h), (245, 247, 250, 255))
    d_sheet = ImageDraw.Draw(sheet)

    # Row 1: Burst
    for idx, f in enumerate(frames_burst):
        sheet.paste(f, (idx * 100, 0), f)
        if idx > 0:
            d_sheet.line([(idx * 100, 0), (idx * 100, 80)], fill="#d5dae2")

    # Separator
    d_sheet.line([(0, 85), (sheet_w, 85)], fill="#b0b7c2", width=2)

    # Row 2: Note
    for idx, f in enumerate(frames_note):
        sheet.paste(f, (idx * 100, 90), f)
        if idx > 0:
            d_sheet.line([(idx * 100, 90), (idx * 100, 170)], fill="#d5dae2")

    sheet_2x = sheet.resize((sheet_w * 2, sheet_h * 2), Image.NEAREST)
    sheet_2x.save(OUT_DIR / "poke_comparison_sheet_2x.png")

    # 2. Animated GIFs for each
    durations = [120, 150, 200, 250]
    
    # Version A: Burst GIF (3x)
    burst_3x = [f.resize((300, 240), Image.NEAREST) for f in frames_burst]
    # Add idle stand at end for loop pause
    burst_3x.append(burst_3x[3])
    burst_dur = durations + [400]
    burst_3x[0].save(
        OUT_DIR / "poke_reaction_burst_3x.gif",
        save_all=True,
        append_images=burst_3x[1:],
        duration=burst_dur,
        loop=0,
        disposal=2
    )

    # Version B: Note GIF (3x)
    note_3x = [f.resize((300, 240), Image.NEAREST) for f in frames_note]
    note_3x.append(note_3x[3])
    note_3x[0].save(
        OUT_DIR / "poke_reaction_note_3x.gif",
        save_all=True,
        append_images=note_3x[1:],
        duration=burst_dur,
        loop=0,
        disposal=2
    )

    # 3. INTERACTIVE CLICK-SIMULATION GIF:
    # Shows cursor pointing hand clicking bird's body -> bird reacts and snaps!
    sim_frames = []
    sim_durations = []
    w, h = 160, 100
    base_bg = Image.new("RGBA", (w, h), (248, 249, 250, 255))
    d_bg = ImageDraw.Draw(base_bg)
    d_bg.line([(0, 87), (w, 87)], fill="#d8dde4", width=1)

    # Simple pixel pointer hand / cursor
    cursor = Image.new("RGBA", (20, 20), (0, 0, 0, 0))
    d_cur = ImageDraw.Draw(cursor)
    # Simple mouse arrow cursor
    arrow_pts = [(0, 0), (0, 14), (4, 11), (7, 16), (9, 15), (6, 10), (11, 10)]
    d_cur.polygon(arrow_pts, fill="#ffffff", outline="#2b2a2e")

    # Step 1: Idle bird, cursor approaches body
    for step in range(3):
        f = base_bg.copy()
        f.paste(frames_burst[3], (25, 10), frames_burst[3])
        # Cursor pos
        cx = 120 - step * 25
        cy = 30 + step * 8
        f.paste(cursor, (cx, cy), cursor)
        sim_frames.append(f)
        sim_durations.append(150)

    # Step 2: Click! (Poke on body)
    click_f = base_bg.copy()
    click_f.paste(frames_burst[0], (25, 10), frames_burst[0])
    # Click star
    d_click = ImageDraw.Draw(click_f)
    d_click.ellipse((85, 48, 93, 56), fill="#ffd100", outline="#353438")
    click_f.paste(cursor, (80, 42), cursor)
    sim_frames.append(click_f)
    sim_durations.append(130)

    # Step 3: Snap bite with burst effect!
    for b_idx in [1, 2, 3]:
        f = base_bg.copy()
        f.paste(frames_burst[b_idx], (25, 10), frames_burst[b_idx])
        # Cursor recoiling back in surprise
        f.paste(cursor, (88 + b_idx * 6, 38 - b_idx * 4), cursor)
        sim_frames.append(f)
        sim_durations.append(160)

    # Step 4: Settle
    f = base_bg.copy()
    f.paste(frames_burst[3], (25, 10), frames_burst[3])
    sim_frames.append(f)
    sim_durations.append(400)

    sim_2x = [sf.resize((w * 2, h * 2), Image.NEAREST) for sf in sim_frames]
    sim_2x[0].save(
        OUT_DIR / "poke_interaction_simulation_2x.gif",
        save_all=True,
        append_images=sim_2x[1:],
        duration=sim_durations,
        loop=0,
        disposal=2
    )

    # Copy all assets to artifact directory
    if ARTIFACT_DIR.exists():
        shutil.copy(OUT_DIR / "poke_comparison_sheet_2x.png", ARTIFACT_DIR / "poke_comparison_sheet_2x.png")
        shutil.copy(OUT_DIR / "poke_reaction_burst_3x.gif", ARTIFACT_DIR / "poke_reaction_burst_3x.gif")
        shutil.copy(OUT_DIR / "poke_reaction_note_3x.gif", ARTIFACT_DIR / "poke_reaction_note_3x.gif")
        shutil.copy(OUT_DIR / "poke_interaction_simulation_2x.gif", ARTIFACT_DIR / "poke_interaction_simulation_2x.gif")
        print("Copied poke preview assets to artifact directory.")

    print("Poke reaction suite generated successfully in D:\\pets\\test_poke")

if __name__ == "__main__":
    generate_preview_suite()
