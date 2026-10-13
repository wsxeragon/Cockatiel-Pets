"""Generate demo samples for complete, undeformed sound icon for user review:
Sample 1: Original Bonk sound icon (complete, unmirrored, full scale 1.0) placed at beak top-left (ox=8, oy=20).
Sample 2: Original Bonk sound icon (complete, unmirrored, full scale 1.0) placed slightly higher at (ox=9, oy=18).
Sample 3: Horizontally mirrored complete sound icon (narrow base near beak, full 16px long wedge radiating up-left, ox=18, oy=22, perfectly bounds within x>=2).
"""
from PIL import Image, ImageDraw
from pathlib import Path
import sys

sys.path.append(r"D:\pets\2d-new")
from generate_sprites_q_optimized import bird_q_optimized

OUT_DIR = Path(r"D:\pets\test_complete_burst")
OUT_DIR.mkdir(parents=True, exist_ok=True)
ARTIFACT_DIR = Path(r"C:\Users\26893\.gemini\antigravity\brain\5df30705-c1cf-4a9e-883a-019811f74aae")

C_BURST_YELLOW = "#ffd100"  # Bright golden-yellow rim
C_BURST_ORANGE = "#ff9800"  # Warm deep orange core
C_BURST_DARK = "#4a3b2c"    # 1px outline for clarity

def draw_complete_unmirrored_burst(im, origin=(8, 20)):
    """Sample 1 & 2: Exactly identical to Bonk sound icon at scale=1.0.
    100% undeformed, full slender wedges.
    """
    im = im.copy()
    d = ImageDraw.Draw(im)
    ox, oy = origin
    s = 1.0

    # 1. TOP WEDGE (tall, near-vertical, slightly tilting left)
    top_outer = [
        (ox - 6 * s, oy - 4 * s),
        (ox - 2 * s, oy - 5 * s),
        (ox - 1 * s, oy - 15 * s),
        (ox - 5 * s, oy - 16 * s),
    ]
    top_inner = [
        (ox - 5 * s, oy - 6 * s),
        (ox - 3 * s, oy - 6 * s),
        (ox - 2 * s, oy - 14 * s),
        (ox - 4 * s, oy - 14 * s),
    ]

    # 2. MIDDLE WEDGE (longest, angled at ~35 deg towards top-right, thick & slender body)
    mid_outer = [
        (ox - 1 * s, oy - 1 * s),
        (ox + 1 * s, oy - 4 * s),
        (ox + 14 * s, oy - 10 * s),
        (ox + 16 * s, oy - 5 * s),
        (ox + 11 * s, oy - 2 * s),
    ]
    mid_inner = [
        (ox + 1 * s, oy - 2 * s),
        (ox + 2 * s, oy - 4 * s),
        (ox + 12 * s, oy - 8 * s),
        (ox + 14 * s, oy - 5 * s),
        (ox + 10 * s, oy - 3 * s),
    ]

    # 3. BOTTOM WEDGE (horizontal-ish, widening to right)
    bot_outer = [
        (ox + 2 * s, oy + 2 * s),
        (ox + 3 * s, oy + 6 * s),
        (ox + 12 * s, oy + 7 * s),
        (ox + 13 * s, oy + 2 * s),
    ]
    bot_inner = [
        (ox + 3 * s, oy + 3 * s),
        (ox + 4 * s, oy + 5 * s),
        (ox + 11 * s, oy + 6 * s),
        (ox + 11 * s, oy + 3 * s),
    ]

    wedges = [(top_outer, top_inner), (mid_outer, mid_inner), (bot_outer, bot_inner)]
    for outer, inner in wedges:
        outer_pts = [(round(x), round(y)) for x, y in outer]
        inner_pts = [(round(x), round(y)) for x, y in inner]
        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            d.polygon([(x + dx, y + dy) for x, y in outer_pts], fill=C_BURST_DARK)
        d.polygon(outer_pts, fill=C_BURST_YELLOW)
        d.polygon(inner_pts, fill=C_BURST_ORANGE)

    return im

def draw_complete_mirrored_burst(im, origin=(18, 22)):
    """Sample 3: Complete Bonk icon horizontally mirrored (radiating towards front-left).
    Base at (18, 22) above beak, long middle wedge extends to x=2, perfectly undeformed!
    """
    im = im.copy()
    d = ImageDraw.Draw(im)
    ox, oy = origin
    s = 1.0

    # 1. TOP WEDGE (mirrored x)
    top_outer = [
        (ox + 6 * s, oy - 4 * s),
        (ox + 2 * s, oy - 5 * s),
        (ox + 1 * s, oy - 15 * s),
        (ox + 5 * s, oy - 16 * s),
    ]
    top_inner = [
        (ox + 5 * s, oy - 6 * s),
        (ox + 3 * s, oy - 6 * s),
        (ox + 2 * s, oy - 14 * s),
        (ox + 4 * s, oy - 14 * s),
    ]

    # 2. MIDDLE WEDGE (longest, angled towards top-left)
    mid_outer = [
        (ox + 1 * s, oy - 1 * s),
        (ox - 1 * s, oy - 4 * s),
        (ox - 14 * s, oy - 10 * s),
        (ox - 16 * s, oy - 5 * s),
        (ox - 11 * s, oy - 2 * s),
    ]
    mid_inner = [
        (ox - 1 * s, oy - 2 * s),
        (ox - 2 * s, oy - 4 * s),
        (ox - 12 * s, oy - 8 * s),
        (ox - 14 * s, oy - 5 * s),
        (ox - 10 * s, oy - 3 * s),
    ]

    # 3. BOTTOM WEDGE (horizontal-ish, widening to left)
    bot_outer = [
        (ox - 2 * s, oy + 2 * s),
        (ox - 3 * s, oy + 6 * s),
        (ox - 12 * s, oy + 7 * s),
        (ox - 13 * s, oy + 2 * s),
    ]
    bot_inner = [
        (ox - 3 * s, oy + 3 * s),
        (ox - 4 * s, oy + 5 * s),
        (ox - 11 * s, oy + 6 * s),
        (ox - 11 * s, oy + 3 * s),
    ]

    wedges = [(top_outer, top_inner), (mid_outer, mid_inner), (bot_outer, bot_inner)]
    for outer, inner in wedges:
        outer_pts = [(round(x), round(y)) for x, y in outer]
        inner_pts = [(round(x), round(y)) for x, y in inner]
        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            d.polygon([(x + dx, y + dy) for x, y in outer_pts], fill=C_BURST_DARK)
        d.polygon(outer_pts, fill=C_BURST_YELLOW)
        d.polygon(inner_pts, fill=C_BURST_ORANGE)

    return im

def build_all_samples():
    # Base bird frames
    # Frame 0: Startled (closed mouth)
    f0 = bird_q_optimized(head=(1, -2), body_roll=1, tail_wag=-1, crest="alert", eye="wide", mouth="closed")
    # Frame 1: Beak open
    f1_base = bird_q_optimized(head=(-1, -1), body_roll=-1, tail_wag=3, crest="alert", eye="wide", mouth="bite")
    # Frame 2: Beak open hold
    f2_base = bird_q_optimized(head=(0, 0), body_roll=-1, tail_wag=2, crest="alert", eye="wide", mouth="bite")
    # Frame 3: Recoil closed mouth
    f3 = bird_q_optimized(head=(-1, -1), body_roll=0, tail_wag=1, crest="alert", eye="wide", mouth="closed")

    # Sample 1: Original Bonk Icon at Beak Top-Left (ox=8, oy=20)
    s1_f1 = draw_complete_unmirrored_burst(f1_base, origin=(8, 21))
    s1_f2 = draw_complete_unmirrored_burst(f2_base, origin=(8, 20))
    s1_frames = [f0, s1_f1, s1_f2, f3]

    # Sample 2: Original Bonk Icon Slightly Higher (ox=9, oy=18)
    s2_f1 = draw_complete_unmirrored_burst(f1_base, origin=(9, 18))
    s2_f2 = draw_complete_unmirrored_burst(f2_base, origin=(9, 17))
    s2_frames = [f0, s2_f1, s2_f2, f3]

    # Sample 3: Mirrored Complete Icon fanning forward-up (ox=18, oy=22)
    s3_f1 = draw_complete_mirrored_burst(f1_base, origin=(18, 23))
    s3_f2 = draw_complete_mirrored_burst(f2_base, origin=(18, 22))
    s3_frames = [f0, s3_f1, s3_f2, f3]

    durations = [140, 180, 240, 320, 360]

    # Generate 3x GIFs for all 3 samples
    def make_gif(frames, out_name):
        scaled = [f.resize((300, 240), Image.NEAREST) for f in [frames[0], frames[1], frames[2], frames[3], frames[3]]]
        scaled[0].save(
            OUT_DIR / out_name,
            save_all=True,
            append_images=scaled[1:],
            duration=durations,
            loop=0,
            disposal=2
        )
        if ARTIFACT_DIR.exists():
            scaled[0].save(
                ARTIFACT_DIR / out_name,
                save_all=True,
                append_images=scaled[1:],
                duration=durations,
                loop=0,
                disposal=2
            )

    make_gif(s1_frames, "sample1_complete_burst_topleft_3x.gif")
    make_gif(s2_frames, "sample2_complete_burst_high_3x.gif")
    make_gif(s3_frames, "sample3_complete_burst_forward_3x.gif")

    # Generate comparison spritesheet: 3 rows x 4 columns
    comp_w = 100 * 4
    comp_h = 80 * 3 + 20
    comp_img = Image.new("RGBA", (comp_w, comp_h), (245, 247, 250, 255))
    d_comp = ImageDraw.Draw(comp_img)

    all_samples = [s1_frames, s2_frames, s3_frames]
    for row_idx, sf in enumerate(all_samples):
        y_off = row_idx * 90
        for col_idx in range(4):
            x_off = col_idx * 100
            comp_img.paste(sf[col_idx], (x_off, y_off), sf[col_idx])
            if col_idx > 0:
                d_comp.line([(x_off, y_off), (x_off, y_off + 80)], fill="#d5dae2")
        if row_idx < 2:
            d_comp.line([(0, y_off + 85), (comp_w, y_off + 85)], fill="#b0b8c4", width=2)

    comp_2x = comp_img.resize((comp_w * 2, comp_h * 2), Image.NEAREST)
    comp_2x.save(OUT_DIR / "complete_burst_3samples_comparison_2x.png")
    if ARTIFACT_DIR.exists():
        comp_2x.save(ARTIFACT_DIR / "complete_burst_3samples_comparison_2x.png")

    # Interaction simulation GIF for Sample 1
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
    for step in range(3):
        f = base_bg.copy()
        f.paste(s1_frames[3], (25, 10), s1_frames[3])
        cx = 120 - step * 25
        cy = 30 + step * 8
        f.paste(cursor, (cx, cy), cursor)
        sim_frames.append(f)
        sim_durations.append(150)

    click_f = base_bg.copy()
    click_f.paste(s1_frames[0], (25, 10), s1_frames[0])
    d_click = ImageDraw.Draw(click_f)
    d_click.ellipse((85, 48, 93, 56), fill="#ffd100", outline="#353438")
    click_f.paste(cursor, (80, 42), cursor)
    sim_frames.append(click_f)
    sim_durations.append(130)

    for b_idx in [1, 2, 3]:
        f = base_bg.copy()
        f.paste(s1_frames[b_idx], (25, 10), s1_frames[b_idx])
        f.paste(cursor, (90 + b_idx * 5, 36 - b_idx * 3), cursor)
        sim_frames.append(f)
        sim_durations.append(180)

    f_settle = base_bg.copy()
    f_settle.paste(s1_frames[3], (25, 10), s1_frames[3])
    sim_frames.append(f_settle)
    sim_durations.append(450)

    sim_2x = [sf.resize((w * 2, h * 2), Image.NEAREST) for sf in sim_frames]
    sim_2x[0].save(
        OUT_DIR / "sample1_poke_interaction_2x.gif",
        save_all=True,
        append_images=sim_2x[1:],
        duration=sim_durations,
        loop=0,
        disposal=2
    )
    if ARTIFACT_DIR.exists():
        sim_2x[0].save(
            ARTIFACT_DIR / "sample1_poke_interaction_2x.gif",
            save_all=True,
            append_images=sim_2x[1:],
            duration=sim_durations,
            loop=0,
            disposal=2
        )

    print("Generated all 3 complete burst samples successfully!")

if __name__ == "__main__":
    build_all_samples()
