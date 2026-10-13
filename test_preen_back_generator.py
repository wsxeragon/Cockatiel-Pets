r"""Cockatiel Preen Back Animation Generator (理毛埋背动作优化测试脚本):
Generates a realistic and adorable cockatiel preening animation where the head is genuinely
turned around and buried into the back/wing feathers.

Output directory: D:\pets\test_preen
Artifact directory: C:\Users\26893\.gemini\antigravity\brain\5df30705-c1cf-4a9e-883a-019811f74aae
"""
import math
import shutil
from pathlib import Path
from PIL import Image, ImageDraw

OUT_DIR = Path(r"D:\pets\test_preen")
OUT_DIR.mkdir(parents=True, exist_ok=True)

ARTIFACT_DIR = Path(r"C:\Users\26893\.gemini\antigravity\brain\5df30705-c1cf-4a9e-883a-019811f74aae")

C = dict(
    ink="#353438", grey="#69696d", light="#88878a", dark="#505055",
    white="#f5f1df", yellow="#fff081", shade="#eacb67", cheek="#e99342",
    beak="#a99b9a", foot="#bba5a5", blush="#f2826a"
)

def render_preen_back_frame(phase=0, eye_mode=None):
    """
    Render 100x80 pixel sprite for preening back feathers.
    phase:
      0: Turn & Enter (Head turned back, beak touching wing/back)
      1: Deep Nibble (Head deeper into feathers, wing ruffles slightly)
      2: Pull & Preen (Beak nibbles feather strand, open eye or soft blink, tiny fluffy down particle)
      3: Relax & Settle (Beak loosens, feathers settle back)
    """
    im = Image.new("RGBA", (100, 80))
    d = ImageDraw.Draw(im)
    c = C

    default_eye = "open"
    # --- Phase Parameters ---
    if phase == 0:
        # 帧 0: 转头探背，嘴尖刚刚触碰到背部羽毛，大圆眼专注注视
        head_x, head_y = 48, 38
        beak_reach = 0        # 深入程度
        wing_ruffle = 0       # 翅膀蓬起
        default_eye = "open"  # 睁开大圆眼
        crest_wag = 0         # 冠羽自然顺贴
        feather_particle = False
        body_breath = 0

    elif phase == 1:
        # 帧 1: 嘴壳深埋进背羽，头部微下探啄弄，专注注视啄羽处
        head_x, head_y = 50, 40
        beak_reach = 2
        wing_ruffle = 2       # 翅羽被嘴壳挑起膨起
        default_eye = "open"  # 睁开大圆眼
        crest_wag = 1         # 冠羽随低头微颤
        feather_particle = False
        body_breath = 1

    elif phase == 2:
        # 帧 2: 轻轻顺理羽丝，嘴壳微抬，空中浮现一抹极细微白绒毛
        head_x, head_y = 49, 39
        beak_reach = 1
        wing_ruffle = 3       # 翅羽处于挑理最高点
        default_eye = "open"  # 睁开大圆眼 (亦可轻柔微眨)
        crest_wag = 2
        feather_particle = True # 产生一颗小羽屑/绒毛
        body_breath = 1

    else:
        # 帧 3: 啄梳完成一个微循环，嘴壳稍微松开回弹，羽毛落回
        head_x, head_y = 47, 37
        beak_reach = 0
        wing_ruffle = 1
        default_eye = "open"  # 睁开大圆眼
        crest_wag = 0
        feather_particle = False
        body_breath = 0

    effective_eye = eye_mode if eye_mode is not None else default_eye

    # 1. TAIL (尾羽 - 依然向右后方自然延伸)
    d.polygon([(61, 52), (96, 54), (98, 58), (68, 60), (60, 56)], fill=c["ink"])
    d.polygon([(63, 53), (95, 55), (92, 57), (67, 57)], fill=c["dark"])
    d.line([(71, 55), (92, 56)], fill=c["light"])

    # 2. FEET (双脚 - 依然稳稳踩在 y=72 地面)
    feet = [(45, 41), (57, 54)]
    for fx, toe in feet:
        d.line([(fx, 65), (toe, 72)], fill=c["ink"], width=3)
        d.line([(fx, 65), (toe, 72)], fill=c["foot"], width=2)
        d.line([(toe - 3, 72), (toe + 2, 72)], fill=c["foot"], width=2)

    # 3. BODY (身体 - 圆润饱满身躯，胸脯在左侧)
    body_x0, body_y0 = 34, 34 - body_breath
    body_x1, body_y1 = 72, 70
    d.ellipse((body_x0, body_y0, body_x1, body_y1), fill=c["ink"])
    d.ellipse((body_x0 + 2, body_y0 + 2, body_x1 - 2, body_y1 - 2), fill=c["grey"])
    # 腹部浅灰色软糖高光
    d.ellipse((body_x0 + 4, body_y0 + 10, body_x0 + 22, body_y1 - 4), fill=c["light"])

    # 4. NECK (弯向背后的柔软脖子 - 顺滑连接左侧胸脯与背部头部)
    neck_pts = [
        (body_x0 + 6, body_y0 + 12),
        (head_x - 10, head_y + 4),
        (head_x - 6, head_y + 11),
        (body_x0 + 18, body_y0 + 16),
        (body_x0 + 12, body_y0 + 22)
    ]
    d.polygon(neck_pts, fill=c["ink"])
    d.polygon([(x + 1, y) for x, y in neck_pts[:-1]], fill=c["grey"])

    # 5. BASE WING (下层翅膀轮廓 - 随理毛啄弄微隆与顺毛)
    base_wing = [
        (47, 40 - wing_ruffle),
        (65, 42 - wing_ruffle),
        (76, 53 + wing_ruffle // 2),
        (63, 62),
        (47, 55)
    ]
    d.polygon(base_wing, fill=c["ink"])
    d.polygon([(x + 1, y + 1) for x, y in base_wing[:-1]], fill=c["dark"])

    # 纯白大翅斑 (覆羽随嘴巴梳理被轻轻带起)
    white_patch = [
        (49, 47 - wing_ruffle),
        (55, 48 - wing_ruffle),
        (63, 54),
        (73, 54),
        (66, 61),
        (56, 59)
    ]
    d.polygon(white_patch, fill=c["white"])

    # 6. HEAD (向后转过 180° 的圆滚滚大头)
    hx, hy = head_x, head_y
    d.ellipse((hx - 13, hy - 13, hx + 13, hy + 13), fill=c["ink"])
    d.ellipse((hx - 12, hy - 12, hx + 12, hy + 12), fill=c["yellow"])
    # 颈后枕部浅白过渡羽
    d.polygon([
        (hx - 12, hy - 6),
        (hx - 8, hy - 11),
        (hx - 2, hy - 3),
        (hx - 6, hy + 8),
        (hx - 12, hy + 4)
    ], fill=c["white"])

    # 7. CHEEK (招牌大腮红 - 位于面部右侧偏下)
    d.ellipse((hx + 1, hy + 1, hx + 10, hy + 10), fill=c["cheek"])

    # 8. EYE (睁开大圆眼 - 专注低头注视背后羽毛，带灵动高光)
    if effective_eye == "blink":
        # 偶尔舒适微闭细线
        d.line([(hx + 3, hy - 3), (hx + 6, hy - 1), (hx + 8, hy - 3)], fill=c["ink"], width=2)
    else:
        # 睁开大圆眼 (5x6 萌系圆润大眼，与 idle 保持一致视觉比例与水灵眼神)
        d.ellipse((hx + 3, hy - 6, hx + 7, hy - 1), fill=c["ink"])
        # 水润纯白高光点
        d.point((hx + 4, hy - 5), fill=c["white"])

    # 9. CREST (羽冠 - 优美向左上方回卷的弧形长羽)
    # 玄凤低头转颈时，羽冠根部在头顶右前方，向后掠向左上方并自然微扬
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
    # 顺羽毛流光线
    d.line([(hx - 1, hy - 11), (hx - 9 - crest_wag, hy - 18 - crest_wag)], fill=c["yellow"], width=1)

    # 10. BEAK (小嘴喙 - 真正向右下方埋进背后翅羽中！)
    bx_base = hx + 6
    by_base = hy + 4
    bx_tip = hx + 12 + beak_reach
    by_tip = hy + 9 + beak_reach

    beak_upper = [
        (bx_base, by_base - 2),
        (bx_base + 3, by_base - 1),
        (bx_tip + 2, by_tip),
        (bx_tip, by_tip + 3),
        (bx_base + 1, by_base + 4),
        (bx_base - 1, by_base + 1)
    ]
    beak_inner = [
        (bx_base + 1, by_base - 1),
        (bx_base + 3, by_base),
        (bx_tip + 1, by_tip),
        (bx_tip, by_tip + 2),
        (bx_base + 1, by_base + 3)
    ]
    d.polygon(beak_upper, fill=c["ink"])
    d.polygon(beak_inner, fill=c["beak"])
    d.point((bx_base + 2, by_base), fill="#c8b8b5")

    # 11. OVERLAPPING BACK FEATHER RUFFLES (肩羽与覆羽遮挡层 - 产生深埋进羽毛的真实体积)
    ruffle_cover = [
        (bx_tip - 2, by_tip - 3),
        (bx_tip + 3, by_tip - 1),
        (bx_tip + 6, by_tip + 4),
        (bx_tip + 2, by_tip + 6),
        (bx_tip - 3, by_tip + 1)
    ]
    d.polygon(ruffle_cover, fill=c["ink"])
    d.polygon([(x, y) for x, y in ruffle_cover[:-1]], fill=c["dark"])
    d.line([(bx_tip - 1, by_tip + 1), (bx_tip + 3, by_tip + 3)], fill=c["light"], width=1)
    d.point((bx_tip + 1, by_tip - 2), fill=c["white"])

    # 12. FEATHER DANDER / FLUFFY DOWN (梳理挑起的极细小白绒毛微粒)
    if feather_particle:
        # 在嘴壳上方轻轻飘起一团轻盈的小绒毛（2~3 像素软白微粒）
        d.point((bx_tip + 3, by_tip - 8), fill="#ffffff")
        d.point((bx_tip + 4, by_tip - 9), fill="#ffffff")
        d.point((bx_tip + 2, by_tip - 9), fill="#eae6da")
        d.point((bx_tip + 5, by_tip - 8), fill="#e0dcce")

    return im

def build_preen_suite():
    # 1. 旧版两帧对比 (面向左侧晃头)
    from PIL import Image
    old_f0 = Image.open(r"D:\pets\assets\sprites\preen_0.png")
    old_f1 = Image.open(r"D:\pets\assets\sprites\preen_1.png")
    old_loop = [old_f0, old_f1, old_f0, old_f1]

    # 2. 新版 4 帧转头埋背理毛循环
    new_f0 = render_preen_back_frame(phase=0) # 转头探背
    new_f1 = render_preen_back_frame(phase=1) # 深埋啄弄
    new_f2 = render_preen_back_frame(phase=2) # 梳理顺羽 + 萌趣小绒毛
    new_f3 = render_preen_back_frame(phase=3) # 惬意微喘平复
    new_loop = [new_f0, new_f1, new_f2, new_f3]

    for i, f in enumerate(new_loop):
        f.save(OUT_DIR / f"preen_back_{i}.png")

    # 3. 3x 放大动图
    scaled_old = [f.resize((300, 240), Image.NEAREST) for f in old_loop]
    scaled_new = [f.resize((300, 240), Image.NEAREST) for f in new_loop]

    scaled_old[0].save(
        OUT_DIR / "preen_old_facing_left_3x.gif",
        save_all=True,
        append_images=scaled_old[1:],
        duration=[280, 280, 280, 280],
        loop=0,
        disposal=2
    )

    # 方案 A: 舒缓温存深埋理毛 (280ms 慢节奏享受)
    scaled_new[0].save(
        OUT_DIR / "preen_new_buried_back_3x.gif",
        save_all=True,
        append_images=scaled_new[1:],
        duration=[320, 260, 280, 340],
        loop=0,
        disposal=2
    )

    # 方案 B: 灵动轻快啄洗顺羽 (180ms 快节奏灵动)
    scaled_new[0].save(
        OUT_DIR / "preen_new_brisk_nibble_3x.gif",
        save_all=True,
        append_images=scaled_new[1:],
        duration=[200, 160, 180, 220],
        loop=0,
        disposal=2
    )

    # 方案 C: 第2帧顺羽微眨眼对比版 (睁眼理羽 + 轻柔微眨)
    f_blink = [render_preen_back_frame(0), render_preen_back_frame(1), render_preen_back_frame(2, eye_mode="blink"), render_preen_back_frame(3)]
    scaled_blink = [f.resize((300, 240), Image.NEAREST) for f in f_blink]
    scaled_blink[0].save(
        OUT_DIR / "preen_open_blink_3x.gif",
        save_all=True,
        append_images=scaled_blink[1:],
        duration=[320, 260, 280, 340],
        loop=0,
        disposal=2
    )

    # 4. 2x 逐帧分解对比图谱 (旧版 vs 新版)
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
    comp_2x.save(OUT_DIR / "preen_comparison_spritesheet_2x.png")

    # 5. 复制到 Artifact 目录供审查
    if ARTIFACT_DIR.exists():
        comp_2x.save(ARTIFACT_DIR / "preen_comparison_spritesheet_2x.png")
        scaled_old[0].save(
            ARTIFACT_DIR / "preen_old_facing_left_3x.gif",
            save_all=True,
            append_images=scaled_old[1:],
            duration=[280, 280, 280, 280],
            loop=0,
            disposal=2
        )
        scaled_new[0].save(
            ARTIFACT_DIR / "preen_new_buried_back_3x.gif",
            save_all=True,
            append_images=scaled_new[1:],
            duration=[320, 260, 280, 340],
            loop=0,
            disposal=2
        )
        scaled_new[0].save(
            ARTIFACT_DIR / "preen_new_brisk_nibble_3x.gif",
            save_all=True,
            append_images=scaled_new[1:],
            duration=[200, 160, 180, 220],
            loop=0,
            disposal=2
        )
        scaled_blink[0].save(
            ARTIFACT_DIR / "preen_open_blink_3x.gif",
            save_all=True,
            append_images=scaled_blink[1:],
            duration=[320, 260, 280, 340],
            loop=0,
            disposal=2
        )
        print("Copied preen demo assets to artifact directory.")

    print("Preen animation test suite generated successfully!")

if __name__ == "__main__":
    build_preen_suite()
