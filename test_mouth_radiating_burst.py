"""Mouth-Emitted Radiating Sound Wave Suite (从嘴巴发出的辐射型拟声波):
The wedges radiate OUTWARDS (辐射型) from the mouth (狭窄端靠近嘴巴，宽口端向嘴巴前方展开).
Colors: Outer golden-yellow #ffd100, inner warm-orange #ff9800, dark outline #4a3b2c.
Generates:
Option A: Standard Beak Radiation (间距 4~5px，紧贴嘴前发散)
Option B: Airy Beak Radiation (间距 7~8px，留出更明显空隙，但辐射中心严格对准嘴腔)
"""
import math
from pathlib import Path
from PIL import Image, ImageDraw
import sys

sys.path.append(r"D:\pets\2d-new")
from generate_sprites_q_optimized import bird_q_optimized

OUT_DIR = Path(r"D:\pets\test_mouth_burst")
OUT_DIR.mkdir(parents=True, exist_ok=True)
ARTIFACT_DIR = Path(r"C:\Users\26893\.gemini\antigravity\brain\5df30705-c1cf-4a9e-883a-019811f74aae")

C_BURST_YELLOW = "#ffd100"  # Bright golden-yellow outer rim
C_BURST_ORANGE = "#ff9800"  # Warm deep orange core
C_BURST_DARK = "#4a3b2c"    # 1px outline for clarity

def make_radiating_wedge(origin, angle_deg, r_start, r_end, w_start, w_end):
    """Generate a wedge radiating from origin at angle_deg (in degrees, 180=left, 90=up).
    Narrow base at r_start with half-width w_start.
    Wide tip at r_end with half-width w_end.
    Returns (outer_polygon, inner_polygon).
    """
    ox, oy = origin
    rad = math.radians(angle_deg)
    # Unit direction vector
    ux = math.cos(rad)
    uy = -math.sin(rad)  # Screen y is inverted
    # Unit perpendicular vector
    px = -uy
    py = ux

    # 4 corners of outer trapezoid
    p1 = (ox + ux * r_start - px * w_start, oy + uy * r_start - py * w_start)
    p2 = (ox + ux * r_start + px * w_start, oy + uy * r_start + py * w_start)
    p3 = (ox + ux * r_end + px * w_end,     oy + uy * r_end + py * w_end)
    p4 = (ox + ux * r_end - px * w_end,     oy + uy * r_end - py * w_end)

    # Inner core (inset by 1.2px)
    r_in_start = r_start + 1.2
    r_in_end = r_end - 1.2
    w_in_start = max(0.5, w_start - 0.9)
    w_in_end = max(1.0, w_end - 1.0)
    q1 = (ox + ux * r_in_start - px * w_in_start, oy + uy * r_in_start - py * w_in_start)
    q2 = (ox + ux * r_in_start + px * w_in_start, oy + uy * r_in_start + py * w_in_start)
    q3 = (ox + ux * r_in_end + px * w_in_end,     oy + uy * r_in_end + py * w_in_end)
    q4 = (ox + ux * r_in_end - px * w_in_end,     oy + uy * r_in_end - py * w_in_end)

    return [p1, p2, p3, p4], [q1, q2, q3, q4]

def draw_mouth_radiating_sound(im, mouth_origin=(16, 35), gap=5.0):
    """Draw 3 sound wedges radiating OUTWARDS from the mouth.
    Narrow ends near mouth, widening as they shoot forward and upward into the air.
    """
    im = im.copy()
    d = ImageDraw.Draw(im)
    ox, oy = mouth_origin

    # 1. TOP WEDGE: Shoots steep up-left towards sky (angle ~112 deg)
    top_out, top_in = make_radiating_wedge(
        origin=(ox, oy),
        angle_deg=112,
        r_start=gap + 2.0,
        r_end=gap + 15.0,
        w_start=1.6,
        w_end=2.6
    )

    # 2. MID WEDGE: Longest, shoots forward-up at ~144 deg (main shriek beam)
    # Ends at r_end: when ox=16, 16 - (gap+13.5)*cos(144) = 16 - 15.0 = 1.0 (strictly x >= 1!)
    mid_out, mid_in = make_radiating_wedge(
        origin=(ox, oy),
        angle_deg=144,
        r_start=gap + 0.5,
        r_end=gap + 13.5,
        w_start=1.8,
        w_end=3.6
    )

    # 3. BOT WEDGE: Shoots straight forward-left at ~174 deg (lower beam)
    bot_out, bot_in = make_radiating_wedge(
        origin=(ox, oy),
        angle_deg=174,
        r_start=gap + 1.5,
        r_end=gap + 11.5,
        w_start=1.5,
        w_end=2.6
    )

    wedges = [(top_out, top_in), (mid_out, mid_in), (bot_out, bot_in)]

    for outer, inner in wedges:
        outer_pts = [(round(x), round(y)) for x, y in outer]
        inner_pts = [(round(x), round(y)) for x, y in inner]
        # Dark 1px outline
        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            d.polygon([(x + dx, y + dy) for x, y in outer_pts], fill=C_BURST_DARK)
        # Golden yellow outer body
        d.polygon(outer_pts, fill=C_BURST_YELLOW)
        # Warm orange inner core
        d.polygon(inner_pts, fill=C_BURST_ORANGE)

    # Subtle vibration dots in the gap right in front of the mouth
    d.point((ox - 2, oy - 1), fill=C_BURST_YELLOW)
    d.point((ox - 3, oy - 2), fill=C_BURST_ORANGE)

    return im

def build_demo_suite():
    # Base bird frames
    # Frame 0: Startled (closed mouth)
    f0 = bird_q_optimized(head=(1, -2), body_roll=1, tail_wag=-1, crest="alert", eye="wide", mouth="closed")
    # Frame 1: Beak snaps open
    f1_base = bird_q_optimized(head=(-1, -1), body_roll=-1, tail_wag=3, crest="alert", eye="wide", mouth="bite")
    # Frame 2: Beak wide open shriek hold
    f2_base = bird_q_optimized(head=(0, 0), body_roll=-1, tail_wag=2, crest="alert", eye="wide", mouth="bite")
    # Frame 3: Recoil closed mouth
    f3 = bird_q_optimized(head=(-1, -1), body_roll=0, tail_wag=1, crest="alert", eye="wide", mouth="closed")

    # Option A: Standard Beak Radiation (gap = 4.5px, close to mouth)
    oa_f1 = draw_mouth_radiating_sound(f1_base, mouth_origin=(15, 35), gap=4.5)
    oa_f2 = draw_mouth_radiating_sound(f2_base, mouth_origin=(16, 36), gap=4.5)
    oa_frames = [f0, oa_f1, oa_f2, f3]

    # Option B: Airy Beak Radiation (gap = 7.0px, more distant air gap)
    ob_f1 = draw_mouth_radiating_sound(f1_base, mouth_origin=(15, 35), gap=7.0)
    ob_f2 = draw_mouth_radiating_sound(f2_base, mouth_origin=(16, 36), gap=7.0)
    ob_frames = [f0, ob_f1, ob_f2, f3]

    durations = [140, 180, 240, 320, 360]

    # Save 3x Animated GIFs
    def save_gif(frames, fname):
        scaled = [f.resize((300, 240), Image.NEAREST) for f in [frames[0], frames[1], frames[2], frames[3], frames[3]]]
        scaled[0].save(
            OUT_DIR / fname,
            save_all=True,
            append_images=scaled[1:],
            duration=durations,
            loop=0,
            disposal=2
        )
        if ARTIFACT_DIR.exists():
            scaled[0].save(
                ARTIFACT_DIR / fname,
                save_all=True,
                append_images=scaled[1:],
                duration=durations,
                loop=0,
                disposal=2
            )

    save_gif(oa_frames, "mouth_radiating_optA_3x.gif")
    save_gif(ob_frames, "mouth_radiating_optB_3x.gif")

    # Spritesheet comparison: Option A vs Option B (2 rows x 4 cols)
    comp_w = 100 * 4
    comp_h = 80 * 2 + 10
    comp_img = Image.new("RGBA", (comp_w, comp_h), (245, 247, 250, 255))
    d_comp = ImageDraw.Draw(comp_img)

    for i in range(4):
        comp_img.paste(oa_frames[i], (i * 100, 0), oa_frames[i])
        comp_img.paste(ob_frames[i], (i * 100, 90), ob_frames[i])
        if i > 0:
            d_comp.line([(i * 100, 0), (i * 100, comp_h)], fill="#d5dae2")
    d_comp.line([(0, 85), (comp_w, 85)], fill="#b0b8c4", width=2)

    comp_2x = comp_img.resize((comp_w * 2, comp_h * 2), Image.NEAREST)
    comp_2x.save(OUT_DIR / "mouth_radiating_comparison_2x.png")
    if ARTIFACT_DIR.exists():
        comp_2x.save(ARTIFACT_DIR / "mouth_radiating_comparison_2x.png")

    # Interaction simulation GIF for Option A
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
        f.paste(oa_frames[3], (25, 10), oa_frames[3])
        cx = 120 - step * 25
        cy = 30 + step * 8
        f.paste(cursor, (cx, cy), cursor)
        sim_frames.append(f)
        sim_durations.append(150)

    click_f = base_bg.copy()
    click_f.paste(oa_frames[0], (25, 10), oa_frames[0])
    d_click = ImageDraw.Draw(click_f)
    d_click.ellipse((85, 48, 93, 56), fill="#ffd100", outline="#353438")
    click_f.paste(cursor, (80, 42), cursor)
    sim_frames.append(click_f)
    sim_durations.append(130)

    for b_idx in [1, 2, 3]:
        f = base_bg.copy()
        f.paste(oa_frames[b_idx], (25, 10), oa_frames[b_idx])
        f.paste(cursor, (90 + b_idx * 5, 36 - b_idx * 3), cursor)
        sim_frames.append(f)
        sim_durations.append(180)

    f_settle = base_bg.copy()
    f_settle.paste(oa_frames[3], (25, 10), oa_frames[3])
    sim_frames.append(f_settle)
    sim_durations.append(450)

    sim_2x = [sf.resize((w * 2, h * 2), Image.NEAREST) for sf in sim_frames]
    sim_2x[0].save(
        OUT_DIR / "mouth_radiating_optA_interaction_2x.gif",
        save_all=True,
        append_images=sim_2x[1:],
        duration=sim_durations,
        loop=0,
        disposal=2
    )
    if ARTIFACT_DIR.exists():
        sim_2x[0].save(
            ARTIFACT_DIR / "mouth_radiating_optA_interaction_2x.gif",
            save_all=True,
            append_images=sim_2x[1:],
            duration=sim_durations,
            loop=0,
            disposal=2
        )

    print("Mouth radiating demo suite generated successfully!")

if __name__ == "__main__":
    build_demo_suite()
