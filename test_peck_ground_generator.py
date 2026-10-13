"""Peck Ground Animation Optimization Suite (啄地面动作深度优化测试脚本):
Generates true ground-pecking animation where the beak actually touches the desk/floor (y=71~72),
with forward body tilt, raised tail, downward angled beak, and impact tap:
1. Old 2-frame airborne peck animation (旧版半空晃头)
2. New 4-frame true ground peck animation (新版真实触地啄桌面)
   - Frame 0: 【瞄准准备】 低头前俯，双眼注视地面
   - Frame 1: 【触地啄击】 嘴尖精准触地 (y=71)，尾巴高高翘起，地面轻微触碰微波
   - Frame 2: 【触地回弹】 头部微弹，嘴壳张合轻嚼，尾翼微颤
   - Frame 3: 【抬头嚼食】 顺势抬头，平稳归位
3. Side-by-side comparison spritesheet (2x)
4. Desktop ground surface simulation GIF (2x) showing clear desk baseline
"""
import math
from pathlib import Path
from PIL import Image, ImageDraw
import sys

sys.path.append(r"D:\pets\2d-new")
from generate_sprites_q_optimized import bird_q_optimized, C

OUT_DIR = Path(r"D:\pets\test_peck")
OUT_DIR.mkdir(parents=True, exist_ok=True)
ARTIFACT_DIR = Path(r"C:\Users\26893\.gemini\antigravity\brain\5df30705-c1cf-4a9e-883a-019811f74aae")

def render_true_ground_peck_frame(phase=0):
    """Render a dedicated 100x80 frame where the bird realistically pecks the ground.
    Ground baseline is at y = 72.
    phase:
      0: Aim (Looking down, body starts tilting forward)
      1: Strike (Beak touches ground y=71! Tail sticks up high!)
      2: Rebound (Head pops up slightly, beak opens/closes chewing)
      3: Recover (Head lifts up, tail lowers, chewing food)
    """
    im = Image.new("RGBA", (100, 80))
    d = ImageDraw.Draw(im)
    c = C

    # Feet baseline: ground is at y = 72
    # Standing feet at x=46, x=58

    if phase == 0:
        # Phase 0: 瞄准准备 (Look down)
        body_tilt_y = 2
        body_x0, body_y0, body_x1, body_y1 = 33, 34, 71, 70
        tail_lift = -4       # 尾巴微翘
        hx, hy = 29, 41      # 头低向地面
        beak_angle = 35      # 鸟喙斜向地面
        eye_look = "down"
        crest_lean = 2
        feet_press = 0
        tap_spark = False

    elif phase == 1:
        # Phase 1: 触地啄击 (Strike - Beak hits ground y=71!)
        body_tilt_y = 4
        body_x0, body_y0, body_x1, body_y1 = 31, 36, 69, 71
        tail_lift = -12      # 尾巴高高翘起 (超萌翘臀杠杆感)
        hx, hy = 23, 53      # 头部深度下压
        beak_angle = 65      # 鸟喙大角度向下狠啄地面
        eye_look = "down"
        crest_lean = 4       # 羽冠惯性前甩
        feet_press = 1       # 脚爪吃力抓地
        tap_spark = True     # 触地清脆微粒

    elif phase == 2:
        # Phase 2: 触地回弹 (Rebound & Nibble)
        body_tilt_y = 3
        body_x0, body_y0, body_x1, body_y1 = 32, 35, 70, 70
        tail_lift = -8       # 尾巴保持微翘
        hx, hy = 26, 46      # 受地面反作用力微弹起
        beak_angle = 45      # 鸟喙微张轻嚼
        eye_look = "happy"
        crest_lean = 1
        feet_press = 0
        tap_spark = False

    else:
        # Phase 3: 抬头嚼食 (Lift & Recover)
        body_tilt_y = 0
        body_x0, body_y0, body_x1, body_y1 = 34, 33, 72, 69
        tail_lift = -2       # 尾巴平稳回落
        hx, hy = 32, 35      # 顺势抬头
        beak_angle = 15      # 接近平时水平
        eye_look = "happy"   # 享受吧唧嘴
        crest_lean = 0
        feet_press = 0
        tap_spark = False

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

    # 7. CREST (羽冠 - 随低头重力与惯性前倾微颤)
    crest_poly_outer = [
        (hx - 5, hy - 10),
        (hx - 3 - crest_lean, hy - 27),
        (hx - crest_lean, hy - 29),
        (hx + 3, hy - 11)
    ]
    crest_poly_inner = [
        (hx - 1, hy - 11),
        (hx + 5 - crest_lean, hy - 24),
        (hx + 7 - crest_lean, hy - 23),
        (hx + 4, hy - 9)
    ]
    d.polygon(crest_poly_outer, fill=c["shade"])
    d.polygon(crest_poly_inner, fill=c["yellow"])

    # 8. EYES (眼神视线聚焦于地面小石子)
    if eye_look == "down":
        # 视线明显向下看 (瞳孔在下方)
        d.ellipse((hx - 8, hy - 5, hx - 4, hy), fill=c["ink"])
        d.point((hx - 6, hy - 2), fill=c["white"])
    else:
        # 眯眯笑眼 (享受吃小米)
        d.line([(hx - 9, hy - 1), (hx - 6, hy - 4), (hx - 3, hy - 1)], fill=c["ink"], width=2)
        d.point((hx + 2, hy + 6), fill=c["blush"])

    # 9. BEAK (小鹦鹉标志性弯钩喙 - 依据啄地俯仰角真实旋转并触地)
    import math

    def rotate_point(px, py, ox, oy, angle_deg):
        # 屏幕坐标系 (y向下): 逆时针为负，使嘴尖从指向前左 (-x) 旋转指向下方 (+y)
        rad = math.radians(angle_deg)
        cos_a = math.cos(rad)
        sin_a = math.sin(rad)
        dx = px - ox
        dy = py - oy
        rx = dx * cos_a - dy * sin_a
        ry = dx * sin_a + dy * cos_a
        return (round(ox + rx), round(oy + ry))

    if phase == 1:
        # Phase 1: 真实触地！头部深潜 (hy=56)，弯钩上喙尖精准落在 (14, 71)
        # 上喙轮廓 (优美的玄凤下弯圆润鹦鹉喙)
        upper_beak_pts = [
            (hx - 10, hy + 2),   # 喙根部上沿
            (hx - 13, hy + 3),
            (hx - 15, hy + 6),
            (hx - 14, hy + 10),  # 弯钩外弧
            (14, 71),            # 嘴尖触地！！(精确 y=71)
            (17, 68),            # 嘴尖内折
            (hx - 7, hy + 9),
            (hx - 8, hy + 4)
        ]
        upper_beak_inner = [
            (hx - 10, hy + 3),
            (hx - 12, hy + 4),
            (hx - 14, hy + 7),
            (hx - 13, hy + 10),
            (14, 70),
            (16, 68),
            (hx - 8, hy + 8),
            (hx - 9, hy + 5)
        ]
        # 下喙 (微收于上喙内侧)
        lower_beak = [
            (hx - 8, hy + 8),
            (16, 67),
            (18, 65),
            (hx - 6, hy + 7)
        ]
        d.polygon(lower_beak, fill=c["ink"])
        d.polygon([(x, y) for x, y in lower_beak], fill=c["beak"])
        d.polygon(upper_beak_pts, fill=c["ink"])
        d.polygon(upper_beak_inner, fill=c["beak"])
        # 喙尖高光与鼻瘤质感
        d.point((15, 69), fill="#c8b8b5")
        d.point((hx - 11, hy + 4), fill="#c8b8b5")

    elif phase == 0:
        # Phase 0: 低头瞄准 (hy=43)，喙朝斜下方 35°
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
        # Phase 2: 触地回弹轻嚼 (hy=47)，小嘴微张、小谷粒在口
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
        
        # 下喙张开 2px 嚼食
        orig_lower = [(hx - 11, hy + 6), (hx - 14, hy + 9), (hx - 12, hy + 11), (hx - 9, hy + 8)]
        orig_lower_in = [(hx - 11, hy + 7), (hx - 13, hy + 9), (hx - 11, hy + 10)]
        lower_beak = [rotate_point(x, y, ox, oy, rot_ang) for x, y in orig_lower]
        lower_beak_in = [rotate_point(x, y, ox, oy, rot_ang) for x, y in orig_lower_in]
        
        d.polygon(lower_beak, fill=c["ink"])
        d.polygon(lower_beak_in, fill=c["beak"])
        d.polygon(upper_beak_pts, fill=c["ink"])
        d.polygon(upper_beak_inner, fill=c["beak"])
        d.point(rotate_point(hx - 14, hy + 1, ox, oy, rot_ang), fill="#c8b8b5")
        # 嘴边咬住的一小粒金黄小米谷粒 (萌点)
        seed_pos = rotate_point(hx - 13, hy + 8, ox, oy, rot_ang)
        d.point(seed_pos, fill="#ffcc00")
        d.point((seed_pos[0] + 1, seed_pos[1]), fill="#ffa000")

    else:
        # Phase 3: 顺势抬头嚼食 (hy=35)，正常回正
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
        # 吧唧嘴小碎屑微粒
        d.point((hx - 15, hy + 6), fill="#ffcc00")

    # 10. GROUND IMPACT TAP PARTICLES (触地瞬间清脆微星斑)
    if tap_spark:
        # 嘴壳尖精准敲击在地面 (14, 71)，在地面反弹 2~3 颗清脆小星芒
        d.point((11, 70), fill="#ffd100")
        d.point((10, 69), fill="#ffffff")
        d.point((17, 71), fill="#ffd100")
        d.point((18, 70), fill="#ff9800")
        d.point((14, 69), fill="#fff3a8")

    return im

def build_peck_suite():
    # 1. 旧版两帧循环 (peck_0, peck_1)
    old_f0 = bird_q_optimized(head=(-3, 4))
    old_f1 = bird_q_optimized(head=(-6, 12), tail_wag=2)
    old_loop = [old_f0, old_f1, old_f0, old_f1]

    # 2. 新版 4 帧真实触地啄桌面循环
    new_f0 = render_true_ground_peck_frame(phase=0) # 瞄准准备
    new_f1 = render_true_ground_peck_frame(phase=1) # 真实触地啄击 (y=71)
    new_f2 = render_true_ground_peck_frame(phase=2) # 触地回弹轻嚼
    new_f3 = render_true_ground_peck_frame(phase=3) # 抬头嚼食复位
    new_loop = [new_f0, new_f1, new_f2, new_f3]

    for i, f in enumerate(new_loop):
        f.save(OUT_DIR / f"peck_ground_{i}.png")

    # 3. 3x 放大对比动图
    scaled_old = [f.resize((300, 240), Image.NEAREST) for f in old_loop]
    scaled_new_a = [f.resize((300, 240), Image.NEAREST) for f in new_loop]
    # 方案 B: 欢快双连啄 (瞄准 -> 触地1 -> 微弹 -> 触地2 -> 回弹微嚼 -> 抬头吧唧)
    new_loop_b = [new_f0, new_f1, new_f2, new_f1, new_f2, new_f3]
    durations_b = [180, 130, 130, 130, 160, 260]
    scaled_new_b = [f.resize((300, 240), Image.NEAREST) for f in new_loop_b]

    scaled_old[0].save(
        OUT_DIR / "peck_old_floating_3x.gif",
        save_all=True,
        append_images=scaled_old[1:],
        duration=[180, 180, 180, 180],
        loop=0,
        disposal=2
    )
    # 方案 A: 经典 4 帧深啄循环 (peck_0 -> peck_1 -> peck_2 -> peck_3)
    scaled_new_a[0].save(
        OUT_DIR / "peck_new_single_strike_3x.gif",
        save_all=True,
        append_images=scaled_new_a[1:],
        duration=[180, 150, 180, 260],
        loop=0,
        disposal=2
    )
    # 方案 B: 连环双啄魔性循环 (两下触地打击感)
    scaled_new_b[0].save(
        OUT_DIR / "peck_new_double_tap_3x.gif",
        save_all=True,
        append_images=scaled_new_b[1:],
        duration=durations_b,
        loop=0,
        disposal=2
    )

    # 4. 2x 帧分解对比图谱 (旧版 vs 新版)
    comp_w = 100 * 4
    comp_h = 80 * 2 + 10
    comp_img = Image.new("RGBA", (comp_w, comp_h), (245, 247, 250, 255))
    d_comp = ImageDraw.Draw(comp_img)

    for col in range(4):
        comp_img.paste(old_loop[col], (col * 100, 0), old_loop[col])
        comp_img.paste(new_loop[col], (col * 100, 90), new_loop[col])
        if col > 0:
            d_comp.line([(col * 100, 0), (col * 100, 80)], fill="#d5dae2")
            d_comp.line([(col * 100, 90), (col * 100, 170)], fill="#d5dae2")
    d_comp.line([(0, 85), (comp_w, 85)], fill="#b0b8c4", width=2)

    comp_2x = comp_img.resize((comp_w * 2, comp_h * 2), Image.NEAREST)
    comp_2x.save(OUT_DIR / "peck_comparison_spritesheet_2x.png")

    # 5. 带有真实木质桌面基准线的 2x 模拟啄击动图
    sim_w, sim_h = 160, 100
    desk_bg = Image.new("RGBA", (sim_w, sim_h), (248, 250, 252, 255))
    d_desk = ImageDraw.Draw(desk_bg)
    # 画出清爽的桌面基准线 (y=82，对应鸟脚 y=72)
    d_desk.line([(0, 82), (sim_w, 82)], fill="#c8d0dc", width=2)
    # 桌面上散落的小米谷粒点缀
    for mx, my in [(38, 80), (45, 81), (50, 79), (32, 81)]:
        d_desk.ellipse((mx, my, mx + 2, my + 2), fill="#ffd100", outline="#bfa000")

    sim_frames = []
    # 模拟啄地 2 个周期的连续觅食动作
    full_cycle = [new_f0, new_f1, new_f2, new_f1, new_f2, new_f3]
    cycle_durations = [180, 160, 180, 160, 200, 360]
    for frame in full_cycle:
        f = desk_bg.copy()
        # 鸟居中放置 (ox=30, oy=10)
        f.paste(frame, (30, 10), frame)
        sim_frames.append(f)

    sim_2x = [sf.resize((sim_w * 2, sim_h * 2), Image.NEAREST) for sf in sim_frames]
    sim_2x[0].save(
        OUT_DIR / "peck_desktop_feeding_simulation_2x.gif",
        save_all=True,
        append_images=sim_2x[1:],
        duration=cycle_durations,
        loop=0,
        disposal=2
    )

    # 复制产物到 Artifact 目录
    if ARTIFACT_DIR.exists():
        comp_2x.save(ARTIFACT_DIR / "peck_comparison_spritesheet_2x.png")
        scaled_old[0].save(
            ARTIFACT_DIR / "peck_old_floating_3x.gif",
            save_all=True,
            append_images=scaled_old[1:],
            duration=[180, 180, 180, 180],
            loop=0,
            disposal=2
        )
        scaled_new_a[0].save(
            ARTIFACT_DIR / "peck_new_single_strike_3x.gif",
            save_all=True,
            append_images=scaled_new_a[1:],
            duration=[180, 150, 180, 260],
            loop=0,
            disposal=2
        )
        scaled_new_b[0].save(
            ARTIFACT_DIR / "peck_new_double_tap_3x.gif",
            save_all=True,
            append_images=scaled_new_b[1:],
            duration=durations_b,
            loop=0,
            disposal=2
        )
        sim_2x[0].save(
            ARTIFACT_DIR / "peck_desktop_feeding_simulation_2x.gif",
            save_all=True,
            append_images=sim_2x[1:],
            duration=cycle_durations,
            loop=0,
            disposal=2
        )
        print("Copied peck demo assets to artifact directory.")

    print("Peck animation test suite generated successfully!")

if __name__ == "__main__":
    build_peck_suite()
