"""Complete, clean generator for Cockatiel Beak Bonking Animation Preview.
Generates 100x80 pixel frames, preview spritesheets, and animated GIFs.
"""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import shutil

OUT_DIR = Path(r"D:\pets\test_bonk")
OUT_DIR.mkdir(parents=True, exist_ok=True)

# Project Artifacts directory
ARTIFACT_DIR = Path(r"C:\Users\26893\.gemini\antigravity\brain\5df30705-c1cf-4a9e-883a-019811f74aae")

C = dict(
    ink="#353438", grey="#69696d", light="#88878a", dark="#505055",
    white="#f5f1df", yellow="#fff081", shade="#eacb67", cheek="#e99342",
    beak="#a99b9a", foot="#bba5a5", blush="#f2826a"
)

def render_bonk_frame(
    head=(-8, 4),
    body_roll=-4,
    tail_wag=4,
    lift=0,
    step=1,
    eye="open",
    crest="alert",
    mouth="closed",
    dot_count=0,
    dot_shift=(0, 0),
    spark_style=None
):
    """Render a flawless 100x80 cockatiel bonk frame."""
    im = Image.new("RGBA", (100, 80))
    d = ImageDraw.Draw(im)
    c = C
    
    bx_off = body_roll
    tx_off = tail_wag
    
    # 1. TAIL (尾巴 - 随前倾敲击自然上翘)
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

    # 2. FEET (双脚 - 前倾时重心稳固)
    feet = [(46, 42), (58, 55)]
    if step == 1:
        # 稳稳下踏
        feet = [(43, 38), (58, 55)]
    for fx, toe in feet:
        d.line([(fx + bx_off, 66 + lift), (toe, 72)], fill=c["ink"], width=3)
        d.line([(fx + bx_off, 66 + lift), (toe, 72)], fill=c["foot"], width=2)
        d.line([(toe - 3, 72), (toe + 2, 72)], fill=c["foot"], width=2)

    # 3. BODY (胖胖身躯)
    body_x0 = 34 + bx_off
    body_y0 = 32 + lift
    body_x1 = 72 + bx_off
    body_y1 = 69 + lift
    d.ellipse((body_x0, body_y0, body_x1, body_y1), fill=c["ink"])
    d.ellipse((body_x0 + 2, body_y0 + 2, body_x1 - 2, body_y1 - 2), fill=c["grey"])
    d.ellipse((body_x0 + 4, body_y0 + 7, body_x0 + 23, body_y1 - 5), fill=c["light"])

    # 4. WING (收拢翅膀)
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

    # 5. NECK BRIDGE (连接脖子，在头部下方渲染，确保100%无接缝)
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

    # 6. HEAD & CHEEKS (大头与橘色大腮红)
    d.ellipse((hx - 13, hy - 13, hx + 13, hy + 13), fill=c["ink"])
    d.ellipse((hx - 12, hy - 12, hx + 11, hy + 12), fill=c["yellow"])
    d.polygon([(hx + 6, hy - 9), (hx + 12, hy - 5), (hx + 13, hy + 9), (hx + 6, hy + 12)], fill=c["white"])
    d.ellipse((hx - 3, hy + 1, hx + 8, hy + 11), fill=c["cheek"])

    # 7. CREST (冠羽)
    if crest == "alert":
        d.polygon([(hx - 5, hy - 10), (hx - 1, hy - 28), (hx + 2, hy - 30), (hx + 3, hy - 11)], fill=c["shade"])
        d.polygon([(hx, hy - 11), (hx + 7, hy - 25), (hx + 9, hy - 24), (hx + 4, hy - 9)], fill=c["yellow"])
    else:
        d.polygon([(hx - 7, hy - 11), (hx + 1, hy - 21), (hx + 14, hy - 26), (hx + 12, hy - 19), (hx + 3, hy - 10)], fill=c["shade"])
        d.polygon([(hx - 5, hy - 12), (hx + 2, hy - 20), (hx + 13, hy - 25), (hx + 10, hy - 20), (hx + 1, hy - 11)], fill=c["yellow"])

    # 8. EYES (眼神)
    if eye == "open":
        d.ellipse((hx - 8, hy - 5, hx - 4, hy), fill=c["ink"])
        d.point((hx - 7, hy - 4), fill=c["white"])
    elif eye == "wide":
        d.ellipse((hx - 9, hy - 7, hx - 3, hy + 1), fill=c["ink"])
        d.point((hx - 7, hy - 5), fill=c["white"])
    elif eye == "happy":
        d.line([(hx - 9, hy - 1), (hx - 6, hy - 4), (hx - 3, hy - 1)], fill=c["ink"], width=2)
        d.point((hx + 2, hy + 6), fill=c["blush"])

    # 9. BEAK (嘴喙)
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

    # 10. SPARK / GLASS IMPACT (嘴壳碰触屏幕玻璃的小星号)
    if spark_style:
        beak_tip_x = max(2, hx - 16)
        beak_tip_y = hy + 3
        # Crisp white & cyan glass tap impact spark
        for dx, dy in [(-2, 0), (-1, 0), (1, 0), (2, 0), (0, -2), (0, -1), (0, 1), (0, 2)]:
            d.point((beak_tip_x + dx, beak_tip_y + dy), fill="#64c0eb")
        d.rectangle((beak_tip_x - 1, beak_tip_y - 1, beak_tip_x + 1, beak_tip_y + 1), fill="#ffffff")

    # 11. SOUND DOTS (头上冒出 3 个声音圆点标识)
    if dot_count > 0:
        # Base arc positioned clear of the tall crest, above head & back
        # Ascending arc: Dot 1 (small) -> Dot 2 (medium) -> Dot 3 (large)
        base_dots = [
            (42, 13, 2),   # Dot 1: small (radius 2)
            (52, 9, 3),    # Dot 2: medium (radius 3)
            (64, 7, 4),    # Dot 3: large (radius 4)
        ]
        sx, sy = dot_shift
        for i in range(min(dot_count, 3)):
            bx, by, r = base_dots[i]
            cx, cy = bx + sx, by + sy
            # Outer dark outline
            d.ellipse((cx - r, cy - r, cx + r, cy + r), fill="#2b2a2e")
            # Clear sky-blue fill (#64c0eb)
            d.ellipse((cx - r + 1, cy - r + 1, cx + r - 1, cy + r - 1), fill="#64c0eb")
            # Highlight glint
            if r >= 3:
                d.point((cx - 1, cy - r + 2), fill="#ffffff")

    return im

def build_bonk_animation():
    # 5 Frames of Beak Bonking Sequence:
    # 0: 蓄力后仰 (Anticipation)
    f0 = render_bonk_frame(
        head=(2, -3), body_roll=0, tail_wag=-1, step=0,
        eye="open", crest="alert", dot_count=0
    )
    # 1: 疾步突进 (Lunge: 1st sound dot emerges)
    f1 = render_bonk_frame(
        head=(-8, 1), body_roll=-3, tail_wag=3, step=1,
        eye="open", crest="alert", dot_count=1
    )
    # 2: 嘴壳撞屏！(Strike & Bonk: impact spark flashes, 2 sound dots)
    f2 = render_bonk_frame(
        head=(-13, 4), body_roll=-6, tail_wag=5, step=1,
        eye="wide", crest="alert", mouth="bite",
        dot_count=2, spark_style="spark"
    )
    # 3: 音波共鸣 (Peak resonance: 3 sound dots radiant, happy expression)
    f3 = render_bonk_frame(
        head=(-11, 4), body_roll=-5, tail_wag=4, step=1,
        eye="happy", crest="alert",
        dot_count=3, spark_style="spark"
    )
    # 4: 满足回弹 (Recoil: 3 dots float higher, happy squint, settle)
    f4 = render_bonk_frame(
        head=(-3, -1), body_roll=-1, tail_wag=1, step=0,
        eye="happy", crest="alert",
        dot_count=3, dot_shift=(2, -3)
    )

    frames = [f0, f1, f2, f3, f4]

    # Save to test_bonk directory
    for i, f in enumerate(frames):
        f.save(OUT_DIR / f"bonk_{i}.png")

    # Animated GIF: Rhythm of Cockatiel Beak Bonk (Double Bonk feel)
    # Ready -> Bonk Strike -> Echo -> Settle -> Pause
    gif_frames = [f0, f1, f2, f3, f4, f0]
    durations = [280, 100, 160, 220, 180, 320]
    scaled_gif = [f.resize((300, 240), Image.NEAREST) for f in gif_frames]
    gif_path = OUT_DIR / "bonk_animated_3x.gif"
    scaled_gif[0].save(
        gif_path,
        save_all=True,
        append_images=scaled_gif[1:],
        duration=durations,
        loop=0,
        disposal=2
    )

    # Spritesheet (1x and 2x)
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
    sheet_2x_path = OUT_DIR / "bonk_spritesheet_2x.png"
    sheet_2x.save(sheet_2x_path)

    # Copy files to artifacts directory so they can be embedded in chat/artifacts
    if ARTIFACT_DIR.exists():
        shutil.copy(sheet_2x_path, ARTIFACT_DIR / "bonk_spritesheet_2x.png")
        shutil.copy(gif_path, ARTIFACT_DIR / "bonk_animated_3x.gif")
        for i in range(5):
            shutil.copy(OUT_DIR / f"bonk_{i}.png", ARTIFACT_DIR / f"bonk_{i}.png")
        print("Copied preview assets to artifact directory.")

    print("Bonk animation suite generated successfully!")

if __name__ == "__main__":
    build_bonk_animation()
