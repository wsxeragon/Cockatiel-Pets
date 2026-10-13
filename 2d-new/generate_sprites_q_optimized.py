r"""Q-Version Cockatiel Animation Optimization Suite.
Generates refined 100x80 procedural pixel sprites into D:\pets\2d-new\sprites.
"""
import math
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

OUT_NEW = Path(r"D:\pets\2d-new\sprites")
OUT_NEW.mkdir(parents=True, exist_ok=True)

OUT_ORIG = Path(r"D:\pets\2d-new\sprites_original")
OUT_ORIG.mkdir(parents=True, exist_ok=True)

C = dict(
    ink="#353438", grey="#69696d", light="#88878a", dark="#505055",
    white="#f5f1df", yellow="#fff081", shade="#eacb67", cheek="#e99342",
    beak="#a99b9a", foot="#bba5a5", blush="#f2826a"
)

def bird_q_optimized(
    head=(0, 0), lift=0, step=0, wing="fold", puff=0, eye="open",
    crest="normal", mouth="closed", crumbs=False, note=0,
    body_roll=0, tail_wag=0, tuck_feet=False
):
    im = Image.new("RGBA", (100, 80))
    d = ImageDraw.Draw(im)
    c = C
    
    # Body roll / tilt offsets
    bx_off = body_roll  # -1 (left), 0, +1 (right)
    tx_off = tail_wag   # tail angle offset
    
    # 1. TAIL (尾巴 - 随摇摆微颤)
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

    # 2. FAR WING IN FLIGHT
    if wing.startswith("fly"):
        far = {
            "fly_up": [(52, 42), (73, 11), (80, 7), (69, 40)],
            "fly_mid": [(53, 43), (82, 27), (96, 28), (66, 49)],
            "fly_down": [(54, 43), (80, 63), (83, 66), (59, 50)]
        }[wing]
        d.polygon([(x, y + lift) for x, y in far], fill=c["dark"])

    # 3. FEET (双脚 - 飞行时紧缩进肚皮，走动时交替迈步)
    if tuck_feet or wing.startswith("fly"):
        # 飞行/母鸡蹲模式: 小短腿可爱地蜷缩在胖肚皮下
        for fx in (48 + bx_off, 56 + bx_off):
            d.line([(fx, 62 + lift), (fx + 4, 62 + lift)], fill=c["ink"], width=2)
            d.line([(fx, 62 + lift), (fx + 4, 62 + lift)], fill=c["foot"], width=1)
    else:
        # 走动/站立模式
        feet = [(46, 42), (58, 55)]
        if step == 1:
            # 左脚前迈，重心左移
            feet = [(43, 36), (58, 55)]
        elif step == 2:
            # 右脚前迈，重心右移
            feet = [(46, 42), (60, 66)]
        for fx, toe in feet:
            d.line([(fx + bx_off, 66 + lift), (toe, 72)], fill=c["ink"], width=3)
            d.line([(fx + bx_off, 66 + lift), (toe, 72)], fill=c["foot"], width=2)
            d.line([(toe - 3, 72), (toe + 2, 72)], fill=c["foot"], width=2)

    # 4. CHUBBY BODY (圆滚滚麻薯身躯)
    body_x0 = 34 - puff + bx_off
    body_y0 = 32 + lift - puff
    body_x1 = 72 + puff + bx_off
    body_y1 = 69 + lift
    d.ellipse((body_x0, body_y0, body_x1, body_y1), fill=c["ink"])
    d.ellipse((body_x0 + 2, body_y0 + 2, body_x1 - 2, body_y1 - 2), fill=c["grey"])
    d.ellipse((body_x0 + 4, body_y0 + 7, body_x0 + 23, body_y1 - 5), fill=c["light"])
    
    # 呼吸蓬毛绒毛微粒
    if puff:
        for px, py in [(35, 48), (34, 56), (39, 64), (70, 42)]:
            d.rectangle((px - 2 + bx_off, py + lift, px + 1 + bx_off, py + lift + 2), fill=c["light"])

    # 5. NEAR WING (近侧翅膀)
    if wing.startswith("fly"):
        wing_shape = {
            "fly_up": [(48, 43), (56, 26), (64, 7), (69, 10), (65, 35), (56, 51)],
            "fly_mid": [(48, 43), (67, 29), (89, 23), (92, 28), (66, 46), (54, 52)],
            "fly_down": [(48, 43), (61, 49), (81, 68), (76, 71), (54, 55)]
        }[wing]
        d.polygon([(x, y + lift) for x, y in wing_shape], fill=c["ink"])
        white_shape = {
            "fly_up": [(52, 42), (61, 23), (65, 13), (62, 33), (55, 46)],
            "fly_mid": [(52, 42), (69, 32), (85, 27), (66, 42), (55, 48)],
            "fly_down": [(52, 46), (62, 52), (77, 66), (72, 65), (55, 52)]
        }[wing]
        d.polygon([(x, y + lift) for x, y in white_shape], fill=c["white"])
    else:
        if wing == "heart":
            # 心形求偶微张翅膀
            d.polygon([
                (47 + bx_off, 36 + lift),
                (67 + bx_off, 42 + lift),
                (74 + bx_off, 60 + lift),
                (58 + bx_off, 55 + lift)
            ], fill=c["ink"])
            d.polygon([
                (48 + bx_off, 38 + lift),
                (66 + bx_off, 43 + lift),
                (71 + bx_off, 58 + lift),
                (59 + bx_off, 54 + lift)
            ], fill=c["dark"])
            d.polygon([
                (49 + bx_off, 42 + lift),
                (56 + bx_off, 44 + lift),
                (64 + bx_off, 53 + lift),
                (57 + bx_off, 54 + lift)
            ], fill=c["white"])
        else:
            # 经典贴身收拢翅膀
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

    # 6. HEAD & CHEEKS (大头与橘色腮红)
    hx = 33 + head[0] + (bx_off // 2)
    hy = 33 + head[1] + lift
    d.ellipse((hx - 13, hy - 13, hx + 13, hy + 13), fill=c["ink"])
    d.ellipse((hx - 12, hy - 12, hx + 11, hy + 12), fill=c["yellow"])
    d.polygon([(hx + 6, hy - 9), (hx + 12, hy - 5), (hx + 13, hy + 9), (hx + 6, hy + 12)], fill=c["white"])
    
    # 招牌大腮红
    d.ellipse((hx - 3, hy + 1, hx + 8, hy + 11), fill=c["cheek"])

    # 7. CREST (呆毛/冠羽 - 情绪风向标)
    if crest == "low":
        # 顺滑贴向后脑 (求摸/生气)
        d.polygon([(hx - 4, hy - 11), (hx + 8, hy - 15), (hx + 17, hy - 13), (hx + 5, hy - 9)], fill=c["shade"])
        d.line([(hx - 2, hy - 12), (hx + 16, hy - 14)], fill=c["yellow"], width=3)
    elif crest == "alert":
        # 笔直高耸炸毛 (警觉/受惊)
        d.polygon([(hx - 5, hy - 10), (hx - 1, hy - 28), (hx + 2, hy - 30), (hx + 3, hy - 11)], fill=c["shade"])
        d.polygon([(hx, hy - 11), (hx + 7, hy - 25), (hx + 9, hy - 24), (hx + 4, hy - 9)], fill=c["yellow"])
    elif crest == "breath":
        # 呼吸微颤 (稍微弹起1像素)
        d.polygon([(hx - 6, hy - 11), (hx + 1, hy - 22), (hx + 14, hy - 27), (hx + 12, hy - 20), (hx + 3, hy - 10)], fill=c["shade"])
        d.polygon([(hx - 4, hy - 12), (hx + 2, hy - 21), (hx + 13, hy - 26), (hx + 10, hy - 21), (hx + 1, hy - 11)], fill=c["yellow"])
    else:
        # 自然软萌微弯
        d.polygon([(hx - 7, hy - 11), (hx + 1, hy - 21), (hx + 14, hy - 26), (hx + 12, hy - 19), (hx + 3, hy - 10)], fill=c["shade"])
        d.polygon([(hx - 5, hy - 12), (hx + 2, hy - 20), (hx + 13, hy - 25), (hx + 10, hy - 20), (hx + 1, hy - 11)], fill=c["yellow"])

    # 8. EYES (表情眼神)
    if eye == "open":
        # 明亮大黑眼珠带小白高光
        d.ellipse((hx - 8, hy - 5, hx - 4, hy), fill=c["ink"])
        d.point((hx - 7, hy - 4), fill=c["white"])
    elif eye == "wide":
        # 惊吓圆瞪大瞳孔
        d.ellipse((hx - 9, hy - 7, hx - 3, hy + 1), fill=c["ink"])
        d.point((hx - 7, hy - 5), fill=c["white"])
    elif eye == "happy":
        # 【新增】求摸惬意享受笑眼 (^_^)
        d.line([(hx - 9, hy - 1), (hx - 6, hy - 4), (hx - 3, hy - 1)], fill=c["ink"], width=2)
        # 腮红红晕加深一点点
        d.point((hx + 2, hy + 6), fill=c["blush"])
    else:
        # 平和闭眼单线 (睡觉/闭眼发呆)
        d.line([(hx - 9, hy - 2), (hx - 6, hy - 1), (hx - 3, hy - 2)], fill=c["ink"], width=2)

    # 9. BEAK (小嘴喙)
    opened = mouth in ("bite", "hiss", "sing")
    if mouth == "sing":
        d.polygon([(hx - 11, hy + 4), (hx - 14, hy + 6), (hx - 13, hy + 8), (hx - 10, hy + 7)], fill=c["ink"])
        d.line([(hx - 13, hy + 6), (hx - 11, hy + 6)], fill=c["beak"])
    elif opened:
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

    # 10. MUSIC NOTES (浮动音符)
    if note:
        nx = hx - (28 if note == 1 else 32)
        ny = hy - (11 if note == 1 else 18)
        music = "#78c9ea"
        d.rectangle((nx + 2, ny + 1, nx + 3, ny + 9), fill=music)
        d.rectangle((nx + 9, ny, nx + 10, ny + 8), fill=music)
        d.polygon([(nx + 2, ny + 1), (nx + 9, ny), (nx + 10, ny + 2), (nx + 3, ny + 3)], fill=music)
        d.ellipse((nx - 1, ny + 8, nx + 3, ny + 11), fill=music)
        d.ellipse((nx + 6, ny + 7, nx + 10, ny + 10), fill=music)

    # 11. CRUMBS (拆家碎屑)
    if crumbs:
        for cx, cy in [(hx - 23, hy + 10), (hx - 27, hy + 5), (hx - 25, hy + 15), (hx - 20, hy + 18)]:
            d.rectangle((cx, cy, cx + 2, cy + 2), fill=c["shade"])
            
    return im

def sleeping_bird_q_optimized(puff=0, head=0, zzz=0):
    """母鸡蹲/农民揣 熟睡团子 (收脚进肚皮，身体压扁软糖)"""
    im = Image.new("RGBA", (100, 80))
    d = ImageDraw.Draw(im)
    c = C
    
    # 尾巴压在身后
    d.polygon([(61, 58), (97, 63), (98, 68), (67, 71), (59, 66)], fill=c["ink"])
    d.polygon([(64, 59), (95, 64), (92, 67), (66, 68)], fill=c["dark"])
    d.line([(71, 63), (93, 65)], fill=c["light"])

    # 压扁的胖团子身躯 (母鸡蹲无脚露出)
    top = 46 - puff
    d.ellipse((28 - puff, top, 80 + puff, 72), fill=c["ink"])
    d.ellipse((30 - puff, top + 2, 78 + puff, 70), fill=c["grey"])
    d.polygon([(34, 60), (62, 56), (75, 64), (69, 71), (37, 71)], fill=c["light"])
    
    # 收拢的翅膀
    d.polygon([(44, 54), (66, 55), (76, 63), (67, 70), (45, 66)], fill=c["ink"])
    d.polygon([(46, 56), (65, 57), (73, 63), (65, 68), (47, 65)], fill=c["dark"])
    d.line([(49, 65), (69, 65)], fill=c["white"], width=2)

    # 缩进胸脯的大头
    hx, hy = 24, 61 + head
    d.ellipse((hx - 13, hy - 13, hx + 13, hy + 13), fill=c["ink"])
    d.ellipse((hx - 12, hy - 12, hx + 11, hy + 12), fill=c["yellow"])
    d.polygon([(hx + 6, hy - 9), (hx + 12, hy - 5), (hx + 13, hy + 9), (hx + 6, hy + 12)], fill=c["white"])
    d.ellipse((hx - 3, hy + 1, hx + 8, hy + 11), fill=c["cheek"])
    
    # 顺滑贴背的呆毛
    d.polygon([(hx - 6, hy - 11), (hx + 7, hy - 15), (hx + 18, hy - 10), (hx + 7, hy - 8)], fill=c["shade"])
    d.line([(hx - 4, hy - 12), (hx + 17, hy - 11)], fill=c["yellow"], width=3)
    
    # 闭眼沉睡线
    d.line([(hx - 9, hy - 2), (hx - 6, hy - 1), (hx - 3, hy - 2)], fill=c["ink"], width=2)

    # 嘴喙
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

    # 软萌 z Z
    if zzz:
        zc = "#8bb8d0"
        zx = 72 + (2 if zzz == 2 else 0)
        zy = 8 if zzz == 1 else 4
        for ox, oy, size in [(0, 7, 5), (8, 0, 4)]:
            x, y = zx + ox, zy + oy
            d.line([(x, y), (x + size, y), (x, y + size), (x + size, y + size)], fill=zc, width=1)
    return im

def make_radiating_wedge(origin, angle_deg, r_start, r_end, w_start, w_end):
    """Generate a wedge radiating from origin at angle_deg (180=left, 90=up).
    Narrow base at r_start with half-width w_start.
    Wide tip at r_end with half-width w_end.
    Returns (outer_polygon, inner_polygon).
    """
    ox, oy = origin
    rad = math.radians(angle_deg)
    ux = math.cos(rad)
    uy = -math.sin(rad)
    px = -uy
    py = ux

    p1 = (ox + ux * r_start - px * w_start, oy + uy * r_start - py * w_start)
    p2 = (ox + ux * r_start + px * w_start, oy + uy * r_start + py * w_start)
    p3 = (ox + ux * r_end + px * w_end,     oy + uy * r_end + py * w_end)
    p4 = (ox + ux * r_end - px * w_end,     oy + uy * r_end - py * w_end)

    r_in_start = r_start + 1.2
    r_in_end = r_end - 1.2
    w_in_start = max(0.5, w_start - 0.9)
    w_in_end = max(1.0, w_end - 1.0)
    q1 = (ox + ux * r_in_start - px * w_in_start, oy + uy * r_in_start - py * w_in_start)
    q2 = (ox + ux * r_in_start + px * w_in_start, oy + uy * r_in_start + py * w_in_start)
    q3 = (ox + ux * r_in_end + px * w_in_end,     oy + uy * r_in_end + py * w_in_end)
    q4 = (ox + ux * r_in_end - px * w_in_end,     oy + uy * r_in_end - py * w_in_end)

    return [p1, p2, p3, p4], [q1, q2, q3, q4]

def draw_mouth_radiating_sound(im, mouth_origin=(16, 35), gap=4.5):
    """Draw 3 sound wedges radiating OUTWARDS from the mouth.
    Narrow ends near mouth, widening as they shoot forward and upward into the air.
    """
    im = im.copy()
    d = ImageDraw.Draw(im)
    ox, oy = mouth_origin
    c_yellow = "#ffd100"
    c_orange = "#ff9800"
    c_dark = "#4a3b2c"

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

    for outer, inner in [(top_out, top_in), (mid_out, mid_in), (bot_out, bot_in)]:
        outer_pts = [(round(x), round(y)) for x, y in outer]
        inner_pts = [(round(x), round(y)) for x, y in inner]
        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            d.polygon([(x + dx, y + dy) for x, y in outer_pts], fill=c_dark)
        d.polygon(outer_pts, fill=c_yellow)
        d.polygon(inner_pts, fill=c_orange)

    d.point((ox - 2, oy - 1), fill=c_yellow)
    d.point((ox - 3, oy - 2), fill=c_orange)

    return im

def render_bird_flight_custom(
    wing_phase=0,      # 0: Up Apex, 1: Power Down, 2: Bottom Lift, 3: Recovery Fold
    lift=-6,
    head=(-2, -1),
    tail_angle=0,
    crest_style="streamline",
    eye="wide"
):
    """Render a dedicated 100x80 aerodynamic flight frame with organic wing mechanics."""
    im = Image.new("RGBA", (100, 80))
    d = ImageDraw.Draw(im)
    c = C

    # 1. TAIL (尾羽 - 随下扑升力调整展翼舵角)
    tx_off = tail_angle
    tail_pts_outer = [
        (61, 47 + lift),
        (96 + tx_off, 49 + lift),
        (98 + tx_off, 53 + lift),
        (68, 56 + lift),
        (60, 52 + lift)
    ]
    d.polygon(tail_pts_outer, fill=c["ink"])
    d.polygon([
        (63, 48 + lift),
        (95 + tx_off, 50 + lift),
        (92 + tx_off, 53 + lift),
        (67, 53 + lift)
    ], fill=c["dark"])
    d.line([(71, 51 + lift), (92 + tx_off, 51 + lift)], fill=c["light"])

    # 2. FAR WING (远侧后翅 - 具立体透视阴影)
    far_shapes = {
        0: [(53, 41), (74, 8), (81, 4), (72, 38)],
        1: [(54, 42), (84, 25), (96, 28), (76, 46), (62, 49)],
        2: [(53, 44), (75, 62), (80, 65), (65, 54)],
        3: [(52, 41), (68, 22), (76, 27), (65, 40)]
    }[wing_phase]
    d.polygon([(x, y + lift) for x, y in far_shapes], fill=c["dark"])

    # 3. TUCKED FEET (飞行小爪紧贴胖肚皮)
    for fx in (48, 56):
        d.line([(fx, 62 + lift), (fx + 4, 62 + lift)], fill=c["ink"], width=2)
        d.line([(fx, 62 + lift), (fx + 4, 62 + lift)], fill=c["foot"], width=1)

    # 4. STREAMLINED CHUBBY BODY (前倾流线型身躯)
    body_x0 = 33
    body_y0 = 32 + lift
    body_x1 = 73
    body_y1 = 68 + lift
    d.ellipse((body_x0, body_y0, body_x1, body_y1), fill=c["ink"])
    d.ellipse((body_x0 + 2, body_y0 + 2, body_x1 - 2, body_y1 - 2), fill=c["grey"])
    d.ellipse((body_x0 + 4, body_y0 + 6, body_x0 + 24, body_y1 - 6), fill=c["light"])

    # 5. NEAR WING (近侧主翼 - 具受风微弧度与饱满纯白飞羽斑)
    if wing_phase == 0:
        near_outer = [(48, 43), (55, 23), (62, 5), (68, 7), (67, 30), (56, 50)]
        near_white = [(51, 41), (58, 21), (63, 11), (63, 27), (55, 46)]
    elif wing_phase == 1:
        near_outer = [(47, 43), (63, 33), (85, 28), (92, 33), (86, 46), (68, 53), (54, 52)]
        near_white = [(50, 42), (66, 35), (84, 32), (80, 43), (64, 48), (53, 48)]
    elif wing_phase == 2:
        near_outer = [(48, 44), (58, 52), (74, 66), (78, 70), (72, 73), (63, 64), (54, 56)]
        near_white = [(51, 46), (60, 53), (73, 67), (68, 68), (55, 54)]
    else:
        near_outer = [(48, 43), (56, 30), (66, 26), (76, 37), (73, 44), (60, 48), (52, 50)]
        near_white = [(51, 41), (58, 31), (67, 28), (70, 36), (61, 44), (54, 46)]

    d.polygon([(x, y + lift) for x, y in near_outer], fill=c["ink"])
    d.polygon([(x, y + lift) for x, y in near_white], fill=c["white"])

    # 6. NECK & HEAD (前探流线型颈部与大头)
    hx = 33 + head[0]
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

    d.ellipse((hx - 13, hy - 13, hx + 13, hy + 13), fill=c["ink"])
    d.ellipse((hx - 12, hy - 12, hx + 11, hy + 12), fill=c["yellow"])
    d.polygon([(hx + 6, hy - 9), (hx + 12, hy - 5), (hx + 13, hy + 9), (hx + 6, hy + 12)], fill=c["white"])
    d.ellipse((hx - 3, hy + 1, hx + 8, hy + 11), fill=c["cheek"])

    # 7. CREST (羽冠 - 顺风流线型后掠，速度感十足)
    if crest_style == "streamline":
        wave_y = 1 if wing_phase in (1, 2) else 0
        crest_outer = [
            (hx - 4, hy - 11),
            (hx + 8, hy - 18 + wave_y),
            (hx + 20, hy - 16 + wave_y),
            (hx + 17, hy - 11),
            (hx + 5, hy - 9)
        ]
        crest_inner = [
            (hx - 2, hy - 12),
            (hx + 7, hy - 17 + wave_y),
            (hx + 19, hy - 15 + wave_y),
            (hx + 15, hy - 12),
            (hx + 3, hy - 10)
        ]
        d.polygon(crest_outer, fill=c["shade"])
        d.polygon(crest_inner, fill=c["yellow"])
    else:
        d.polygon([(hx - 5, hy - 10), (hx - 1, hy - 28), (hx + 2, hy - 30), (hx + 3, hy - 11)], fill=c["shade"])
        d.polygon([(hx, hy - 11), (hx + 7, hy - 25), (hx + 9, hy - 24), (hx + 4, hy - 9)], fill=c["yellow"])

    # 8. EYES
    d.ellipse((hx - 9, hy - 7, hx - 3, hy + 1), fill=c["ink"])
    d.point((hx - 7, hy - 5), fill=c["white"])

    # 9. BEAK
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

    return im

def render_true_ground_peck_frame(phase=0):
    """Render a dedicated 100x80 frame where the bird realistically pecks the ground.
    Ground baseline is at y = 72.
    phase:
      0: 瞄准准备 (Aim): 低头瞄准，羽冠微弓自然下垂
      1: 触地啄击 (Strike): 刚体鸟喙精准触地，羽冠急停大甩鞭！(嘴壳绝对刚体不变形)
      2: 触地回弹 (Rebound): 头部微弹起，羽冠滞后拉扯，小嘴轻嚼谷粒
      3: 抬头嚼食 (Recover): 头部回正顺势嚼食，羽冠弹性回振微颤
    """
    im = Image.new("RGBA", (100, 80))
    d = ImageDraw.Draw(im)
    c = C

    if phase == 0:
        # Phase 0: 瞄准准备 (Look down)
        body_tilt_y = 2
        body_x0, body_y0, body_x1, body_y1 = 33, 34, 71, 70
        tail_lift = -4       # 尾巴微翘
        hx, hy = 29, 41      # 头低向地面
        eye_look = "down"
        crest_mode = "peck_aim"
        feet_press = 0
        tap_spark = False
        beak_rot = -28

    elif phase == 1:
        # Phase 1: 触地啄击 (Strike - 刚体鸟喙触地，羽冠惯性大甩鞭！)
        body_tilt_y = 4
        body_x0, body_y0, body_x1, body_y1 = 31, 36, 69, 71
        tail_lift = -12      # 尾巴高高翘起 (超萌翘臀杠杆感)
        hx, hy = 21, 56      # 头部深度下潜，刚体鸟喙自然触地
        eye_look = "down"
        crest_mode = "peck_impact_whip"
        feet_press = 1       # 脚爪吃力抓地
        tap_spark = True     # 触地清脆微粒
        beak_rot = -42       # 刚体无形变旋转角度

    elif phase == 2:
        # Phase 2: 触地回弹 (Rebound & Nibble)
        body_tilt_y = 3
        body_x0, body_y0, body_x1, body_y1 = 32, 35, 70, 70
        tail_lift = -8       # 尾巴保持微翘
        hx, hy = 26, 46      # 受地面反作用力微弹起
        eye_look = "happy"
        crest_mode = "peck_rebound_lag"
        feet_press = 0
        tap_spark = False
        beak_rot = -20

    else:
        # Phase 3: 抬头嚼食 (Lift & Recover)
        body_tilt_y = 0
        body_x0, body_y0, body_x1, body_y1 = 34, 33, 72, 69
        tail_lift = -2       # 尾巴平稳回落
        hx, hy = 32, 35      # 顺势抬头
        eye_look = "happy"   # 享受吧唧嘴
        crest_mode = "peck_recover_settle"
        feet_press = 0
        tap_spark = False
        beak_rot = 0

    # 1. TAIL (尾羽 - 随身体前俯杠杆翘起)
    tail_pts_outer = [
        (61, 49 + body_tilt_y),
        (96, 51 + tail_lift),
        (98, 55 + tail_lift),
        (68, 57 + body_tilt_y),
        (60, 53 + body_tilt_y)
    ]
    d.polygon(tail_pts_outer, fill=c["ink"])
    d.polygon([
        (63, 50 + body_tilt_y),
        (95, 52 + tail_lift),
        (92, 54 + tail_lift),
        (67, 54 + body_tilt_y)
    ], fill=c["dark"])
    d.line([(71, 52 + body_tilt_y), (92, 53 + tail_lift)], fill=c["light"])

    # 2. FEET (双脚 - 稳固踩在地面 y=72)
    feet = [(45, 41), (57, 54)]
    for fx, toe in feet:
        d.line([(fx, 65 + feet_press), (toe, 72)], fill=c["ink"], width=3)
        d.line([(fx, 65 + feet_press), (toe, 72)], fill=c["foot"], width=2)
        d.line([(toe - 3, 72), (toe + 2, 72)], fill=c["foot"], width=2)

    # 3. BODY (圆滚滚麻薯身躯 - 前倾俯冲姿态)
    d.ellipse((body_x0, body_y0, body_x1, body_y1), fill=c["ink"])
    d.ellipse((body_x0 + 2, body_y0 + 2, body_x1 - 2, body_y1 - 2), fill=c["grey"])
    d.ellipse((body_x0 + 4, body_y0 + 6, body_x0 + 22, body_y1 - 5), fill=c["light"])

    # 4. WING (近侧翅膀 - 随身体前俯紧收后翘)
    wing_pts = [
        (47, 39 + body_tilt_y),
        (65, 42 + body_tilt_y + tail_lift // 3),
        (76, 52 + body_tilt_y + tail_lift // 2),
        (63, 61 + body_tilt_y),
        (47, 54 + body_tilt_y)
    ]
    d.polygon(wing_pts, fill=c["ink"])
    d.polygon([(x + 1, y + 1) for x, y in wing_pts[:-1]], fill=c["dark"])
    # 纯白大翅斑
    d.polygon([
        (49, 46 + body_tilt_y),
        (54, 47 + body_tilt_y),
        (62, 54 + body_tilt_y + tail_lift // 4),
        (72, 54 + body_tilt_y + tail_lift // 3),
        (65, 60 + body_tilt_y),
        (56, 58 + body_tilt_y)
    ], fill=c["white"])

    # 5. NECK (伸长的下倾颈部)
    neck_pts = [
        (hx - 2, hy + 5),
        (hx + 10, hy + 2),
        (body_x0 + 16, body_y0 + 8),
        (body_x0 + 6, body_y0 + 17),
        (hx + 2, hy + 14)
    ]
    d.polygon(neck_pts, fill=c["ink"])
    d.polygon([(x, y) for x, y in neck_pts[:-1]], fill=c["grey"])

    # 6. HEAD & CHEEKS (大头俯探)
    d.ellipse((hx - 13, hy - 13, hx + 13, hy + 13), fill=c["ink"])
    d.ellipse((hx - 12, hy - 12, hx + 11, hy + 12), fill=c["yellow"])
    d.polygon([(hx + 6, hy - 9), (hx + 12, hy - 5), (hx + 13, hy + 9), (hx + 6, hy + 12)], fill=c["white"])
    # 招牌橘色大腮红
    d.ellipse((hx - 3, hy + 1, hx + 8, hy + 11), fill=c["cheek"])

    # 7. CREST INERTIA (羽冠惯性动力学)
    if crest_mode == "peck_impact_whip":
        # 撞地瞬间！急停导致羽冠受前冲惯性大甩鞭！向前弧形弯卷
        crest_poly_outer = [
            (hx - 5, hy - 9),
            (hx - 11, hy - 17),
            (hx - 16, hy - 20),
            (hx - 13, hy - 25),
            (hx - 7, hy - 17),
            (hx + 2, hy - 10)
        ]
        crest_poly_inner = [
            (hx - 4, hy - 10),
            (hx - 10, hy - 17),
            (hx - 14, hy - 20),
            (hx - 12, hy - 24),
            (hx - 6, hy - 17),
            (hx + 1, hy - 11)
        ]
    elif crest_mode == "peck_rebound_lag":
        # 反弹微抬时：惯性向下向后滞后拉扯
        crest_poly_outer = [
            (hx - 6, hy - 10),
            (hx, hy - 20),
            (hx + 9, hy - 26),
            (hx + 12, hy - 22),
            (hx + 4, hy - 12),
            (hx + 2, hy - 10)
        ]
        crest_poly_inner = [
            (hx - 4, hy - 11),
            (hx + 1, hy - 19),
            (hx + 8, hy - 25),
            (hx + 10, hy - 22),
            (hx + 3, hy - 12),
            (hx + 1, hy - 11)
        ]
    elif crest_mode == "peck_aim":
        # 瞄准准备：轻微下探，微弓弧线
        crest_poly_outer = [
            (hx - 5, hy - 10),
            (hx - 3, hy - 24),
            (hx + 1, hy - 28),
            (hx + 3, hy - 24),
            (hx + 3, hy - 11)
        ]
        crest_poly_inner = [
            (hx - 3, hy - 11),
            (hx - 1, hy - 23),
            (hx + 2, hy - 26),
            (hx + 2, hy - 22),
            (hx + 2, hy - 10)
        ]
    else: # peck_recover_settle
        # 恢复站立：自然微弯软萌回弹
        crest_poly_outer = [
            (hx - 7, hy - 11),
            (hx + 1, hy - 21),
            (hx + 14, hy - 26),
            (hx + 12, hy - 19),
            (hx + 3, hy - 10)
        ]
        crest_poly_inner = [
            (hx - 5, hy - 12),
            (hx + 2, hy - 20),
            (hx + 13, hy - 25),
            (hx + 10, hy - 20),
            (hx + 1, hy - 11)
        ]

    d.polygon(crest_poly_outer, fill=c["shade"])
    d.polygon(crest_poly_inner, fill=c["yellow"])

    # 8. EYES (眼神视线聚焦于桌面小石子/谷粒)
    if eye_look == "down":
        d.ellipse((hx - 8, hy - 5, hx - 4, hy), fill=c["ink"])
        d.point((hx - 6, hy - 2), fill=c["white"])
    else:
        # 眯眯笑眼 (享受吃小米)
        d.line([(hx - 9, hy - 1), (hx - 6, hy - 4), (hx - 3, hy - 1)], fill=c["ink"], width=2)
        d.point((hx + 2, hy + 6), fill=c["blush"])

    # 9. RIGID BEAK (绝对刚体鸟喙 - 零拉伸零形变)
    def rotate_point(px, py, ox, oy, angle_deg):
        rad = math.radians(angle_deg)
        cos_a = math.cos(rad)
        sin_a = math.sin(rad)
        dx = px - ox
        dy = py - oy
        rx = dx * cos_a - dy * sin_a
        ry = dx * sin_a + dy * cos_a
        return (round(ox + rx), round(oy + ry))

    ox, oy = hx - 9, hy + 2
    orig_upper = [
        (hx - 10, hy - 2), (hx - 13, hy - 2), (hx - 15, hy),
        (hx - 16, hy + 2), (hx - 16, hy + 4), (hx - 14, hy + 6),
        (hx - 13, hy + 8), (hx - 13, hy + 5), (hx - 10, hy + 2)
    ]
    orig_inner = [
        (hx - 11, hy - 1), (hx - 13, hy - 1), (hx - 15, hy + 1),
        (hx - 15, hy + 4), (hx - 13, hy + 6), (hx - 13, hy + 5),
        (hx - 10, hy + 2)
    ]
    upper_beak_pts = [rotate_point(x, y, ox, oy, beak_rot) for x, y in orig_upper]
    upper_beak_inner = [rotate_point(x, y, ox, oy, beak_rot) for x, y in orig_inner]

    if phase == 2:
        orig_lower = [(hx - 11, hy + 6), (hx - 14, hy + 9), (hx - 12, hy + 11), (hx - 9, hy + 8)]
        orig_lower_in = [(hx - 11, hy + 7), (hx - 13, hy + 9), (hx - 11, hy + 10)]
    else:
        orig_lower = [(hx - 11, hy + 4), (hx - 13, hy + 6), (hx - 11, hy + 8), (hx - 9, hy + 6)]
        orig_lower_in = [(hx - 11, hy + 5), (hx - 12, hy + 6), (hx - 10, hy + 7)]

    lower_beak = [rotate_point(x, y, ox, oy, beak_rot) for x, y in orig_lower]
    lower_beak_in = [rotate_point(x, y, ox, oy, beak_rot) for x, y in orig_lower_in]

    d.polygon(lower_beak, fill=c["ink"])
    d.polygon(lower_beak_in, fill=c["beak"])
    d.polygon(upper_beak_pts, fill=c["ink"])
    d.polygon(upper_beak_inner, fill=c["beak"])
    d.point(rotate_point(hx - 14, hy + 1, ox, oy, beak_rot), fill="#c8b8b5")

    if phase == 2:
        seed_pos = rotate_point(hx - 13, hy + 8, ox, oy, beak_rot)
        d.point(seed_pos, fill="#ffcc00")
        d.point((seed_pos[0] + 1, seed_pos[1]), fill="#ffa000")
    elif phase == 3:
        d.point((hx - 15, hy + 6), fill="#ffcc00")

    # 10. GROUND IMPACT TAP PARTICLES (触地瞬间清脆微星斑)
    if tap_spark:
        tip_pt = max(upper_beak_pts, key=lambda p: p[1])
        for sx, sy in [(tip_pt[0] - 2, tip_pt[1] + 1), (tip_pt[0], tip_pt[1] + 2), (tip_pt[0] + 3, tip_pt[1] + 1)]:
            d.point((sx, sy), fill="#ffd100")
        d.point((tip_pt[0] - 3, tip_pt[1]), fill="#ffffff")
        d.point((tip_pt[0] + 4, tip_pt[1]), fill="#ff9800")

    return im

def render_bonk_screen_frame(frame_idx=0):
    """Render 100x80 frame for Screen Bonking with dynamic crest inertia.
    frame_idx:
      0: 蓄力后仰 (Anticipation / Pullback): 头部后拉，羽冠受惯性保持前方微弓弧度
      1: 疾步前冲 (Forward Lunge): 头部超高速前倾冲刺！羽冠迎风受阻，大幅向后破风漂浮！
      2: 撞屏瞬间！(Glass Impact Bonk!): 喙尖撞击硬屏骤停！羽冠受巨大前冲惯性猛烈向前大甩鞭！
      3: 震颤余响 (Recoil & Echo): 头部微弹后退，羽冠受反作用力回弹震颤，音波扩散
      4: 满足回位 (Settle): 头部复位，羽冠骄傲高耸抖擞微晃
    """
    im = Image.new("RGBA", (100, 80))
    d = ImageDraw.Draw(im)
    c = C

    if frame_idx == 0:
        head = (2, -3)
        body_roll = 0
        tail_wag = -1
        step = 0
        eye = "open"
        crest_mode = "bonk_windup"

    elif frame_idx == 1:
        head = (-8, 1)
        body_roll = -3
        tail_wag = 3
        step = 1
        eye = "open"
        crest_mode = "bonk_lunge_wind"

    elif frame_idx == 2:
        head = (-13, 4)
        body_roll = -6
        tail_wag = 5
        step = 1
        eye = "wide"
        crest_mode = "bonk_impact_whip"

    elif frame_idx == 3:
        head = (-11, 4)
        body_roll = -5
        tail_wag = 4
        step = 1
        eye = "happy"
        crest_mode = "bonk_recoil_snap"

    else: # frame_idx == 4
        head = (-3, -1)
        body_roll = -1
        tail_wag = 1
        step = 0
        eye = "happy"
        crest_mode = "bonk_settle_proud"

    bx_off = body_roll
    tx_off = tail_wag
    lift = 0

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

    # 5. NECK
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

    # 7. CREST INERTIA (敲击屏幕惯性羽冠)
    if crest_mode == "bonk_impact_whip":
        crest_outer = [
            (hx - 5, hy - 9),
            (hx - 12, hy - 16),
            (hx - 18, hy - 18),
            (hx - 15, hy - 23),
            (hx - 7, hy - 16),
            (hx + 2, hy - 10)
        ]
        crest_inner = [
            (hx - 4, hy - 10),
            (hx - 11, hy - 16),
            (hx - 16, hy - 18),
            (hx - 14, hy - 22),
            (hx - 6, hy - 16),
            (hx + 1, hy - 11)
        ]
    elif crest_mode == "bonk_lunge_wind":
        crest_outer = [
            (hx - 4, hy - 11),
            (hx + 8, hy - 19),
            (hx + 21, hy - 16),
            (hx + 18, hy - 11),
            (hx + 4, hy - 9)
        ]
        crest_inner = [
            (hx - 2, hy - 12),
            (hx + 7, hy - 18),
            (hx + 20, hy - 15),
            (hx + 16, hy - 12),
            (hx + 3, hy - 10)
        ]
    elif crest_mode == "bonk_recoil_snap":
        crest_outer = [
            (hx - 6, hy - 10),
            (hx - 2, hy - 24),
            (hx + 6, hy - 28),
            (hx + 4, hy - 22),
            (hx + 3, hy - 10)
        ]
        crest_inner = [
            (hx - 4, hy - 11),
            (hx - 1, hy - 23),
            (hx + 5, hy - 27),
            (hx + 3, hy - 22),
            (hx + 1, hy - 10)
        ]
    elif crest_mode == "bonk_windup":
        crest_outer = [
            (hx - 5, hy - 10),
            (hx - 2, hy - 26),
            (hx + 2, hy - 28),
            (hx + 3, hy - 11)
        ]
        crest_inner = [
            (hx - 1, hy - 11),
            (hx + 3, hy - 24),
            (hx + 5, hy - 23),
            (hx + 3, hy - 9)
        ]
    else: # bonk_settle_proud
        crest_outer = [
            (hx - 5, hy - 10),
            (hx - 1, hy - 28),
            (hx + 2, hy - 30),
            (hx + 3, hy - 11)
        ]
        crest_inner = [
            (hx, hy - 11),
            (hx + 7, hy - 25),
            (hx + 9, hy - 24),
            (hx + 4, hy - 9)
        ]

    d.polygon(crest_outer, fill=c["shade"])
    d.polygon(crest_inner, fill=c["yellow"])

    # 8. EYES
    if eye == "open":
        d.ellipse((hx - 8, hy - 5, hx - 4, hy), fill=c["ink"])
        d.point((hx - 7, hy - 4), fill=c["white"])
    elif eye == "wide":
        d.ellipse((hx - 9, hy - 7, hx - 3, hy + 1), fill=c["ink"])
        d.point((hx - 7, hy - 5), fill=c["white"])
    elif eye == "happy":
        d.line([(hx - 9, hy - 2), (hx - 6, hy - 5), (hx - 3, hy - 2)], fill=c["ink"], width=2)
        d.point((hx + 2, hy + 5), fill=c["blush"])

    # 9. BEAK (小鸟刚体鸟喙)
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

    # 10. SCREEN IMPACT BURST PARTICLES
    if frame_idx == 2:
        for bx, by in [(hx - 18, hy + 3), (hx - 19, hy + 5), (hx - 17, hy + 7), (hx - 20, hy + 2)]:
            d.point((bx, by), fill="#ffd100")
        d.point((hx - 18, hy + 4), fill="#ffffff")
    elif frame_idx == 3:
        for bx, by in [(hx - 19, hy + 1), (hx - 21, hy + 4), (hx - 18, hy + 8)]:
            d.point((bx, by), fill="#fff3a8")

    return im

def render_preen_back_frame(phase=0):
    """Render 100x80 pixel sprite for preening back feathers.
    phase:
      0: Turn & Enter (Head turned back 180°, beak touching wing/back)
      1: Deep Nibble (Head deeper into feathers, wing ruffles slightly)
      2: Pull & Preen (Beak nibbles feather strand, happy squint, tiny fluffy down particle)
      3: Relax & Settle (Beak loosens, feathers settle back)
    """
    im = Image.new("RGBA", (100, 80))
    d = ImageDraw.Draw(im)
    c = C

    if phase == 0:
        head_x, head_y = 48, 38
        wing_ruffle = 0
        eye_mode = "open"
        crest_wag = 0
        feather_particle = False
        body_breath = 0

    elif phase == 1:
        head_x, head_y = 50, 40
        wing_ruffle = 2
        eye_mode = "open"
        crest_wag = 1
        feather_particle = False
        body_breath = 1

    elif phase == 2:
        head_x, head_y = 49, 38
        wing_ruffle = 2
        eye_mode = "open"
        crest_wag = 2
        feather_particle = True
        body_breath = 1

    else:
        head_x, head_y = 47, 37
        wing_ruffle = 1
        eye_mode = "open"
        crest_wag = 0
        feather_particle = False
        body_breath = 0

    # 1. TAIL
    d.polygon([(61, 52), (96, 54), (98, 58), (68, 60), (60, 56)], fill=c["ink"])
    d.polygon([(63, 53), (95, 55), (92, 57), (67, 57)], fill=c["dark"])
    d.line([(71, 55), (92, 56)], fill=c["light"])

    # 2. FEET
    feet = [(45, 41), (57, 54)]
    for fx, toe in feet:
        d.line([(fx, 65), (toe, 72)], fill=c["ink"], width=3)
        d.line([(fx, 65), (toe, 72)], fill=c["foot"], width=2)
        d.line([(toe - 3, 72), (toe + 2, 72)], fill=c["foot"], width=2)

    # 3. BODY
    body_x0, body_y0 = 34, 34 - body_breath
    body_x1, body_y1 = 72, 70
    d.ellipse((body_x0, body_y0, body_x1, body_y1), fill=c["ink"])
    d.ellipse((body_x0 + 2, body_y0 + 2, body_x1 - 2, body_y1 - 2), fill=c["grey"])
    d.ellipse((body_x0 + 4, body_y0 + 10, body_x0 + 22, body_y1 - 4), fill=c["light"])

    # 4. NECK
    neck_pts = [
        (body_x0 + 6, body_y0 + 12),
        (head_x - 10, head_y + 4),
        (head_x - 6, head_y + 11),
        (body_x0 + 18, body_y0 + 16),
        (body_x0 + 12, body_y0 + 22)
    ]
    d.polygon(neck_pts, fill=c["ink"])
    d.polygon([(x + 1, y) for x, y in neck_pts[:-1]], fill=c["grey"])

    # 5. BASE WING
    base_wing = [
        (47, 40 - wing_ruffle),
        (65, 42 - wing_ruffle),
        (76, 53 + wing_ruffle // 2),
        (63, 62),
        (47, 55)
    ]
    d.polygon(base_wing, fill=c["ink"])
    d.polygon([(x + 1, y + 1) for x, y in base_wing[:-1]], fill=c["dark"])

    white_patch = [
        (49, 47 - wing_ruffle),
        (55, 48 - wing_ruffle),
        (63, 54),
        (73, 54),
        (66, 61),
        (56, 59)
    ]
    d.polygon(white_patch, fill=c["white"])

    # 6. HEAD
    hx, hy = head_x, head_y
    d.ellipse((hx - 13, hy - 13, hx + 13, hy + 13), fill=c["ink"])
    d.ellipse((hx - 12, hy - 12, hx + 12, hy + 12), fill=c["yellow"])
    # 颈后枕部浅白过渡羽 (在头后方，即左侧)
    d.polygon([
        (hx - 6, hy - 9),
        (hx - 12, hy - 5),
        (hx - 13, hy + 9),
        (hx - 6, hy + 12)
    ], fill=c["white"])

    # 7. CHEEK (招牌大腮红 - 正确镜像至眼后耳羽位置，位于头部左侧偏下，完全避免被嘴壳遮挡)
    d.ellipse((hx - 8, hy + 1, hx + 3, hy + 11), fill=c["cheek"])

    # 8. EYE (睁开大圆眼 - 专注低头注视背后羽毛，带灵动水润高光)
    if eye_mode == "blink":
        # 偶尔舒适微闭细线
        d.line([(hx + 3, hy - 3), (hx + 6, hy - 1), (hx + 8, hy - 3)], fill=c["ink"], width=2)
    else:
        # 睁开大圆眼 (5x6 萌系圆润大黑眼珠，与 idle/stand 保持统一风格)
        d.ellipse((hx + 3, hy - 6, hx + 7, hy - 1), fill=c["ink"])
        # 水润纯白高光点
        d.point((hx + 4, hy - 5), fill=c["white"])

    # 9. CREST
    crest_outer = [
        (hx + 3, hy - 10),
        (hx - 3, hy - 16),
        (hx - 11 - crest_wag, hy - 22 - crest_wag),
        (hx - 15 - crest_wag, hy - 20 - crest_wag),
        (hx - 8, hy - 13),
        (hx - 2, hy - 8)
    ]
    crest_inner = [
        (hx + 1, hy - 10),
        (hx - 3, hy - 15),
        (hx - 10 - crest_wag, hy - 20 - crest_wag),
        (hx - 13 - crest_wag, hy - 19 - crest_wag),
        (hx - 7, hy - 12),
        (hx - 1, hy - 7)
    ]
    d.polygon(crest_outer, fill=c["shade"])
    d.polygon(crest_inner, fill=c["yellow"])
    d.line([(hx - 1, hy - 11), (hx - 9 - crest_wag, hy - 18 - crest_wag)], fill=c["yellow"], width=1)

    # 10. RIGID BEAK (100% 完全不发生形变的固定小嘴壳 - 严格保持原版几何形状水平镜像)
    upper = [
        (hx + 9, hy - 1), (hx + 12, hy - 1), (hx + 14, hy + 1),
        (hx + 15, hy + 3), (hx + 15, hy + 5), (hx + 13, hy + 7),
        (hx + 12, hy + 9), (hx + 12, hy + 6), (hx + 9, hy + 3)
    ]
    inner = [
        (hx + 10, hy), (hx + 12, hy), (hx + 14, hy + 2),
        (hx + 14, hy + 5), (hx + 12, hy + 7), (hx + 12, hy + 6),
        (hx + 9, hy + 3)
    ]
    lower_out = [(hx + 10, hy + 5), (hx + 12, hy + 7), (hx + 10, hy + 9), (hx + 8, hy + 7)]
    lower_in = [(hx + 10, hy + 6), (hx + 11, hy + 7), (hx + 9, hy + 8)]

    d.polygon(lower_out, fill=c["ink"])
    d.polygon(lower_in, fill=c["beak"])
    d.polygon(upper, fill=c["ink"])
    d.polygon(inner, fill=c["beak"])
    d.point((hx + 13, hy + 2), fill="#c8b8b5")

    # 11. FEATHER DANDER / FLUFFY DOWN (极细小软白羽绒微粒)
    if feather_particle:
        d.point((hx + 17, hy + 1), fill="#ffffff")
        d.point((hx + 18, hy), fill="#ffffff")
        d.point((hx + 16, hy), fill="#eae6da")
        d.point((hx + 19, hy + 1), fill="#e0dcce")

    return im

def generate_optimized_suite():
    # 1. 走动 (Waddle) - 注入外八字左右重心摇摆与尾巴反向微颤！
    frames = {
        # 呼吸发呆
        "idle_0": bird_q_optimized(),
        "idle_1": bird_q_optimized(eye="closed"),
        "idle_2": bird_q_optimized(puff=1, head=(0, -1), crest="breath"), # 呼吸微起伏
        
        # 左右摇摆外八字鸭子步
        "waddle_0": bird_q_optimized(),
        "waddle_1": bird_q_optimized(step=1, head=(-2, 0), body_roll=-1, tail_wag=2), # 向左摇摆迈步
        "waddle_2": bird_q_optimized(),
        "waddle_3": bird_q_optimized(step=2, head=(1, 1), body_roll=1, tail_wag=-2),   # 向右摇摆迈步
        
        # 真实触地啄桌面与嚼食 (深潜触地 y=71、翘臀杠杆、反冲咀嚼)
        "peck_0": render_true_ground_peck_frame(phase=0), # 瞄准准备
        "peck_1": render_true_ground_peck_frame(phase=1), # 真实触地击打 (y=71)
        "peck_2": render_true_ground_peck_frame(phase=2), # 触地回弹轻嚼
        "peck_3": render_true_ground_peck_frame(phase=3), # 抬头嚼食复位
        "chew_0": bird_q_optimized(head=(-3, 3)),
        "chew_1": bird_q_optimized(head=(-5, 4), mouth="bite", crumbs=True),
        
        # 蓬毛团子
        "fluff_0": bird_q_optimized(puff=3, eye="closed", crest="low"),
        "fluff_1": bird_q_optimized(puff=5, eye="closed", crest="low", lift=-1),
        
        # 整理羽毛 (转头180°埋进背后羽毛细致啄理)
        "preen_0": render_preen_back_frame(phase=0),
        "preen_1": render_preen_back_frame(phase=1),
        "preen_2": render_preen_back_frame(phase=2),
        "preen_3": render_preen_back_frame(phase=3),
        
        # 求摸摸 (注入极致享受眯眯笑眼 ^_^)
        "bow_0": bird_q_optimized(head=(-5, 7), eye="closed", crest="low"),
        "bow_1": bird_q_optimized(head=(-8, 13), eye="happy", crest="low"), # 舒服眯眯笑眼！
        
        # 雀跃小跳
        "hop_0": bird_q_optimized(lift=1), # 起跳下蹲蓄力
        "hop_1": bird_q_optimized(lift=-6, step=1, tuck_feet=True), # 腾空悬空缩脚
        
        # 点头打节拍
        "bob_0": bird_q_optimized(head=(0, -2)),
        "bob_1": bird_q_optimized(head=(-3, 6)),
        
        # 心形翅膀
        "heart_wings_0": bird_q_optimized(wing="heart"),
        "heart_wings_1": bird_q_optimized(wing="heart", head=(0, -1)),
        
        # 唱歌独奏 (结合心形翅膀更蠢萌)
        "sing_0": bird_q_optimized(wing="heart", mouth="sing", note=1, crest="alert"),
        "sing_1": bird_q_optimized(wing="heart", mouth="sing", note=2, head=(0, -1), crest="alert"),
        "sing_2": bird_q_optimized(wing="heart", mouth="closed", head=(0, -1)),
        
        # 警觉
        "alert_0": bird_q_optimized(head=(0, -4), crest="alert", eye="wide"),
        
        # 敲击屏幕 (5帧物理冲击：迎风后掠、撞屏大甩鞭、余震反抽)
        "bonk_0": render_bonk_screen_frame(frame_idx=0),
        "bonk_1": render_bonk_screen_frame(frame_idx=1),
        "bonk_2": render_bonk_screen_frame(frame_idx=2),
        "bonk_3": render_bonk_screen_frame(frame_idx=3),
        "bonk_4": render_bonk_screen_frame(frame_idx=4),

        # 反咬受惊威慑 (以嘴巴为发散原点向前方辐射展开金黄三向音波)
        "bite_0": bird_q_optimized(head=(1, -2), body_roll=1, tail_wag=-1, crest="alert", eye="wide", mouth="closed"),
        "bite_1": draw_mouth_radiating_sound(bird_q_optimized(head=(-1, -1), body_roll=-1, tail_wag=3, crest="alert", eye="wide", mouth="bite"), mouth_origin=(15, 35), gap=4.5),
        "bite_2": draw_mouth_radiating_sound(bird_q_optimized(head=(0, 0), body_roll=-1, tail_wag=2, crest="alert", eye="wide", mouth="bite"), mouth_origin=(16, 36), gap=4.5),
        "bite_3": bird_q_optimized(head=(-1, -1), body_roll=0, tail_wag=1, crest="alert", eye="wide", mouth="closed"),
        
        # 哈气
        "hiss_0": bird_q_optimized(head=(-2, 2), puff=2, crest="alert", eye="wide", mouth="hiss"),
        "hiss_1": bird_q_optimized(head=(-4, 4), puff=5, crest="alert", eye="wide", mouth="hiss", lift=-1),
        
        # 飞行 (4帧有机动力学扑翼：风阻流线羽冠、升力沉浮、柔韧折翼)
        "fly_0": render_bird_flight_custom(wing_phase=0, lift=-4, head=(-2, -1), tail_angle=0),
        "fly_1": render_bird_flight_custom(wing_phase=1, lift=-6, head=(-3, 0), tail_angle=2),
        "fly_2": render_bird_flight_custom(wing_phase=2, lift=-8, head=(-3, 0), tail_angle=1),
        "fly_3": render_bird_flight_custom(wing_phase=3, lift=-5, head=(-2, -1), tail_angle=0),
        
        # 母鸡蹲睡觉 (双脚彻底收进肚子里，软糖压扁)
        "sleep_0": sleeping_bird_q_optimized(puff=0, head=-1, zzz=1),
        "sleep_1": sleeping_bird_q_optimized(puff=2, head=0, zzz=2),
        "wake_0": sleeping_bird_q_optimized(puff=0, head=-1),
        "wake_1": bird_q_optimized(crest="alert", eye="wide", head=(0, -2)),
    }
    
    # Save optimized sprites
    for name, img in frames.items():
        img.save(OUT_NEW / f"{name}.png")

    # Sync bite, fly & true ground peck frames to main assets/sprites directory
    assets_sprites = Path(r"D:\pets\assets\sprites")
    if assets_sprites.exists():
        for b_name in [
            "bite_0", "bite_1", "bite_2", "bite_3",
            "fly_0", "fly_1", "fly_2", "fly_3",
            "peck_0", "peck_1", "peck_2", "peck_3",
            "preen_0", "preen_1", "preen_2", "preen_3",
            "bonk_0", "bonk_1", "bonk_2", "bonk_3", "bonk_4",
            "wake_0", "wake_1", "sleep_0", "sleep_1"
        ]:
            if b_name in frames:
                frames[b_name].save(assets_sprites / f"{b_name}.png")
                print(f"Synced {b_name}.png to {assets_sprites}")
    
    # Also copy original backup sprites for 1-to-1 comparison
    src_orig = Path(r"D:\pets\backup_original\assets\sprites")
    if src_orig.exists():
        for f in src_orig.glob("*.png"):
            img = Image.open(f)
            img.save(OUT_ORIG / f.name)

    print(f"Generated {len(frames)} optimized Q-version sprites in {OUT_NEW}")

if __name__ == "__main__":
    generate_optimized_suite()
