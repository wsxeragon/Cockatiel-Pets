"""Script to generate Cockatiel Bonk Animation with procedurally drawn sound burst
matching user's reference image (3 radiating rounded wedges: yellow rim, orange fill).
"""
from pathlib import Path
from PIL import Image, ImageDraw
import shutil

OUT_DIR = Path(r"D:\pets\test_bonk")
OUT_DIR.mkdir(parents=True, exist_ok=True)
ARTIFACT_DIR = Path(r"C:\Users\26893\.gemini\antigravity\brain\5df30705-c1cf-4a9e-883a-019811f74aae")

C = dict(
    ink="#353438", grey="#69696d", light="#88878a", dark="#505055",
    white="#f5f1df", yellow="#fff081", shade="#eacb67", cheek="#e99342",
    beak="#a99b9a", foot="#bba5a5", blush="#f2826a"
)

# Colors matching user reference image exactly:
C_BURST_YELLOW = "#ffd100"  # Bright vibrant golden yellow outer border
C_BURST_ORANGE = "#ff9800"  # Warm deep orange inner core
C_BURST_DARK = "#4a3b2c"    # Optional soft dark edge for high-contrast on light wallpapers

def draw_procedural_burst(im, origin=(36, 20), stage=2, scale=1.0, with_dark_edge=True):
    """Draw the 3 radiating sound wedges matching user reference image.
    stage:
      0: None
      1: Emerging small (scale ~0.65)
      2: Full impact burst (scale 1.0)
      3: Expanding / resonant (scale 1.15, slightly shifted outwards)
    """
    if stage == 0:
        return im

    im = im.copy()
    d = ImageDraw.Draw(im)
    ox, oy = origin

    # If stage 1, smaller
    if stage == 1:
        s = scale * 0.65
    elif stage == 2:
        s = scale * 1.0
    elif stage == 3:
        s = scale * 1.18
        ox += 1
        oy -= 1
    else:
        s = scale

    # 1. TOP WEDGE (near-vertical, slightly tilting left, widening upward)
    top_outer = [
        (ox - 6 * s, oy - 4 * s),   # bottom-left narrow
        (ox - 2 * s, oy - 5 * s),   # bottom-right narrow
        (ox - 1 * s, oy - 15 * s),  # top-right wide
        (ox - 5 * s, oy - 16 * s),  # top-left wide
    ]
    top_inner = [
        (ox - 5 * s, oy - 6 * s),
        (ox - 3 * s, oy - 6 * s),
        (ox - 2 * s, oy - 14 * s),
        (ox - 4 * s, oy - 14 * s),
    ]

    # 2. MIDDLE WEDGE (longest, angled at ~35 deg towards top-right, thick body)
    mid_outer = [
        (ox - 1 * s, oy - 1 * s),   # bottom-left narrow
        (ox + 1 * s, oy - 4 * s),   # top-left narrow
        (ox + 14 * s, oy - 10 * s), # top-right wide
        (ox + 16 * s, oy - 5 * s),  # right tip
        (ox + 11 * s, oy - 2 * s),  # bottom-right
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
        (ox + 2 * s, oy + 2 * s),   # top-left narrow
        (ox + 3 * s, oy + 6 * s),   # bottom-left narrow
        (ox + 12 * s, oy + 7 * s),  # bottom-right wide
        (ox + 13 * s, oy + 2 * s),  # top-right wide
    ]
    bot_inner = [
        (ox + 3 * s, oy + 3 * s),
        (ox + 4 * s, oy + 5 * s),
        (ox + 11 * s, oy + 6 * s),
        (ox + 11 * s, oy + 3 * s),
    ]

    wedges = [
        (top_outer, top_inner),
        (mid_outer, mid_inner),
        (bot_outer, bot_inner),
    ]

    for outer, inner in wedges:
        outer_pts = [(round(x), round(y)) for x, y in outer]
        inner_pts = [(round(x), round(y)) for x, y in inner]

        if with_dark_edge:
            # Subtle 1px dark edge for crisp readability
            for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                d.polygon([(x + dx, y + dy) for x, y in outer_pts], fill=C_BURST_DARK)

        # Draw outer bright yellow
        d.polygon(outer_pts, fill=C_BURST_YELLOW)
        # Draw inner warm orange
        d.polygon(inner_pts, fill=C_BURST_ORANGE)

    return im

def render_bonk_frame_with_burst(
    head=(-8, 4),
    body_roll=-4,
    tail_wag=4,
    lift=0,
    step=1,
    eye="open",
    crest="alert",
    mouth="closed",
    burst_stage=0,
    spark_style=None
):
    """Render 100x80 cockatiel bonk frame with the user's custom sound burst."""
    im = Image.new("RGBA", (100, 80))
    d = ImageDraw.Draw(im)
    c = C

    bx_off = body_roll
    tx_off = tail_wag

    # 1. TAIL
    tail_pts_outer = [
        (61 + bx_off, 47 + lift),
        (96 + tx_off, 51 + lift),
        (98 + tx_off, 54 + lift),
        (68 + bx_off, 56 + lift),
        (60 + bx_off, 52 + lift)
    ]
    d.polygon(tail_pts_outer, fill=c["ink"])
    d.polygon([
        (63 + bx_off, 48 + lift),
        (95 + tx_off, 52 + lift),
        (92 + tx_off, 54 + lift),
        (67 + bx_off, 53 + lift)
    ], fill=c["dark"])
    d.line([(71 + bx_off, 51 + lift), (92 + tx_off, 53 + lift)], fill=c["light"])

    # 2. FEET
    feet = [(46, 42), (58, 55)]
    if step == 1:
        feet = [(43, 38), (58, 55)]
    for fx, toe in feet:
        d.line([(fx + bx_off, 66 + lift), (toe, 72)], fill=c["ink"], width=3)
        d.line([(fx + bx_off, 66 + lift), (toe, 72)], fill=c["foot"], width=2)
        d.line([(toe - 3, 72), (toe + 2, 72)], fill=c["foot"], width=2)

    # 3. BODY
    body_x0 = 34 + bx_off
    body_y0 = 32 + lift
    body_x1 = 72 + bx_off
    body_y1 = 69 + lift
    d.ellipse((body_x0, body_y0, body_x1, body_y1), fill=c["ink"])
    d.ellipse((body_x0 + 2, body_y0 + 2, body_x1 - 2, body_y1 - 2), fill=c["grey"])
    d.ellipse((body_x0 + 4, body_y0 + 7, body_x0 + 23, body_y1 - 5), fill=c["light"])

    # 4. WING
    d.polygon([
        (48 + bx_off, 38 + lift),
        (65 + bx_off, 43 + lift),
        (76 + bx_off, 54 + lift),
        (63 + bx_off, 62 + lift),
        (48 + bx_off, 55 + lift)
    ], fill=c["ink"])
    d.polygon([
        (49 + bx_off, 40 + lift),
        (65 + bx_off, 44 + lift),
        (73 + bx_off, 53 + lift),
        (61 + bx_off, 57 + lift),
        (49 + bx_off, 52 + lift)
    ], fill=c["dark"])
    d.polygon([
        (49 + bx_off, 46 + lift),
        (54 + bx_off, 48 + lift),
        (61 + bx_off, 56 + lift),
        (72 + bx_off, 55 + lift),
        (65 + bx_off, 61 + lift),
        (56 + bx_off, 59 + lift)
    ], fill=c["white"])

    # 5. NECK BRIDGE
    hx = 33 + head[0] + (bx_off // 2)
    hy = 33 + head[1] + lift
    neck_poly = [
        (hx - 2, hy + 5),
        (hx + 10, hy + 2),
        (body_x0 + 15, body_y0 + 8),
        (body_x0 + 6, body_y0 + 18),
        (hx + 2, hy + 14)
    ]
    d.polygon(neck_poly, fill=c["ink"])
    d.polygon([(x, y) for x, y in neck_poly[:-1]], fill=c["grey"])

    # 6. HEAD & CHEEKS
    d.ellipse((hx - 13, hy - 13, hx + 13, hy + 13), fill=c["ink"])
    d.ellipse((hx - 12, hy - 12, hx + 11, hy + 12), fill=c["yellow"])
    d.polygon([(hx + 6, hy - 9), (hx + 12, hy - 5), (hx + 13, hy + 9), (hx + 6, hy + 12)], fill=c["white"])
    d.ellipse((hx - 3, hy + 1, hx + 8, hy + 11), fill=c["cheek"])

    # 7. CREST
    if crest == "alert":
        d.polygon([(hx - 5, hy - 10), (hx - 1, hy - 28), (hx + 2, hy - 30), (hx + 3, hy - 11)], fill=c["shade"])
        d.polygon([(hx, hy - 11), (hx + 7, hy - 25), (hx + 9, hy - 24), (hx + 4, hy - 9)], fill=c["yellow"])
    else:
        d.polygon([(hx - 7, hy - 11), (hx + 1, hy - 21), (hx + 14, hy - 26), (hx + 12, hy - 19), (hx + 3, hy - 10)], fill=c["shade"])
        d.polygon([(hx - 5, hy - 12), (hx + 2, hy - 20), (hx + 13, hy - 25), (hx + 10, hy - 20), (hx + 1, hy - 11)], fill=c["yellow"])

    # 8. EYES
    if eye == "open":
        d.ellipse((hx - 8, hy - 5, hx - 4, hy), fill=c["ink"])
        d.point((hx - 7, hy - 4), fill=c["white"])
    elif eye == "wide":
        d.ellipse((hx - 9, hy - 7, hx - 3, hy + 1), fill=c["ink"])
        d.point((hx - 7, hy - 5), fill=c["white"])
    elif eye == "happy":
        d.line([(hx - 9, hy - 1), (hx - 6, hy - 4), (hx - 3, hy - 1)], fill=c["ink"], width=2)
        d.point((hx + 2, hy + 6), fill=c["blush"])

    # 9. BEAK
    if mouth == "bite":
        d.polygon([(hx - 11, hy + 4), (hx - 14, hy + 7), (hx - 13, hy + 10), (hx - 10, hy + 9), (hx - 8, hy + 6)], fill=c["ink"])
        d.polygon([(hx - 11, hy + 7), (hx - 13, hy + 8), (hx - 12, hy + 9), (hx - 10, hy + 8)], fill=c["beak"])
    else:
        d.polygon([(hx - 11, hy + 4), (hx - 13, hy + 6), (hx - 11, hy + 8), (hx - 9, hy + 6)], fill=c["ink"])
        d.polygon([(hx - 11, hy + 5), (hx - 12, hy + 6), (hx - 10, hy + 7)], fill=c["beak"])

    upper = [
        (hx - 10, hy - 2), (hx - 13, hy - 2), (hx - 15, hy),
        (hx - 16, hy + 2), (hx - 16, hy + 4), (hx - 14, hy + 6),
        (hx - 13, hy + 8), (hx - 13, hy + 5), (hx - 10, hy + 2)
    ]
    d.polygon(upper, fill=c["ink"])
    d.polygon([
        (hx - 11, hy - 1), (hx - 13, hy - 1), (hx - 15, hy + 1),
        (hx - 15, hy + 4), (hx - 13, hy + 6), (hx - 13, hy + 5),
        (hx - 10, hy + 2)
    ], fill=c["beak"])
    d.point((hx - 14, hy + 1), fill="#c8b8b5")

    # 10. IMPACT SPARK
    if spark_style:
        beak_tip_x = max(2, hx - 16)
        beak_tip_y = hy + 3
        for dx, dy in [(-2, 0), (-1, 0), (1, 0), (2, 0), (0, -2), (0, -1), (0, 1), (0, 2)]:
            d.point((beak_tip_x + dx, beak_tip_y + dy), fill="#ffd100")
        d.rectangle((beak_tip_x - 1, beak_tip_y - 1, beak_tip_x + 1, beak_tip_y + 1), fill="#ffffff")

    # 11. PROCEDURAL SOUND BURST WEDGES
    if burst_stage > 0:
        burst_origin = (hx + 17, hy - 16)
        im = draw_procedural_burst(im, origin=burst_origin, stage=burst_stage, with_dark_edge=True)

    return im

def build_all_new_burst_frames():
    # 5 Frames Sequence:
    # Frame 0: 蓄力后仰 (Anticipation - no burst)
    f0 = render_bonk_frame_with_burst(
        head=(2, -3), body_roll=0, tail_wag=-1, step=0,
        eye="open", crest="alert", burst_stage=0
    )
    # Frame 1: 疾步突进 (Lunge - small burst emerging)
    f1 = render_bonk_frame_with_burst(
        head=(-8, 1), body_roll=-3, tail_wag=3, step=1,
        eye="open", crest="alert", burst_stage=1
    )
    # Frame 2: 嘴壳撞屏！(Strike & Bonk - full vibrant burst & glass spark)
    f2 = render_bonk_frame_with_burst(
        head=(-13, 4), body_roll=-6, tail_wag=5, step=1,
        eye="wide", crest="alert", mouth="bite",
        burst_stage=2, spark_style="spark"
    )
    # Frame 3: 音波共鸣 (Peak resonance - expanding burst, happy smiling eye)
    f3 = render_bonk_frame_with_burst(
        head=(-11, 4), body_roll=-5, tail_wag=4, step=1,
        eye="happy", crest="alert",
        burst_stage=3, spark_style="spark"
    )
    # Frame 4: 满足回弹 (Recoil & Settle - burst fades)
    f4 = render_bonk_frame_with_burst(
        head=(-3, -1), body_roll=-1, tail_wag=1, step=0,
        eye="happy", crest="alert", burst_stage=0
    )

    frames = [f0, f1, f2, f3, f4]

    # Save to test_bonk
    for i, f in enumerate(frames):
        f.save(OUT_DIR / f"bonk_custom_{i}.png")

    # Animated GIF (3x)
    gif_frames = [f0, f1, f2, f3, f4, f0]
    durations = [280, 100, 160, 220, 180, 320]
    scaled_gif = [f.resize((300, 240), Image.NEAREST) for f in gif_frames]
    gif_path = OUT_DIR / "bonk_custom_animated_3x.gif"
    scaled_gif[0].save(
        gif_path,
        save_all=True,
        append_images=scaled_gif[1:],
        duration=durations,
        loop=0,
        disposal=2
    )

    # Spritesheet (2x)
    sheet_w = 100 * 5
    sheet_h = 80
    sheet = Image.new("RGBA", (sheet_w, sheet_h), (255, 255, 255, 0))
    d_sheet = ImageDraw.Draw(sheet)
    for i, f in enumerate(frames):
        ox = i * 100
        sheet.paste(f, (ox, 0), f)
        if i > 0:
            d_sheet.line([(ox, 0), (ox, sheet_h)], fill="#d5dae2", width=1)

    sheet_2x = sheet.resize((sheet_w * 2, sheet_h * 2), Image.NEAREST)
    sheet_2x_path = OUT_DIR / "bonk_custom_spritesheet_2x.png"
    sheet_2x.save(sheet_2x_path)

    # Copy to artifact dir
    if ARTIFACT_DIR.exists():
        shutil.copy(sheet_2x_path, ARTIFACT_DIR / "bonk_custom_spritesheet_2x.png")
        shutil.copy(gif_path, ARTIFACT_DIR / "bonk_custom_animated_3x.gif")
        for i in range(5):
            shutil.copy(OUT_DIR / f"bonk_custom_{i}.png", ARTIFACT_DIR / f"bonk_custom_{i}.png")
        print("Copied custom burst assets to artifact directory.")

    print("Custom burst bonk animation generated successfully!")

if __name__ == "__main__":
    build_all_new_burst_frames()
