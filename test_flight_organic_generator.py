"""Flight Animation Optimization Suite (飞行翅膀形态与帧数生动性优化测试脚本):
Generates:
1. Old 3-frame flight animation (fly_0 -> fly_1 -> fly_2 -> fly_1)
2. New 4-frame organic flight animation (Apex -> Power Downstroke -> Bottom Lift -> Recovery Fold)
   - Streamlined aerodynamic crest (顺风流线型羽冠)
   - Organic curved wings with prominent white patches (饱满柔韧受风弧面与白翅斑)
   - Wing-body lift synchronization (下拍升力浮沉联动 +2px)
3. Side-by-side spritesheet comparison (2x)
4. Screen flight simulation GIF (2x) across a desktop sky trajectory
"""
import math
from pathlib import Path
from PIL import Image, ImageDraw
import sys

sys.path.append(r"D:\pets\2d-new")
from generate_sprites_q_optimized import C

OUT_DIR = Path(r"D:\pets\test_flight")
OUT_DIR.mkdir(parents=True, exist_ok=True)
ARTIFACT_DIR = Path(r"C:\Users\26893\.gemini\antigravity\brain\5df30705-c1cf-4a9e-883a-019811f74aae")

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
    # Wing phases:
    # 0: High up apex (pointed up-back)
    # 1: Mid power stroke (reaching forward-down)
    # 2: Full bottom downstroke (extended low)
    # 3: Recovery fold (wrist bent upward, tips trailing)
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
        # Phase 0: 【高扬蓄力】 双翼高高扬起，翼尖微收上挑
        near_outer = [
            (48, 43), (55, 23), (62, 5), (68, 7), (67, 30), (56, 50)
        ]
        near_white = [
            (51, 41), (58, 21), (63, 11), (63, 27), (55, 46)
        ]
    elif wing_phase == 1:
        # Phase 1: 【破风下扑】 猛烈下拍！饱满迎风微弧，纯白大翼斑完全展露
        near_outer = [
            (47, 43), (63, 33), (85, 28), (92, 33), (86, 46), (68, 53), (54, 52)
        ]
        near_white = [
            (50, 42), (66, 35), (84, 32), (80, 43), (64, 48), (53, 48)
        ]
    elif wing_phase == 2:
        # Phase 2: 【下压底峰】 压至最低点，翼尖顺风向后甩，升力推力极值
        near_outer = [
            (48, 44), (58, 52), (74, 66), (78, 70), (72, 73), (63, 64), (54, 56)
        ]
        near_white = [
            (51, 46), (60, 53), (73, 67), (68, 68), (55, 54)
        ]
    else:
        # Phase 3: 【曲翼折叠·顺风回抬】 肘部先提，翼尖受阻微折拖曳，柔韧丝滑回位！
        near_outer = [
            (48, 43), (56, 30), (66, 26), (76, 37), (73, 44), (60, 48), (52, 50)
        ]
        near_white = [
            (51, 41), (58, 31), (67, 28), (70, 36), (61, 44), (54, 46)
        ]

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

    # 7. CREST (羽冠 - 顺风流线型后掠，告别僵硬直立)
    if crest_style == "streamline":
        # 顺风流线型贴脑飘展 (速度风阻微颤)
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
        # 旧版直立天线
        d.polygon([(hx - 5, hy - 10), (hx - 1, hy - 28), (hx + 2, hy - 30), (hx + 3, hy - 11)], fill=c["shade"])
        d.polygon([(hx, hy - 11), (hx + 7, hy - 25), (hx + 9, hy - 24), (hx + 4, hy - 9)], fill=c["yellow"])

    # 8. EYES (飞行动感大眼神)
    d.ellipse((hx - 9, hy - 7, hx - 3, hy + 1), fill=c["ink"])
    d.point((hx - 7, hy - 5), fill=c["white"])

    # 9. BEAK (小巧嘴喙)
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

def build_flight_suite():
    # 1. 渲染旧版 3 帧
    from generate_sprites_q_optimized import bird_q_optimized
    old_f0 = bird_q_optimized(wing="fly_up", lift=-5, crest="alert", tuck_feet=True)
    old_f1 = bird_q_optimized(wing="fly_mid", lift=-5, crest="alert", tuck_feet=True)
    old_f2 = bird_q_optimized(wing="fly_down", lift=-7, crest="alert", tuck_feet=True)
    old_loop = [old_f0, old_f1, old_f2, old_f1]  # 经典乒乓 3 帧循环

    # 2. 渲染新版 4 帧有机动力学飞行
    # Frame 0: 【高扬蓄力】 身体微沉 lift=-4, 头部微探
    new_f0 = render_bird_flight_custom(wing_phase=0, lift=-4, head=(-2, -1), tail_angle=0)
    # Frame 1: 【破风下扑】 强力推风 lift=-6, 大白翅斑完全展露, 尾羽微展开
    new_f1 = render_bird_flight_custom(wing_phase=1, lift=-6, head=(-3, 0), tail_angle=2)
    # Frame 2: 【下压底峰】 升力极值！身体受升力上浮 lift=-8, 尾翼平展
    new_f2 = render_bird_flight_custom(wing_phase=2, lift=-8, head=(-3, 0), tail_angle=1)
    # Frame 3: 【曲翼折叠】 肘先提羽后折 lift=-5, 柔韧丝滑回接
    new_f3 = render_bird_flight_custom(wing_phase=3, lift=-5, head=(-2, -1), tail_angle=0)
    new_loop = [new_f0, new_f1, new_f2, new_f3]

    # 保存单帧到测试目录
    for i, f in enumerate(new_loop):
        f.save(OUT_DIR / f"flight_organic_{i}.png")

    # 3. 生成 3倍放大对比 GIF (120ms/帧)
    durations = [120, 120, 120, 120]
    scaled_old = [f.resize((300, 240), Image.NEAREST) for f in old_loop]
    scaled_new = [f.resize((300, 240), Image.NEAREST) for f in new_loop]

    scaled_old[0].save(
        OUT_DIR / "flight_old_loop_3x.gif",
        save_all=True,
        append_images=scaled_old[1:],
        duration=durations,
        loop=0,
        disposal=2
    )
    scaled_new[0].save(
        OUT_DIR / "flight_new_organic_3x.gif",
        save_all=True,
        append_images=scaled_new[1:],
        duration=durations,
        loop=0,
        disposal=2
    )

    # 4. 生成 2x 帧分解对比图谱 Spritesheet
    comp_w = 100 * 4
    comp_h = 80 * 2 + 10
    comp_img = Image.new("RGBA", (comp_w, comp_h), (245, 247, 250, 255))
    d_comp = ImageDraw.Draw(comp_img)

    # 上排：旧版 3 帧 + 回放第 1 帧
    for col in range(4):
        comp_img.paste(old_loop[col], (col * 100, 0), old_loop[col])
        if col > 0:
            d_comp.line([(col * 100, 0), (col * 100, 80)], fill="#d5dae2")

    # 下排：新版 4 帧有机动力学
    for col in range(4):
        comp_img.paste(new_loop[col], (col * 100, 90), new_loop[col])
        if col > 0:
            d_comp.line([(col * 100, 90), (col * 100, 170)], fill="#d5dae2")

    d_comp.line([(0, 85), (comp_w, 85)], fill="#b0b8c4", width=2)

    comp_2x = comp_img.resize((comp_w * 2, comp_h * 2), Image.NEAREST)
    comp_2x.save(OUT_DIR / "flight_comparison_spritesheet_2x.png")

    # 5. 生成真实横穿屏幕飞翔轨迹模拟动图 (2x)
    sim_w, sim_h = 240, 120
    bg = Image.new("RGBA", (sim_w, sim_h), (242, 245, 249, 255))
    d_bg = ImageDraw.Draw(bg)
    d_bg.line([(0, 105), (sim_w, 105)], fill="#d0d6e0", width=1)

    sim_frames = []
    total_steps = 16
    for step in range(total_steps):
        f = bg.copy()
        # 抛物线横移轨迹：从右侧 x=180 飞向左侧 x=10
        t = step / (total_steps - 1)
        bx = 180 - t * 170
        # 抛物线上凸弧度
        arc_y = math.sin(t * math.pi) * 35
        by = 25 - arc_y

        frame_idx = step % 4
        bird_frame = new_loop[frame_idx]
        f.paste(bird_frame, (round(bx), round(by)), bird_frame)
        sim_frames.append(f)

    sim_2x = [sf.resize((sim_w * 2, sim_h * 2), Image.NEAREST) for sf in sim_frames]
    sim_2x[0].save(
        OUT_DIR / "flight_screen_simulation_2x.gif",
        save_all=True,
        append_images=sim_2x[1:],
        duration=95,
        loop=0,
        disposal=2
    )

    # 复制产物到 Artifact 目录
    if ARTIFACT_DIR.exists():
        comp_2x.save(ARTIFACT_DIR / "flight_comparison_spritesheet_2x.png")
        scaled_old[0].save(
            ARTIFACT_DIR / "flight_old_loop_3x.gif",
            save_all=True,
            append_images=scaled_old[1:],
            duration=durations,
            loop=0,
            disposal=2
        )
        scaled_new[0].save(
            ARTIFACT_DIR / "flight_new_organic_3x.gif",
            save_all=True,
            append_images=scaled_new[1:],
            duration=durations,
            loop=0,
            disposal=2
        )
        sim_2x[0].save(
            ARTIFACT_DIR / "flight_screen_simulation_2x.gif",
            save_all=True,
            append_images=sim_2x[1:],
            duration=95,
            loop=0,
            disposal=2
        )
        print("Copied all flight demo assets to artifact directory.")

    print("Flight animation test suite generated successfully!")

if __name__ == "__main__":
    build_flight_suite()
