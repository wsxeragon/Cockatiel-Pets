"""
Cockatiel Poop Feature Asset & Animation Generator
1. Generates pixel-art poop sprites (idle, fall, land, cleanup sparkles) based on user's reference icon.
2. Generates complete cockatiel pooping animation frames (poop_0..poop_13) for both Triple and Classic crests:
   - Step back 2 steps
   - Crouch down and lift tail (~2 seconds squat)
   - Vent drop poop
   - Stand back up and shake tail
3. Produces high-resolution demonstration GIFs and comparison sheets for user review.
"""
import os
import sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

# Add 2d-new for core bird drawing primitives
sys.path.append(str(Path(__file__).resolve().parent / "2d-new"))
from generate_sprites_q_optimized import C, draw_triple_crest_recurve

ARTIFACT_DIR = Path(r"C:\Users\26893\.gemini\antigravity\brain\5df30705-c1cf-4a9e-883a-019811f74aae")
REF_IMAGE_PATH = ARTIFACT_DIR / ".user_uploaded" / "media_1792719201155_7acf6f08.png"

POOP_DIR = Path("assets/poop")
POOP_DIR.mkdir(parents=True, exist_ok=True)

# -------------------------------------------------------------
# 1. COMPACT MOSAIC PIXEL ART POOP SPRITE GENERATOR (16x14)
# -------------------------------------------------------------
C_MOSAIC_PAL = {
    'shadow': (0x4a, 0x24, 0x0c, 255),  # Deep outline / crease
    'dark':   (0x7a, 0x44, 0x1e, 255),  # Shaded mosaic tile
    'mid':    (0xb4, 0x7a, 0x3e, 255),  # Warm caramel base tile
    'light':  (0xd4, 0x9f, 0x68, 255),  # Light caramel tile
    'high':   (0xfa, 0xca, 0x88, 255),  # Golden shine tile
    'gnd':    (0x44, 0x48, 0x5a, 80),   # Ground shadow
    '_':      (0, 0, 0, 0),             # Transparent
}

def draw_mosaic_grid(grid, cell_size=2):
    """Render 2x2 chunky mosaic cells with subtle grid-line borders for anime censor effect"""
    h_blocks = len(grid)
    w_blocks = len(grid[0])
    im = Image.new("RGBA", (w_blocks * cell_size, h_blocks * cell_size), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)

    for gy in range(h_blocks):
        for gx in range(w_blocks):
            key = grid[gy][gx]
            c = C_MOSAIC_PAL[key]
            if c[3] > 0:
                px = gx * cell_size
                py = gy * cell_size
                for dx in range(cell_size):
                    for dy in range(cell_size):
                        if key != 'gnd' and (dx == cell_size - 1 and dy == cell_size - 1):
                            # Mosaic cell bottom-right corner grid line
                            bc = (int(c[0] * 0.82), int(c[1] * 0.82), int(c[2] * 0.82), c[3])
                            d.point((px + dx, py + dy), fill=bc)
                        elif key != 'gnd' and (dx == 0 and dy == 0):
                            # Mosaic cell top-left highlight
                            hc = (min(255, int(c[0] * 1.10)), min(255, int(c[1] * 1.10)), min(255, int(c[2] * 1.10)), c[3])
                            d.point((px + dx, py + dy), fill=hc)
                        else:
                            d.point((px + dx, py + dy), fill=c)
    return im

def generate_poop_idle():
    """Compact pixel-art resting poop (16x14) with 2x2 anime mosaic censor tiles"""
    grid = [
        ['_',     '_',      '_',      'light',  'dark',   '_',      '_',      '_'],
        ['_',     '_',      'mid',    'high',   'shadow', '_',      '_',      '_'],
        ['_',     'shadow', 'light',  'mid',    'mid',    'shadow', '_',      '_'],
        ['_',     'mid',    'light',  'mid',    'dark',   'shadow', '_',      '_'],
        ['shadow','mid',    'mid',    'light',  'mid',    'dark',   'shadow', '_'],
        ['shadow','dark',   'mid',    'mid',    'dark',   'dark',   'shadow', '_'],
        ['_',     'gnd',    'gnd',    'gnd',    'gnd',    'gnd',    'gnd',    '_'],
    ]
    return draw_mosaic_grid(grid, cell_size=2)

def generate_poop_fall():
    """Streamlined aerodynamic falling poop (14x16) with 2x2 mosaic tiles"""
    grid = [
        ['_',     '_',      'light',  'dark',   '_',      '_',      '_'],
        ['_',     '_',      'high',   'shadow', '_',      '_',      '_'],
        ['_',     'shadow', 'light',  'mid',    'shadow', '_',      '_'],
        ['_',     'shadow', 'mid',    'dark',   'shadow', '_',      '_'],
        ['_',     'mid',    'light',  'mid',    'shadow', '_',      '_'],
        ['shadow','mid',    'mid',    'mid',    'dark',   'shadow', '_'],
        ['shadow','dark',   'mid',    'dark',   'dark',   'shadow', '_'],
        ['_',     'shadow', 'shadow', 'shadow', '_',      '_',      '_'],
    ]
    return draw_mosaic_grid(grid, cell_size=2)

def generate_poop_land():
    """Squashed wide impact frame (18x12) upon landing with 2x2 mosaic tiles"""
    grid = [
        ['_',     '_',      '_',      'high',   'shadow', '_',      '_',      '_',      '_'],
        ['_',     '_',      'shadow', 'light',  'mid',    'shadow', '_',      '_',      '_'],
        ['_',     'shadow', 'mid',    'light',  'mid',    'dark',   'shadow', '_',      '_'],
        ['shadow','mid',    'mid',    'mid',    'mid',    'mid',    'dark',   'shadow', '_'],
        ['shadow','dark',   'dark',   'mid',    'mid',    'dark',   'dark',   'dark',   'shadow'],
        ['high',  'gnd',    'gnd',    'gnd',    'gnd',    'gnd',    'gnd',    'gnd',    'high'],
    ]
    return draw_mosaic_grid(grid, cell_size=2)

def generate_poop_clean_frames():
    """4-frame clean-up poof & sparkle animation (24x20) when user clicks the compact poop"""
    frames = []
    w, h = 24, 20
    base = generate_poop_idle()

    C_STAR = (0xff, 0xf0, 0x80, 255) # Bright gold star
    C_WHITE = (0xff, 0xff, 0xff, 255)
    C_PUFF = (0xee, 0xee, 0xf5, 200)

    # Frame 0: Click pop - poop shrinks slightly (12x10), 2 sparkles appear
    f0 = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d0 = ImageDraw.Draw(f0)
    p0 = base.resize((12, 10), Image.Resampling.NEAREST)
    f0.paste(p0, (6, 8), p0)
    # Sparkle 1 (top right)
    d0.line([(19, 3), (19, 7)], fill=C_STAR)
    d0.line([(17, 5), (21, 5)], fill=C_STAR)
    d0.point((19, 5), fill=C_WHITE)
    frames.append(f0)

    # Frame 1: Bursting - poop at 50% opacity (8x7), 4 stars + smoke
    f1 = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d1 = ImageDraw.Draw(f1)
    p1 = base.resize((8, 7), Image.Resampling.NEAREST)
    alpha = p1.split()[3].point(lambda a: a // 2)
    p1.putalpha(alpha)
    f1.paste(p1, (8, 10), p1)
    # Smoke puffs
    d1.ellipse((5, 7, 10, 12), fill=C_PUFF)
    d1.ellipse((13, 8, 18, 13), fill=C_PUFF)
    # Big star top right
    d1.line([(19, 2), (19, 8)], fill=C_STAR)
    d1.line([(16, 5), (22, 5)], fill=C_STAR)
    d1.point((19, 5), fill=C_WHITE)
    # Small star top left
    d1.line([(4, 4), (4, 8)], fill=C_STAR)
    d1.line([(2, 6), (6, 6)], fill=C_STAR)
    d1.point((4, 6), fill=C_WHITE)
    frames.append(f1)

    # Frame 2: Dispersal - poop completely vanished, stars expand outward
    f2 = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d2 = ImageDraw.Draw(f2)
    # Expanding smoke dots
    d2.point((4, 9), fill=C_PUFF); d2.point((19, 9), fill=C_PUFF)
    d2.point((11, 4), fill=C_PUFF); d2.point((12, 14), fill=C_PUFF)
    # Exploded star points
    d2.point((21, 2), fill=C_STAR); d2.point((22, 3), fill=C_WHITE)
    d2.point((2, 5), fill=C_STAR); d2.point((3, 6), fill=C_WHITE)
    d2.point((11, 16), fill=C_STAR)
    frames.append(f2)

    # Frame 3: Final lingering twinkle glints fading
    f3 = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d3 = ImageDraw.Draw(f3)
    d3.point((22, 1), fill=(0xff, 0xf0, 0x80, 160))
    d3.point((1, 4), fill=(0xff, 0xf0, 0x80, 160))
    d3.point((12, 17), fill=(0xff, 0xf0, 0x80, 140))
    frames.append(f3)

    return frames

# -------------------------------------------------------------
# 2. BIRD POOPING ANIMATION FRAMES GENERATOR
# -------------------------------------------------------------
def render_bird_poop_frame(
    frame_idx: int,
    crest_style: str = "triple"
) -> Image.Image:
    """
    Renders one frame (0..13) of the cockatiel pooping sequence:
    0: idle stand
    1..2: backstep 1
    3..4: backstep 2
    5: pre-squat (knees bend, tail tilts up)
    6..8: deep squat hold & strain (belly low, tail cocked up high, squint eye)
    9: vent drop release (poop drops out)
    10: rising back up
    11..12: stand up & tail wag shake
    13: happy relief smile -> idle
    """
    im = Image.new("RGBA", (100, 80))
    d = ImageDraw.Draw(im)
    c = C

    # Pose dynamics based on frame_idx:
    # X back-shift: 0 (frames 0), +2 (frame 1..2), +4 (frame 3..13)
    # Lift (crouch): 0 (normal), +2 (frame 5, 10), +4 (frame 6, 9), +5 (frame 7, 8)
    # Tail tilt up (cocked tail): 0 (normal), 8 (frame 5), 18 (frame 6..9), 4 (frame 10)
    # Tail wag (left-right shake): 0 (normal), +4 (frame 11), -4 (frame 12)
    # Head offset: (-2, +2) when squatting

    if frame_idx == 0:
        x_shift = 0
        lift = 0
        tail_tilt_up = 0
        tail_wag = 0
        eye = "open"
        step = 0
        crest = "normal"
    elif frame_idx == 1:
        # Step back 1: lift rear foot
        x_shift = 1
        lift = 0
        tail_tilt_up = 2
        tail_wag = 0
        eye = "open"
        step = 2  # rear foot stepping back
        crest = "normal"
    elif frame_idx == 2:
        # Step back 1: rear foot planted
        x_shift = 2
        lift = 0
        tail_tilt_up = 3
        tail_wag = 0
        eye = "open"
        step = 0
        crest = "normal"
    elif frame_idx == 3:
        # Step back 2: front foot stepping back
        x_shift = 3
        lift = 0
        tail_tilt_up = 5
        tail_wag = 0
        eye = "open"
        step = 1  # front foot stepping back
        crest = "normal"
    elif frame_idx == 4:
        # Step back 2: both feet firmly planted 4px back
        x_shift = 4
        lift = 0
        tail_tilt_up = 6
        tail_wag = 0
        eye = "open"
        step = 0
        crest = "normal"
    elif frame_idx == 5:
        # Pre-squat: knees bending, tail lifting
        x_shift = 4
        lift = 2
        tail_tilt_up = 10
        tail_wag = 0
        eye = "open"
        step = 0
        crest = "normal"
    elif frame_idx in (6, 7, 8):
        # Deep squat & hold 2 seconds:
        x_shift = 4
        lift = 4 if frame_idx == 6 else 5
        tail_tilt_up = 18
        # Tremor / slight pulse during holding
        tail_wag = 1 if frame_idx == 7 else (-1 if frame_idx == 8 else 0)
        eye = "squint"
        step = 0
        crest = "low"
    elif frame_idx == 9:
        # Vent drop release moment!
        x_shift = 4
        lift = 4
        tail_tilt_up = 16
        tail_wag = 0
        eye = "squint"
        step = 0
        crest = "normal"
    elif frame_idx == 10:
        # Rising back up
        x_shift = 4
        lift = 2
        tail_tilt_up = 6
        tail_wag = 0
        eye = "open"
        step = 0
        crest = "normal"
    elif frame_idx == 11:
        # Standing up & tail wag right
        x_shift = 4
        lift = 0
        tail_tilt_up = 0
        tail_wag = 4
        eye = "open"
        step = 0
        crest = "breath"
    elif frame_idx == 12:
        # Tail wag left
        x_shift = 4
        lift = 0
        tail_tilt_up = 0
        tail_wag = -4
        eye = "open"
        step = 0
        crest = "breath"
    elif frame_idx == 13:
        # Relief & happy smile, tail centered
        x_shift = 4
        lift = 0
        tail_tilt_up = 0
        tail_wag = 0
        eye = "happy"
        step = 0
        crest = "normal"
    else:
        x_shift, lift, tail_tilt_up, tail_wag, eye, step, crest = 0, 0, 0, 0, "open", 0, "normal"

    bx_off = x_shift

    # 1. TAIL (Cocked upwards when squatting, shakes left/right on relief)
    tail_pts_outer = [
        (61 + bx_off, 47 + lift),
        (94 + bx_off + tail_wag, 51 + lift - tail_tilt_up),
        (96 + bx_off + tail_wag, 54 + lift - tail_tilt_up),
        (68 + bx_off, 56 + lift),
        (60 + bx_off, 52 + lift)
    ]
    d.polygon(tail_pts_outer, fill=c["ink"])
    d.polygon([
        (63 + bx_off, 48 + lift),
        (93 + bx_off + tail_wag, 52 + lift - tail_tilt_up),
        (90 + bx_off + tail_wag, 54 + lift - tail_tilt_up),
        (67 + bx_off, 53 + lift)
    ], fill=c["dark"])
    d.line([(71 + bx_off, 51 + lift), (90 + bx_off + tail_wag, 53 + lift - tail_tilt_up)], fill=c["light"])

    # 2. FEET (Squatting bent legs or walking back steps)
    feet = [(46 + bx_off, 42 + bx_off), (58 + bx_off, 55 + bx_off)]
    if step == 1:
        feet = [(43 + bx_off, 36 + bx_off), (58 + bx_off, 55 + bx_off)]
    elif step == 2:
        feet = [(46 + bx_off, 42 + bx_off), (60 + bx_off, 64 + bx_off)]
    for fx, toe in feet:
        d.line([(fx, 66 + lift), (toe, 73)], fill=c["ink"], width=3)
        d.line([(fx, 66 + lift), (toe, 73)], fill=c["foot"], width=2)
        d.line([(toe - 3, 73), (toe + 2, 73)], fill=c["foot"], width=2)

    # 3. CHUBBY BODY
    body_x0 = 34 + bx_off
    body_y0 = 32 + lift
    body_x1 = 72 + bx_off
    body_y1 = 69 + lift
    d.ellipse((body_x0, body_y0, body_x1, body_y1), fill=c["ink"])
    d.ellipse((body_x0 + 2, body_y0 + 2, body_x1 - 2, body_y1 - 2), fill=c["grey"])
    d.ellipse((body_x0 + 4, body_y0 + 7, body_x0 + 23, body_y1 - 5), fill=c["light"])

    # 4. WING (Tight folded, tilts with crouch)
    tilt_wing = 2 if lift > 0 else 0
    d.polygon([
        (48 + bx_off, 38 + lift),
        (65 + bx_off, 43 + lift - tilt_wing),
        (76 + bx_off, 54 + lift - tilt_wing * 2),
        (63 + bx_off, 62 + lift),
        (48 + bx_off, 55 + lift)
    ], fill=c["ink"])
    d.polygon([
        (49 + bx_off, 40 + lift),
        (65 + bx_off, 44 + lift - tilt_wing),
        (73 + bx_off, 53 + lift - tilt_wing * 2),
        (61 + bx_off, 57 + lift),
        (49 + bx_off, 52 + lift)
    ], fill=c["dark"])
    d.polygon([
        (49 + bx_off, 46 + lift),
        (54 + bx_off, 48 + lift),
        (61 + bx_off, 56 + lift),
        (72 + bx_off, 55 + lift - tilt_wing * 2),
        (65 + bx_off, 61 + lift),
        (56 + bx_off, 59 + lift)
    ], fill=c["white"])

    # 5. HEAD & CHEEKS
    head_x = -2 if lift > 0 else 0
    head_y = 2 if lift > 0 else 0
    hx = 33 + bx_off + head_x
    hy = 33 + lift + head_y
    d.ellipse((hx - 13, hy - 13, hx + 13, hy + 13), fill=c["ink"])
    d.ellipse((hx - 12, hy - 12, hx + 11, hy + 12), fill=c["yellow"])
    d.polygon([(hx + 6, hy - 9), (hx + 12, hy - 5), (hx + 13, hy + 9), (hx + 6, hy + 12)], fill=c["white"])
    d.ellipse((hx - 3, hy + 1, hx + 8, hy + 11), fill=c["cheek"])

    # 6. CREST
    if crest_style == "classic":
        if crest == "low":
            d.polygon([(hx - 4, hy - 11), (hx + 8, hy - 15), (hx + 17, hy - 13), (hx + 5, hy - 9)], fill=c["shade"])
            d.line([(hx - 2, hy - 12), (hx + 16, hy - 14)], fill=c["yellow"], width=3)
        else:
            d.polygon([(hx - 7, hy - 11), (hx + 1, hy - 21), (hx + 14, hy - 26), (hx + 12, hy - 19), (hx + 3, hy - 10)], fill=c["shade"])
            d.polygon([(hx - 5, hy - 12), (hx + 2, hy - 20), (hx + 13, hy - 25), (hx + 10, hy - 20), (hx + 1, hy - 11)], fill=c["yellow"])
    else: # triple
        if crest == "low":
            draw_triple_crest_recurve(d, hx, hy, w1=1.2, w2=0.6, w3=0.0, fan=-0.3, lift=-1.2)
        else:
            draw_triple_crest_recurve(d, hx, hy, w1=0.0, w2=0.0, w3=0.0, fan=0.0, lift=0.0)

    # 7. EYE
    if eye == "squint":
        # Focused straining eye
        d.line([(hx - 9, hy - 1), (hx - 5, hy - 3), (hx - 3, hy - 1)], fill=c["ink"], width=2)
    elif eye == "happy":
        # Happy relief curve eye
        d.line([(hx - 9, hy - 1), (hx - 6, hy - 4), (hx - 3, hy - 1)], fill=c["ink"], width=2)
        d.point((hx + 2, hy + 6), fill=c["blush"])
    else: # open
        d.ellipse((hx - 8, hy - 5, hx - 4, hy), fill=c["ink"])
        d.point((hx - 7, hy - 4), fill=c["white"])

    # 8. BEAK
    d.polygon([(hx - 11, hy + 4), (hx - 13, hy + 6), (hx - 11, hy + 8), (hx - 9, hy + 6)], fill=c["ink"])
    d.polygon([(hx - 11, hy + 5), (hx - 12, hy + 6), (hx - 10, hy + 7)], fill=c["beak"])
    upper = [
        (hx - 10, hy - 2), (hx - 13, hy - 2), (hx - 15, hy),
        (hx - 16, hy + 2), (hx - 16, hy + 4), (hx - 14, hy + 6),
        (hx - 11, hy + 5), (hx - 10, hy + 3), (hx - 9, hy + 1), (hx - 9, hy - 1)
    ]
    d.polygon(upper, fill=c["ink"])
    d.polygon([(x + 1, y + 1) for x, y in upper[:-2]], fill=c["beak"])

    return im

def main():
    print("=== [1/4] 生成像素大便单体与动态资产 (assets/poop/) ===")
    p_idle = generate_poop_idle()
    p_fall = generate_poop_fall()
    p_land = generate_poop_land()
    p_cleans = generate_poop_clean_frames()

    p_idle.save(POOP_DIR / "poop_idle.png")
    p_fall.save(POOP_DIR / "poop_fall.png")
    p_land.save(POOP_DIR / "poop_land.png")
    for idx, cf in enumerate(p_cleans):
        cf.save(POOP_DIR / f"poop_clean_{idx}.png")
    print(f"已生成大便单体精灵: idle, fall, land, clean_0..clean_{len(p_cleans)-1}")

    print("=== [2/4] 生成玄凤拉屎动画序列 (poop_0..poop_13) ===")
    target_dirs = [
        Path("assets/sprites_triple"),
        Path("assets/sprites_classic"),
        Path("assets/sprites"),
        Path("2d-new/sprites_triple"),
        Path("2d-new/sprites_classic"),
        Path("2d-new/sprites"),
    ]
    for d in target_dirs:
        d.mkdir(parents=True, exist_ok=True)

    for frame_idx in range(14):
        # Triple
        f_triple = render_bird_poop_frame(frame_idx, crest_style="triple")
        f_triple.save(Path("assets/sprites_triple") / f"poop_{frame_idx}.png")
        f_triple.save(Path("assets/sprites") / f"poop_{frame_idx}.png")
        f_triple.save(Path("2d-new/sprites_triple") / f"poop_{frame_idx}.png")
        f_triple.save(Path("2d-new/sprites") / f"poop_{frame_idx}.png")

        # Classic
        f_classic = render_bird_poop_frame(frame_idx, crest_style="classic")
        f_classic.save(Path("assets/sprites_classic") / f"poop_{frame_idx}.png")
        f_classic.save(Path("2d-new/sprites_classic") / f"poop_{frame_idx}.png")
    print("已成功为 Triple 和 Classic 双羽冠生成 14 帧拉屎动效 (poop_0..poop_13)")

    print("=== [3/4] 制作像素大便与原图 8x 对比大图 ===")
    ref_img = Image.open(REF_IMAGE_PATH).convert("RGBA")
    # Crop ref image tightly
    bg = ref_img.getpixel((0, 0))
    w_ref, h_ref = ref_img.size
    non_bg = []
    for y in range(h_ref):
        for x in range(w_ref):
            p = ref_img.getpixel((x, y))
            if abs(p[0] - bg[0]) > 10 or abs(p[1] - bg[1]) > 10 or abs(p[2] - bg[2]) > 10:
                non_bg.append((x, y))
    r_bbox = (min(p[0] for p in non_bg), min(p[1] for p in non_bg), max(p[0] for p in non_bg), max(p[1] for p in non_bg))
    ref_cropped = ref_img.crop(r_bbox)

    # Build side by side 8x comparison
    sheet_w = 640
    sheet_h = 280
    sheet = Image.new("RGBA", (sheet_w, sheet_h), (250, 252, 253, 255))
    s_draw = ImageDraw.Draw(sheet)

    # Paste ref cropped (scaled to height 200)
    ref_aspect = ref_cropped.width / ref_cropped.height
    ref_display = ref_cropped.resize((int(200 * ref_aspect), 200), Image.Resampling.LANCZOS)
    sheet.paste(ref_display, (40, 40), ref_display)

    # Paste compact mosaic pixel poop 10x (16x14 -> 160x140)
    poop_8x = p_idle.resize((16 * 10, 14 * 10), Image.Resampling.NEAREST)
    sheet.paste(poop_8x, (380, 70), poop_8x)

    # Save to artifact dir
    sheet.save(ARTIFACT_DIR / "poop_pixel_art_breakdown_8x.png")
    print(f"对比图已输出至: {ARTIFACT_DIR / 'poop_pixel_art_breakdown_8x.png'}")

    print("=== [4/4] 制作全套动态展示 GIF (拉屎全过程 + 下落物理 + 点击清理) ===")
    # GIF 1: Bird pooping sequence with dropped poop on ground
    gif_frames = []
    durations = []
    frame_durations = [300, 220, 220, 220, 260, 240, 450, 600, 600, 350, 240, 180, 180, 500]

    bg_canvas_w, bg_canvas_h = 130, 85
    for idx in range(14):
        canvas = Image.new("RGBA", (bg_canvas_w, bg_canvas_h), (245, 248, 250, 255))
        d_can = ImageDraw.Draw(canvas)
        # Floor line
        d_can.line([(10, 75), (120, 75)], fill=(220, 225, 230), width=1)

        # Draw bird
        b_frame = render_bird_poop_frame(idx, crest_style="triple")
        canvas.paste(b_frame, (10, 2), b_frame)

        # After frame 9, poop appears on the ground behind bird!
        # Vent is at bird's rear: X ~ 76, Y ~ 56
        if idx >= 9:
            # Drop from bird vent to floor
            if idx == 9:
                # Mid-drop frame (14x16)
                canvas.paste(p_fall, (76, 56), p_fall)
            elif idx == 10:
                # Land bounce (18x12)
                canvas.paste(p_land, (74, 63), p_land)
            else:
                # Resting on floor (16x14)
                canvas.paste(p_idle, (75, 61), p_idle)

        gif_frames.append(canvas)
        durations.append(frame_durations[idx])

    # Add extra resting frames so user sees the bird standing proudly beside poop
    extra_canvas = Image.new("RGBA", (bg_canvas_w, bg_canvas_h), (245, 248, 250, 255))
    d_can = ImageDraw.Draw(extra_canvas)
    d_can.line([(10, 75), (120, 75)], fill=(220, 225, 230), width=1)
    b_idle = render_bird_poop_frame(0, crest_style="triple")
    extra_canvas.paste(b_idle, (14, 2), b_idle)
    extra_canvas.paste(p_idle, (75, 61), p_idle)
    gif_frames.append(extra_canvas)
    durations.append(1000)

    gif_path = ARTIFACT_DIR / "demo_bird_poop_full_sequence.gif"
    gif_frames[0].save(
        gif_path,
        save_all=True,
        append_images=gif_frames[1:],
        duration=durations,
        loop=0,
        disposal=2
    )
    print(f"拉屎完整过程 GIF 已输出: {gif_path}")

    # GIF 2: Poop falling physics with gravity from altitude
    fall_gif_frames = []
    fall_durations = []
    can_w, can_h = 100, 180
    y_pos = 20.0
    vy = 0.0
    gravity = 1.8
    while y_pos < 155.0:
        base_f = Image.new("RGBA", (can_w, can_h), (245, 248, 250, 255))
        d_f = ImageDraw.Draw(base_f)
        # Floor line at y=172
        d_f.line([(10, 172), (90, 172)], fill=(220, 225, 230), width=1)

        # Draw falling poop (14x16)
        base_f.paste(p_fall, (43, int(y_pos)), p_fall)
        fall_gif_frames.append(base_f)
        fall_durations.append(40)
        vy += gravity
        y_pos += vy

    # Land impact frame (squash 18x12)
    f_land = Image.new("RGBA", (can_w, can_h), (245, 248, 250, 255))
    d_l = ImageDraw.Draw(f_land)
    d_l.line([(10, 172), (90, 172)], fill=(220, 225, 230), width=1)
    f_land.paste(p_land, (41, 160), p_land)
    fall_gif_frames.append(f_land)
    fall_durations.append(90)

    # Rest frame (16x14)
    f_rest = Image.new("RGBA", (can_w, can_h), (245, 248, 250, 255))
    d_r = ImageDraw.Draw(f_rest)
    d_r.line([(10, 172), (90, 172)], fill=(220, 225, 230), width=1)
    f_rest.paste(p_idle, (42, 158), p_idle)
    fall_gif_frames.append(f_rest)
    fall_durations.append(900)

    fall_gif_path = ARTIFACT_DIR / "demo_poop_random_drop_physics.gif"
    fall_gif_frames[0].save(
        fall_gif_path,
        save_all=True,
        append_images=fall_gif_frames[1:],
        duration=fall_durations,
        loop=0,
        disposal=2
    )
    print(f"大便自由落体物理动效 GIF 已输出: {fall_gif_path}")

    # GIF 3: Poop click clean-up animation
    clean_gif_frames = []
    clean_durations = []
    c_w, c_h = 70, 50

    # Frame 0: Poop sitting (16x14)
    c0 = Image.new("RGBA", (c_w, c_h), (245, 248, 250, 255))
    c0.paste(p_idle, (27, 22), p_idle)
    clean_gif_frames.append(c0)
    clean_durations.append(700)

    # Frame 1: Mouse click cursor appears
    c1 = c0.copy()
    d1 = ImageDraw.Draw(c1)
    # Draw simple pixel cursor pointer at (35, 22)
    cursor_pts = [(35, 16), (35, 28), (39, 25), (43, 31), (45, 30), (41, 24), (46, 24)]
    d1.polygon(cursor_pts, fill=(255, 255, 255, 255), outline=(40, 40, 40, 255))
    clean_gif_frames.append(c1)
    clean_durations.append(350)

    # Frame 2..5: Sparkle clean frames (24x20)
    for s_idx, cf in enumerate(p_cleans):
        cs = Image.new("RGBA", (c_w, c_h), (245, 248, 250, 255))
        cs.paste(cf, (23, 16), cf)
        clean_gif_frames.append(cs)
        clean_durations.append(120)

    # Empty clean floor
    clean_empty = Image.new("RGBA", (c_w, c_h), (245, 248, 250, 255))
    clean_gif_frames.append(clean_empty)
    clean_durations.append(800)

    clean_gif_path = ARTIFACT_DIR / "demo_poop_cleanup_sparkle.gif"
    clean_gif_frames[0].save(
        clean_gif_path,
        save_all=True,
        append_images=clean_gif_frames[1:],
        duration=clean_durations,
        loop=0,
        disposal=2
    )
    print(f"点击清理动效 GIF 已输出: {clean_gif_path}")

if __name__ == "__main__":
    main()
