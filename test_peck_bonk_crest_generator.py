"""Independent Test Generator for Cockatiel Ground Pecking and Screen Bonking
with Physical Crest Inertia Dynamics.

Generates side-by-side comparison GIFs and spritesheets:
- Ground Pecking (4 frames): Aim -> Impact Strike -> Rebound -> Chewing
- Screen Bonking (5 frames): Windup -> Forward Lunge -> Glass Impact -> Recoil -> Settle

Strictly for demonstration / preview - DOES NOT touch project production files.
"""

from pathlib import Path
import math
import shutil
from PIL import Image, ImageDraw

OUT_DIR = Path(r"D:\pets\test_peck_bonk")
OUT_DIR.mkdir(parents=True, exist_ok=True)

ARTIFACT_DIR = Path(r"C:\Users\26893\.gemini\antigravity\brain\5df30705-c1cf-4a9e-883a-019811f74aae")

C = dict(
    ink="#353438", grey="#69696d", light="#88878a", dark="#505055",
    white="#f5f1df", yellow="#fff081", shade="#eacb67", cheek="#e99342",
    beak="#a99b9a", foot="#bba5a5", blush="#f2826a"
)

# -------------------------------------------------------------
# Part 1: GROUND PECK WITH CREST INERTIA (啄地面 - 4 帧生物动力学循环)
# -------------------------------------------------------------

def render_ground_peck_inertia(phase=0):
    """
    Render 100x80 frame for Ground Peck with organic crest inertia.
    phase:
      0: 瞄准下探 (Aim & Lean Forward): 头部轻微下移，羽冠由于重力与初始下探轻微受阻保持垂直微后倾
      1: 触地瞬间 (Ground Strike): 头部骤停于 y=71！羽冠受巨大前冲惯性向前大甩鞭！
      2: 触地反弹 (Rebound): 头部受反作用力微弹起，羽冠反向受滞后拉扯向后回荡
      3: 抬头嚼食 (Lift & Recover): 头部复位，羽冠弹性回振至自然软萌微弯
    """
    im = Image.new("RGBA", (100, 80))
    d = ImageDraw.Draw(im)
    c = C

    if phase == 0:
        # Phase 0: 瞄准准备
        body_tilt_y = 2
        body_x0, body_y0, body_x1, body_y1 = 33, 34, 71, 70
        tail_lift = -4
        hx, hy = 29, 41
        eye_look = "down"
        feet_press = 0
        tap_spark = False
        # 羽冠状态: 初始下倾阶段，羽冠略显垂直自然微屈
        crest_mode = "peck_aim"

    elif phase == 1:
        # Phase 1: 触地猛烈击打！
        body_tilt_y = 4
        body_x0, body_y0, body_x1, body_y1 = 31, 36, 69, 71
        tail_lift = -12
        hx, hy = 23, 53      # 头部深度下压触地
        eye_look = "down"
        feet_press = 1
        tap_spark = True     # 地面清脆微粒
        # 羽冠状态: 急停撞击！羽冠惯性向前猛甩鞭！尖端前冲向嘴喙上方
        crest_mode = "peck_impact_whip"

    elif phase == 2:
        # Phase 2: 触地反弹
        body_tilt_y = 3
        body_x0, body_y0, body_x1, body_y1 = 32, 35, 70, 70
        tail_lift = -8
        hx, hy = 26, 46      # 头部受反冲弹起
        eye_look = "happy"
        feet_press = 0
        tap_spark = False
        # 羽冠状态: 向上弹起时，羽冠因滞后惯性向后飘扬下垂
        crest_mode = "peck_rebound_lag"

    else:
        # Phase 3: 抬头嚼食
        body_tilt_y = 0
        body_x0, body_y0, body_x1, body_y1 = 34, 33, 72, 69
        tail_lift = -2
        hx, hy = 32, 35      # 顺势抬头
        eye_look = "happy"
        feet_press = 0
        tap_spark = False
        # 羽冠状态: 弹性回弹，软萌自然微颤
        crest_mode = "peck_recover_settle"

    # 1. TAIL (尾羽)
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

    # 2. FEET (双脚 - y=72)
    feet = [(45, 41), (57, 54)]
    for fx, toe in feet:
        d.line([(fx, 65 + feet_press), (toe, 72)], fill=c["ink"], width=3)
        d.line([(fx, 65 + feet_press), (toe, 72)], fill=c["foot"], width=2)
        d.line([(toe - 3, 72), (toe + 2, 72)], fill=c["foot"], width=2)

    # 3. BODY (身躯)
    d.ellipse((body_x0, body_y0, body_x1, body_y1), fill=c["ink"])
    d.ellipse((body_x0 + 2, body_y0 + 2, body_x1 - 2, body_y1 - 2), fill=c["grey"])
    d.ellipse((body_x0 + 4, body_y0 + 6, body_x0 + 22, body_y1 - 5), fill=c["light"])

    # 4. WING (翅膀)
    wing_pts = [
        (47, 39 + body_tilt_y),
        (65, 42 + body_tilt_y + tail_lift // 3),
        (76, 52 + body_tilt_y + tail_lift // 2),
        (63, 61 + body_tilt_y),
        (47, 54 + body_tilt_y)
    ]
    d.polygon(wing_pts, fill=c["ink"])
    d.polygon([(x + 1, y + 1) for x, y in wing_pts[:-1]], fill=c["dark"])
    white_patch = [
        (49, 46 + body_tilt_y),
        (54, 47 + body_tilt_y),
        (62, 54 + body_tilt_y + tail_lift // 4),
        (72, 54 + body_tilt_y + tail_lift // 3),
        (65, 60 + body_tilt_y),
        (56, 58 + body_tilt_y)
    ]
    d.polygon(white_patch, fill=c["white"])

    # 5. NECK
    neck_pts = [
        (hx - 2, hy + 5),
        (hx + 10, hy + 2),
        (body_x0 + 16, body_y0 + 8),
        (body_x0 + 6, body_y0 + 17),
        (hx + 2, hy + 14)
    ]
    d.polygon(neck_pts, fill=c["ink"])
    d.polygon([(x, y) for x, y in neck_pts[:-1]], fill=c["grey"])

    # 6. HEAD & CHEEKS
    d.ellipse((hx - 13, hy - 13, hx + 13, hy + 13), fill=c["ink"])
    d.ellipse((hx - 12, hy - 12, hx + 11, hy + 12), fill=c["yellow"])
    d.polygon([(hx + 6, hy - 9), (hx + 12, hy - 5), (hx + 13, hy + 9), (hx + 6, hy + 12)], fill=c["white"])
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

    # 8. EYES
    if eye_look == "down":
        d.ellipse((hx - 8, hy - 5, hx - 4, hy), fill=c["ink"])
        d.point((hx - 6, hy - 2), fill=c["white"])
    else:
        d.line([(hx - 9, hy - 1), (hx - 6, hy - 4), (hx - 3, hy - 1)], fill=c["ink"], width=2)
        d.point((hx + 2, hy + 6), fill=c["blush"])

    # 9. BEAK (小鸟啄地喙)
    def rotate_point(px, py, ox, oy, angle_deg):
        rad = math.radians(angle_deg)
        cos_a = math.cos(rad)
        sin_a = math.sin(rad)
        dx = px - ox
        dy = py - oy
        rx = dx * cos_a - dy * sin_a
        ry = dx * sin_a + dy * cos_a
        return (round(ox + rx), round(oy + ry))

    if phase == 1:
        # 触地！嘴尖在 (14, 71)
        upper_beak_pts = [
            (hx - 10, hy + 2), (hx - 13, hy + 3), (hx - 15, hy + 6), (hx - 14, hy + 10),
            (14, 71), (17, 68), (hx - 7, hy + 9), (hx - 8, hy + 4)
        ]
        upper_beak_inner = [
            (hx - 10, hy + 3), (hx - 12, hy + 4), (hx - 14, hy + 7), (hx - 13, hy + 10),
            (14, 70), (16, 68), (hx - 8, hy + 8), (hx - 9, hy + 5)
        ]
        lower_beak = [(hx - 8, hy + 8), (16, 67), (18, 65), (hx - 6, hy + 7)]
        d.polygon(lower_beak, fill=c["ink"])
        d.polygon([(x, y) for x, y in lower_beak], fill=c["beak"])
        d.polygon(upper_beak_pts, fill=c["ink"])
        d.polygon(upper_beak_inner, fill=c["beak"])
        d.point((15, 69), fill="#c8b8b5")
        d.point((hx - 11, hy + 4), fill="#c8b8b5")

        # 触地清脆微粒
        if tap_spark:
            spark_c = "#ffffff"
            for sx, sy in [(11, 71), (13, 69), (17, 72), (18, 70)]:
                d.point((sx, sy), fill=spark_c)

    elif phase == 0:
        ox, oy = hx - 9, hy + 2
        rot_ang = -28
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
        upper_beak_pts = [rotate_point(x, y, ox, oy, rot_ang) for x, y in orig_upper]
        upper_beak_inner = [rotate_point(x, y, ox, oy, rot_ang) for x, y in orig_inner]
        orig_lower = [(hx - 11, hy + 4), (hx - 13, hy + 6), (hx - 11, hy + 8), (hx - 9, hy + 6)]
        orig_lower_in = [(hx - 11, hy + 5), (hx - 12, hy + 6), (hx - 10, hy + 7)]
        lower_beak = [rotate_point(x, y, ox, oy, rot_ang) for x, y in orig_lower]
        lower_beak_in = [rotate_point(x, y, ox, oy, rot_ang) for x, y in orig_lower_in]
        d.polygon(lower_beak, fill=c["ink"])
        d.polygon(lower_beak_in, fill=c["beak"])
        d.polygon(upper_beak_pts, fill=c["ink"])
        d.polygon(upper_beak_inner, fill=c["beak"])
        d.point(rotate_point(hx - 14, hy + 1, ox, oy, rot_ang), fill="#c8b8b5")

    elif phase == 2:
        ox, oy = hx - 9, hy + 2
        rot_ang = -20
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
        upper_beak_pts = [rotate_point(x, y, ox, oy, rot_ang) for x, y in orig_upper]
        upper_beak_inner = [rotate_point(x, y, ox, oy, rot_ang) for x, y in orig_inner]
        orig_lower = [(hx - 11, hy + 5), (hx - 13, hy + 7), (hx - 11, hy + 9), (hx - 9, hy + 7)]
        orig_lower_in = [(hx - 11, hy + 6), (hx - 12, hy + 7), (hx - 10, hy + 8)]
        lower_beak = [rotate_point(x, y, ox, oy, rot_ang) for x, y in orig_lower]
        lower_beak_in = [rotate_point(x, y, ox, oy, rot_ang) for x, y in orig_lower_in]
        d.polygon(lower_beak, fill=c["ink"])
        d.polygon(lower_beak_in, fill=c["beak"])
        d.polygon(upper_beak_pts, fill=c["ink"])
        d.polygon(upper_beak_inner, fill=c["beak"])
        d.point(rotate_point(hx - 14, hy + 1, ox, oy, rot_ang), fill="#c8b8b5")
        # 嘴衔金黄小米粒
        d.rectangle((hx - 15, hy + 7, hx - 13, hy + 9), fill="#ffd24a")

    else: # phase 3
        ox, oy = hx - 9, hy + 2
        rot_ang = -5
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
        upper_beak_pts = [rotate_point(x, y, ox, oy, rot_ang) for x, y in orig_upper]
        upper_beak_inner = [rotate_point(x, y, ox, oy, rot_ang) for x, y in orig_inner]
        orig_lower = [(hx - 11, hy + 4), (hx - 13, hy + 6), (hx - 11, hy + 8), (hx - 9, hy + 6)]
        orig_lower_in = [(hx - 11, hy + 5), (hx - 12, hy + 6), (hx - 10, hy + 7)]
        lower_beak = [rotate_point(x, y, ox, oy, rot_ang) for x, y in orig_lower]
        lower_beak_in = [rotate_point(x, y, ox, oy, rot_ang) for x, y in orig_lower_in]
        d.polygon(lower_beak, fill=c["ink"])
        d.polygon(lower_beak_in, fill=c["beak"])
        d.polygon(upper_beak_pts, fill=c["ink"])
        d.polygon(upper_beak_inner, fill=c["beak"])
        d.point(rotate_point(hx - 14, hy + 1, ox, oy, rot_ang), fill="#c8b8b5")

    return im

# -------------------------------------------------------------
# Part 2: SCREEN BONKING WITH CREST INERTIA (敲击屏幕 - 5 帧物理冲击循环)
# -------------------------------------------------------------

def render_bonk_screen_inertia(frame_idx=0):
    """
    Render 100x80 frame for Screen Bonking with dynamic crest inertia.
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
        mouth = "closed"
        dot_count = 0
        dot_shift = (0, 0)
        spark_style = None
        crest_mode = "bonk_windup"

    elif frame_idx == 1:
        head = (-8, 1)
        body_roll = -3
        tail_wag = 3
        step = 1
        eye = "open"
        mouth = "closed"
        dot_count = 1
        dot_shift = (0, 0)
        spark_style = None
        crest_mode = "bonk_lunge_wind" # 破风后掠！

    elif frame_idx == 2:
        head = (-13, 4)
        body_roll = -6
        tail_wag = 5
        step = 1
        eye = "wide"
        mouth = "bite"
        dot_count = 2
        dot_shift = (0, 0)
        spark_style = "spark"
        crest_mode = "bonk_impact_whip" # 撞屏大甩鞭！

    elif frame_idx == 3:
        head = (-11, 4)
        body_roll = -5
        tail_wag = 4
        step = 1
        eye = "happy"
        mouth = "closed"
        dot_count = 3
        dot_shift = (0, 0)
        spark_style = "spark"
        crest_mode = "bonk_recoil_snap" # 回弹反抽震颤！

    else: # frame_idx == 4
        head = (-3, -1)
        body_roll = -1
        tail_wag = 1
        step = 0
        eye = "happy"
        mouth = "closed"
        dot_count = 3
        dot_shift = (2, -3)
        spark_style = None
        crest_mode = "bonk_settle_proud" # 骄傲高耸复位！

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
        # 撞屏瞬间！急停导致羽冠受强烈前冲惯性猛烈向前大甩鞭！
        # 冠尖前探跨越额头，如灵动金黄软鞭直扑屏幕
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
        # 快速前冲突刺！羽冠迎风受阻，大幅向后掠（流线型大漂移）
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
        # 反弹微退！受反作用力回弹反抽，剧烈向上弓起震颤
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
        # 蓄力后仰：自然略挺，微弧前倾
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
        # 满足抖擞回位：高耸笔直挺拔
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

    # 10. SPARK / IMPACT
    if spark_style:
        beak_tip_x = max(2, hx - 16)
        beak_tip_y = hy + 3
        for dx, dy in [(-2, 0), (-1, 0), (1, 0), (2, 0), (0, -2), (0, -1), (0, 1), (0, 2)]:
            d.point((beak_tip_x + dx, beak_tip_y + dy), fill="#64c0eb")
        d.rectangle((beak_tip_x - 1, beak_tip_y - 1, beak_tip_x + 1, beak_tip_y + 1), fill="#ffffff")

    # 11. SOUND DOTS
    if dot_count > 0:
        base_dots = [
            (42, 13, 2),
            (52, 9, 3),
            (64, 7, 4),
        ]
        sx, sy = dot_shift
        for i in range(min(dot_count, 3)):
            bx, by, r = base_dots[i]
            cx, cy = bx + sx, by + sy
            d.ellipse((cx - r, cy - r, cx + r, cy + r), fill="#2b2a2e")
            d.ellipse((cx - r + 1, cy - r + 1, cx + r - 1, cy + r - 1), fill="#64c0eb")
            if r >= 3:
                d.point((cx - 1, cy - r + 2), fill="#ffffff")

    return im

# -------------------------------------------------------------
# Part 3: BUILD SUITE & COMPARISONS
# -------------------------------------------------------------

def build_comparison_suite():
    # A. PECK SUITE
    # 1. Old peck frames from assets
    peck_old = [Image.open(f"D:/pets/assets/sprites/peck_{i}.png") for i in range(4)]
    # 2. New inertia peck frames
    peck_new = [render_ground_peck_inertia(p) for p in range(4)]

    for i, f in enumerate(peck_new):
        f.save(OUT_DIR / f"peck_inertia_{i}.png")

    # Peck GIF 3x
    scaled_peck_old = [f.resize((300, 240), Image.NEAREST) for f in peck_old]
    scaled_peck_new = [f.resize((300, 240), Image.NEAREST) for f in peck_new]

    scaled_peck_new[0].save(
        OUT_DIR / "peck_inertia_3x.gif",
        save_all=True,
        append_images=scaled_peck_new[1:],
        duration=[200, 160, 180, 240],
        loop=0,
        disposal=2
    )

    scaled_peck_old[0].save(
        OUT_DIR / "peck_old_3x.gif",
        save_all=True,
        append_images=scaled_peck_old[1:],
        duration=[200, 160, 180, 240],
        loop=0,
        disposal=2
    )

    # Peck spritesheet (2x)
    peck_sheet = Image.new("RGBA", (400, 170), (245, 247, 250, 255))
    d_ps = ImageDraw.Draw(peck_sheet)
    for c_idx in range(4):
        peck_sheet.paste(peck_old[c_idx], (c_idx * 100, 0), peck_old[c_idx])
        peck_sheet.paste(peck_new[c_idx], (c_idx * 100, 90), peck_new[c_idx])
        if c_idx > 0:
            d_ps.line([(c_idx * 100, 0), (c_idx * 100, 80)], fill="#d5dae2")
            d_ps.line([(c_idx * 100, 90), (c_idx * 100, 170)], fill="#d5dae2")
    d_ps.line([(0, 85), (400, 85)], fill="#b0b8c4", width=2)
    peck_sheet_2x = peck_sheet.resize((800, 340), Image.NEAREST)
    peck_sheet_2x.save(OUT_DIR / "peck_comparison_spritesheet_2x.png")

    # B. BONK SUITE
    # 1. Old bonk frames from test_bonk (or assets if available)
    bonk_old = []
    for i in range(5):
        p = Path(f"D:/pets/test_bonk/bonk_{i}.png")
        if p.exists():
            bonk_old.append(Image.open(p))
        else:
            # fallback: standard render without inertia
            from test_bonk_generator import render_bonk_frame
            bonk_old.append(render_bonk_frame(crest="alert"))

    # 2. New inertia bonk frames
    bonk_new = [render_bonk_screen_inertia(i) for i in range(5)]

    for i, f in enumerate(bonk_new):
        f.save(OUT_DIR / f"bonk_inertia_{i}.png")

    # Bonk GIF 3x
    bonk_durations = [280, 100, 160, 220, 180]
    scaled_bonk_old = [f.resize((300, 240), Image.NEAREST) for f in bonk_old]
    scaled_bonk_new = [f.resize((300, 240), Image.NEAREST) for f in bonk_new]

    scaled_bonk_new[0].save(
        OUT_DIR / "bonk_inertia_3x.gif",
        save_all=True,
        append_images=scaled_bonk_new[1:],
        duration=bonk_durations,
        loop=0,
        disposal=2
    )

    scaled_bonk_old[0].save(
        OUT_DIR / "bonk_old_3x.gif",
        save_all=True,
        append_images=scaled_bonk_old[1:],
        duration=bonk_durations,
        loop=0,
        disposal=2
    )

    # Bonk spritesheet (2x)
    bonk_sheet = Image.new("RGBA", (500, 170), (245, 247, 250, 255))
    d_bs = ImageDraw.Draw(bonk_sheet)
    for c_idx in range(5):
        bonk_sheet.paste(bonk_old[c_idx], (c_idx * 100, 0), bonk_old[c_idx])
        bonk_sheet.paste(bonk_new[c_idx], (c_idx * 100, 90), bonk_new[c_idx])
        if c_idx > 0:
            d_bs.line([(c_idx * 100, 0), (c_idx * 100, 80)], fill="#d5dae2")
            d_bs.line([(c_idx * 100, 90), (c_idx * 100, 170)], fill="#d5dae2")
    d_bs.line([(0, 85), (500, 85)], fill="#b0b8c4", width=2)
    bonk_sheet_2x = bonk_sheet.resize((1000, 340), Image.NEAREST)
    bonk_sheet_2x.save(OUT_DIR / "bonk_comparison_spritesheet_2x.png")

    # Copy to Artifact directory
    if ARTIFACT_DIR.exists():
        for fname in [
            "peck_inertia_3x.gif", "peck_old_3x.gif", "peck_comparison_spritesheet_2x.png",
            "bonk_inertia_3x.gif", "bonk_old_3x.gif", "bonk_comparison_spritesheet_2x.png"
        ]:
            src = OUT_DIR / fname
            if src.exists():
                shutil.copy2(src, ARTIFACT_DIR / fname)
        print("Copied all comparison assets to artifact directory.")

    print("Peck & Bonk crest inertia test suite generated successfully!")

if __name__ == "__main__":
    build_comparison_suite()
