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
    beak="#a99b9a", foot="#bba5a5", blush="#f2826a",
    highlight="#fff9a6", deep_shade="#bd8b2a"
)

# -------------------------------------------------------------
# Procedural Recurved Overlapping Crest (反曲状 + 相互重叠三簇羽冠)
# 严格按照原型图重构：
# 1. 相互重叠：三簇绝非分离椭圆，而是一个紧密重合的整体羽冠，以暖琥珀羽褶阴影分割。
# 2. 反曲状：前缘呈反曲内凹弧线，峰顶为 1px 锋芒锐角，后缘三级阶梯递降。
# -------------------------------------------------------------
def draw_triple_crest_recurve(d, hx, hy, w1=0.0, w2=0.0, w3=0.0, fan=0.0, lift=0.0):
    c = C
    sw3 = w3 + fan * 1.5
    sw2 = w2 + fan * 0.4
    sw1 = w1 - fan * 0.8
    l3 = lift * 0.35
    l2 = lift * 0.7
    l1 = lift * 1.0

    # 1. Tier 3 (底层后羽 - 最靠近后脑勺，与头骨融为一体，平静低伏)
    p3 = [
        (hx + 1, hy - 10),
        (hx + 6 + sw3, hy - 13 - l3),
        (hx + 12 + sw3, hy - 14 - l3), # sharp tip 3 (calm lowered)
        (hx + 10 + sw3, hy - 12 - l3),
        (hx + 5, hy - 8)
    ]
    d.polygon(p3, fill=c["shade"])
    d.polygon([(hx + 2, hy - 10), (hx + 6 + sw3, hy - 12 - l3), (hx + 11 + sw3, hy - 13 - l3), (hx + 9 + sw3, hy - 11 - l3), (hx + 4, hy - 8)], fill=c["yellow"])

    # 2. Tier 2 (中间层副羽 - 紧密覆压在后羽之上，平静低伏)
    p2 = [
        (hx - 2, hy - 11),
        (hx + 3 + sw2, hy - 16 - l2 * 0.6),
        (hx + 10 + sw2, hy - 19 - l2), # sharp tip 2 (calm lowered)
        (hx + 11 + sw2, hy - 18 - l2),
        (hx + 7 + sw2, hy - 14 - l2 * 0.5),
        (hx + 2, hy - 10)
    ]
    d.polygon(p2, fill=c["shade"])
    d.polygon([(hx - 1, hy - 11), (hx + 3 + sw2, hy - 15 - l2 * 0.6), (hx + 9 + sw2, hy - 18 - l2), (hx + 10 + sw2, hy - 17 - l2), (hx + 6 + sw2, hy - 13 - l2 * 0.5), (hx + 1, hy - 10)], fill=c["yellow"])
    # 叠层交界处的暖琥珀羽褶阴影线
    d.line([(hx + 1, hy - 11), (hx + 7 + sw2, hy - 15 - l2 * 0.5)], fill=c["shade"], width=1)

    # 3. Tier 1 (最顶层主长羽 - 前缘饱满拱起反曲微挑，平静高度降低至 hy - 24)
    p1 = [
        (hx - 6, hy - 11),                   # 额基
        (hx - 2 + sw1, hy - 17 - l1 * 0.5),  # 前缘饱满微凸拱起 (反曲方向纠正)
        (hx + 3 + sw1, hy - 22 - l1 * 0.85), # 顺滑弧线向上后掠
        (hx + 7 + sw1, hy - 24 - l1),        # 平静梢部尖端 (hy-24，不再过高翘起)
        (hx + 8 + sw1, hy - 22 - l1),        # 尖锐反曲微挑
        (hx + 5 + sw1, hy - 17 - l1 * 0.8),  # 与副羽紧密叠合
        (hx + 2 + sw1, hy - 14 - l1 * 0.5),
        (hx, hy - 11)
    ]
    d.polygon(p1, fill=c["shade"])
    d.polygon([(hx - 5, hy - 11), (hx - 1 + sw1, hy - 17 - l1 * 0.5), (hx + 3 + sw1, hy - 21 - l1 * 0.85), (hx + 6 + sw1, hy - 23 - l1), (hx + 7 + sw1, hy - 22 - l1), (hx + 4 + sw1, hy - 17 - l1 * 0.8), (hx + 1 + sw1, hy - 14 - l1 * 0.5), (hx - 1, hy - 11)], fill=c["yellow"])
    # 迎风面象牙金高光
    d.line([(hx - 5, hy - 11), (hx - 1 + sw1, hy - 17 - l1 * 0.5), (hx + 5 + sw1, hy - 23 - l1)], fill=c["highlight"], width=1)
    # 主羽与副羽重叠的分界羽褶阴影
    d.line([(hx, hy - 11), (hx + 4 + sw1, hy - 17 - l1 * 0.8)], fill=c["shade"], width=1)

def draw_triple_crest_low(d, hx, hy):
    c = C
    # 三簇顺滑贴背，紧密相互重叠
    p3 = [(hx + 1, hy - 10), (hx + 6, hy - 13), (hx + 11, hy - 15), (hx + 9, hy - 11), (hx + 4, hy - 9)]
    d.polygon(p3, fill=c["shade"])
    d.polygon([(hx + 2, hy - 10), (hx + 6, hy - 12), (hx + 10, hy - 14), (hx + 8, hy - 11), (hx + 3, hy - 9)], fill=c["yellow"])
    
    p2 = [(hx - 1, hy - 11), (hx + 6, hy - 15), (hx + 14, hy - 14), (hx + 12, hy - 11), (hx + 5, hy - 9)]
    d.polygon(p2, fill=c["shade"])
    d.polygon([(hx, hy - 11), (hx + 6, hy - 14), (hx + 13, hy - 13), (hx + 11, hy - 11), (hx + 4, hy - 9)], fill=c["yellow"])
    d.line([(hx + 1, hy - 11), (hx + 10, hy - 13)], fill=c["shade"], width=1)

    p1 = [(hx - 4, hy - 11), (hx + 7, hy - 16), (hx + 18, hy - 13), (hx + 16, hy - 10), (hx + 6, hy - 9)]
    d.polygon(p1, fill=c["shade"])
    d.polygon([(hx - 3, hy - 11), (hx + 7, hy - 15), (hx + 17, hy - 12), (hx + 15, hy - 10), (hx + 5, hy - 9)], fill=c["yellow"])
    d.line([(hx - 2, hy - 11), (hx + 15, hy - 13)], fill=c["highlight"], width=1)

def draw_triple_crest_streamline(d, hx, hy, wave_y=0):
    c = C
    p3 = [(hx + 1, hy - 10), (hx + 7, hy - 13 + wave_y), (hx + 14, hy - 13 + wave_y), (hx + 11, hy - 11), (hx + 5, hy - 8)]
    d.polygon(p3, fill=c["shade"])
    d.polygon([(hx + 2, hy - 10), (hx + 7, hy - 12 + wave_y), (hx + 13, hy - 12 + wave_y), (hx + 10, hy - 11), (hx + 4, hy - 8)], fill=c["yellow"])

    p2 = [(hx - 1, hy - 11), (hx + 7, hy - 16 + wave_y), (hx + 18, hy - 15 + wave_y), (hx + 14, hy - 11), (hx + 4, hy - 9)]
    d.polygon(p2, fill=c["shade"])
    d.polygon([(hx, hy - 11), (hx + 7, hy - 15 + wave_y), (hx + 17, hy - 14 + wave_y), (hx + 13, hy - 11), (hx + 3, hy - 9)], fill=c["yellow"])
    d.line([(hx + 1, hy - 11), (hx + 12, hy - 14 + wave_y)], fill=c["shade"], width=1)

    p1 = [(hx - 4, hy - 11), (hx + 8, hy - 18 + wave_y), (hx + 22, hy - 16 + wave_y), (hx + 17, hy - 11), (hx + 5, hy - 9)]
    d.polygon(p1, fill=c["shade"])
    d.polygon([(hx - 3, hy - 11), (hx + 8, hy - 17 + wave_y), (hx + 21, hy - 15 + wave_y), (hx + 16, hy - 11), (hx + 4, hy - 9)], fill=c["yellow"])
    d.line([(hx - 2, hy - 11), (hx + 18, hy - 15 + wave_y)], fill=c["highlight"], width=1)

def draw_triple_crest_preen(d, hx, hy, angle_deg=0.0):
    """灵动三毛羽冠理毛起伏动态 - 纯刚体轴心旋转 (羽长100%恒定绝对不发生拉伸形变)"""
    c = C
    ox, oy = hx, hy - 8 # 颅顶羽根旋转支点

    def rotate_pt(px, py):
        rad = math.radians(angle_deg)
        cos_a = math.cos(rad)
        sin_a = math.sin(rad)
        dx = px - ox
        dy = py - oy
        return (round(ox + dx * cos_a - dy * sin_a), round(oy + dx * sin_a + dy * cos_a))

    # 1. Tier 3 (额基短羽)
    orig_p3_outer = [(hx - 1, hy - 9), (hx - 5, hy - 13), (hx - 9, hy - 14), (hx - 8, hy - 11), (hx - 3, hy - 8)]
    orig_p3_inner = [(hx - 1, hy - 9), (hx - 5, hy - 12), (hx - 8, hy - 13), (hx - 7, hy - 11), (hx - 2, hy - 8)]
    p3_outer = [rotate_pt(x, y) for x, y in orig_p3_outer]
    p3_inner = [rotate_pt(x, y) for x, y in orig_p3_inner]
    d.polygon(p3_outer, fill=c["shade"])
    d.polygon(p3_inner, fill=c["yellow"])

    # 2. Tier 2 (副中羽)
    orig_p2_outer = [(hx + 1, hy - 10), (hx - 4, hy - 16), (hx - 12, hy - 18), (hx - 10, hy - 15), (hx - 4, hy - 10)]
    orig_p2_inner = [(hx, hy - 10), (hx - 4, hy - 15), (hx - 11, hy - 17), (hx - 9, hy - 14), (hx - 3, hy - 10)]
    p2_outer = [rotate_pt(x, y) for x, y in orig_p2_outer]
    p2_inner = [rotate_pt(x, y) for x, y in orig_p2_inner]
    d.polygon(p2_outer, fill=c["shade"])
    d.polygon(p2_inner, fill=c["yellow"])
    d.line([rotate_pt(hx - 1, hy - 10), rotate_pt(hx - 8, hy - 14)], fill=c["shade"], width=1)

    # 3. Tier 1 (主长羽)
    orig_p1_outer = [(hx + 3, hy - 10), (hx - 3, hy - 17), (hx - 11, hy - 23), (hx - 15, hy - 21), (hx - 8, hy - 14), (hx - 2, hy - 8)]
    orig_p1_inner = [(hx + 2, hy - 10), (hx - 3, hy - 16), (hx - 10, hy - 21), (hx - 13, hy - 20), (hx - 7, hy - 13), (hx - 1, hy - 8)]
    p1_outer = [rotate_pt(x, y) for x, y in orig_p1_outer]
    p1_inner = [rotate_pt(x, y) for x, y in orig_p1_inner]
    d.polygon(p1_outer, fill=c["shade"])
    d.polygon(p1_inner, fill=c["yellow"])
    d.line([rotate_pt(hx + 1, hy - 10), rotate_pt(hx - 9, hy - 19)], fill=c["highlight"], width=1)

def draw_classic_crest_preen(d, hx, hy, angle_deg=0.0):
    """经典兔耳羽冠理毛起伏动态 - 纯刚体轴心旋转 (羽长100%恒定绝对不发生拉伸形变)"""
    c = C
    ox, oy = hx, hy - 8 # 颅顶羽根旋转支点

    def rotate_pt(px, py):
        rad = math.radians(angle_deg)
        cos_a = math.cos(rad)
        sin_a = math.sin(rad)
        dx = px - ox
        dy = py - oy
        return (round(ox + dx * cos_a - dy * sin_a), round(oy + dx * sin_a + dy * cos_a))

    orig_outer = [
        (hx + 3, hy - 10),
        (hx - 3, hy - 16),
        (hx - 11, hy - 22),
        (hx - 15, hy - 20),
        (hx - 8, hy - 13),
        (hx - 2, hy - 8)
    ]
    orig_inner = [
        (hx + 1, hy - 10),
        (hx - 3, hy - 15),
        (hx - 10, hy - 20),
        (hx - 13, hy - 19),
        (hx - 7, hy - 12),
        (hx - 1, hy - 7)
    ]
    outer = [rotate_pt(x, y) for x, y in orig_outer]
    inner = [rotate_pt(x, y) for x, y in orig_inner]
    d.polygon(outer, fill=c["shade"])
    d.polygon(inner, fill=c["yellow"])
    d.line([rotate_pt(hx - 1, hy - 11), rotate_pt(hx - 9, hy - 18)], fill=c["yellow"], width=1)

def draw_triple_crest_peck_aim(d, hx, hy):
    c = C
    p3 = [(hx + 2, hy - 10), (hx + 4, hy - 16), (hx + 7, hy - 19), (hx + 5, hy - 17), (hx + 3, hy - 10)]
    d.polygon(p3, fill=c["shade"])
    d.polygon([(hx + 2, hy - 10), (hx + 4, hy - 15), (hx + 6, hy - 18), (hx + 4, hy - 16), (hx + 3, hy - 10)], fill=c["yellow"])

    p2 = [(hx, hy - 11), (hx + 1, hy - 19), (hx + 4, hy - 24), (hx + 3, hy - 21), (hx + 1, hy - 11)]
    d.polygon(p2, fill=c["shade"])
    d.polygon([(hx, hy - 11), (hx + 1, hy - 18), (hx + 3, hy - 23), (hx + 2, hy - 20), (hx + 1, hy - 11)], fill=c["yellow"])
    d.line([(hx + 1, hy - 11), (hx + 2, hy - 18)], fill=c["shade"], width=1)

    p1 = [(hx - 5, hy - 10), (hx - 3, hy - 20), (hx + 1, hy - 27), (hx + 3, hy - 24), (hx - 1, hy - 11)]
    d.polygon(p1, fill=c["shade"])
    d.polygon([(hx - 4, hy - 10), (hx - 2, hy - 19), (hx + 1, hy - 25), (hx + 2, hy - 23), (hx - 1, hy - 11)], fill=c["yellow"])
    d.line([(hx - 4, hy - 10), (hx, hy - 25)], fill=c["highlight"], width=1)

def draw_triple_crest_peck_whip(d, hx, hy):
    c = C
    p3 = [(hx - 1, hy - 9), (hx - 4, hy - 14), (hx - 8, hy - 16), (hx - 6, hy - 14), (hx + 1, hy - 9)]
    d.polygon(p3, fill=c["shade"])
    d.polygon([(hx - 1, hy - 9), (hx - 4, hy - 13), (hx - 7, hy - 15), (hx - 5, hy - 13), (hx + 1, hy - 9)], fill=c["yellow"])

    p2 = [(hx - 3, hy - 10), (hx - 8, hy - 17), (hx - 13, hy - 21), (hx - 10, hy - 18), (hx - 1, hy - 10)]
    d.polygon(p2, fill=c["shade"])
    d.polygon([(hx - 2, hy - 10), (hx - 7, hy - 16), (hx - 12, hy - 20), (hx - 9, hy - 17), (hx - 1, hy - 10)], fill=c["yellow"])
    d.line([(hx - 1, hy - 10), (hx - 9, hy - 17)], fill=c["shade"], width=1)

    p1 = [(hx - 5, hy - 9), (hx - 11, hy - 17), (hx - 17, hy - 21), (hx - 14, hy - 26), (hx - 7, hy - 17), (hx + 2, hy - 10)]
    d.polygon(p1, fill=c["shade"])
    d.polygon([(hx - 4, hy - 10), (hx - 10, hy - 17), (hx - 15, hy - 21), (hx - 13, hy - 24), (hx - 6, hy - 17), (hx + 1, hy - 11)], fill=c["yellow"])
    d.line([(hx - 4, hy - 10), (hx - 13, hy - 22)], fill=c["highlight"], width=1)

def draw_triple_crest_peck_lag(d, hx, hy):
    c = C
    p3 = [(hx + 3, hy - 9), (hx + 9, hy - 14), (hx + 14, hy - 17), (hx + 11, hy - 14), (hx + 4, hy - 9)]
    d.polygon(p3, fill=c["shade"])
    d.polygon([(hx + 3, hy - 9), (hx + 8, hy - 13), (hx + 13, hy - 16), (hx + 10, hy - 13), (hx + 4, hy - 9)], fill=c["yellow"])

    p2 = [(hx + 1, hy - 10), (hx + 6, hy - 18), (hx + 12, hy - 22), (hx + 9, hy - 18), (hx + 3, hy - 10)]
    d.polygon(p2, fill=c["shade"])
    d.polygon([(hx + 1, hy - 10), (hx + 5, hy - 17), (hx + 11, hy - 21), (hx + 8, hy - 17), (hx + 2, hy - 10)], fill=c["yellow"])
    d.line([(hx + 2, hy - 10), (hx + 8, hy - 18)], fill=c["shade"], width=1)

    p1 = [(hx - 5, hy - 10), (hx + 1, hy - 20), (hx + 9, hy - 26), (hx + 12, hy - 22), (hx + 4, hy - 12), (hx + 2, hy - 10)]
    d.polygon(p1, fill=c["shade"])
    d.polygon([(hx - 4, hy - 10), (hx + 1, hy - 19), (hx + 8, hy - 25), (hx + 10, hy - 22), (hx + 3, hy - 12), (hx + 1, hy - 11)], fill=c["yellow"])
    d.line([(hx - 3, hy - 10), (hx + 7, hy - 24)], fill=c["highlight"], width=1)

def draw_triple_crest_bonk_windup(d, hx, hy):
    draw_triple_crest_recurve(d, hx, hy, w1=-1.0, w2=-0.5, w3=0.2, lift=2.5)

def draw_triple_crest_bonk_lunge(d, hx, hy):
    draw_triple_crest_streamline(d, hx, hy, wave_y=0)

def draw_triple_crest_bonk_whip(d, hx, hy):
    draw_triple_crest_peck_whip(d, hx, hy)

def draw_triple_crest_bonk_recoil(d, hx, hy):
    draw_triple_crest_recurve(d, hx, hy, w1=1.5, w2=0.8, w3=-0.3, lift=2.0)

def bird_q_optimized(
    head=(0, 0), lift=0, step=0, wing="fold", puff=0, eye="open",
    crest="normal", mouth="closed", crumbs=False, note=0,
    body_roll=0, tail_wag=0, tuck_feet=False, crest_style="triple"
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
    # 呼吸蓬毛效果由主体双层嵌套膨胀椭圆平滑呈现，移除遗留的固定坐标硬边绒毛矩形（曾导致 (34, 56) 与 (39, 64) 冲破身体墨边轮廓向外凸出两个异物方块）

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

    # 7. CREST (可配置: 经典兔耳 vs 灵动三毛)
    if crest_style == "classic":
        if crest in ("low", "hop_leap", "streamline"):
            # 顺滑贴向后脑 (求摸/生气/腾空前跃风阻贴背)
            d.polygon([(hx - 4, hy - 11), (hx + 8, hy - 15), (hx + 17, hy - 13), (hx + 5, hy - 9)], fill=c["shade"])
            d.line([(hx - 2, hy - 12), (hx + 16, hy - 14)], fill=c["yellow"], width=3)
        elif crest == "alert":
            # 笔直高耸炸毛 (警觉/受惊/起立蓄力)
            d.polygon([(hx - 5, hy - 10), (hx - 1, hy - 28), (hx + 2, hy - 30), (hx + 3, hy - 11)], fill=c["shade"])
            d.polygon([(hx, hy - 11), (hx + 7, hy - 25), (hx + 9, hy - 24), (hx + 4, hy - 9)], fill=c["yellow"])
        elif crest == "breath":
            # 呼吸微颤 (稍微弹起1像素)
            d.polygon([(hx - 6, hy - 11), (hx + 1, hy - 22), (hx + 14, hy - 27), (hx + 12, hy - 20), (hx + 3, hy - 10)], fill=c["shade"])
            d.polygon([(hx - 4, hy - 12), (hx + 2, hy - 21), (hx + 13, hy - 26), (hx + 10, hy - 21), (hx + 1, hy - 11)], fill=c["yellow"])
        else:
            # 自然软萌微弯 (包括 normal)
            d.polygon([(hx - 7, hy - 11), (hx + 1, hy - 21), (hx + 14, hy - 26), (hx + 12, hy - 19), (hx + 3, hy - 10)], fill=c["shade"])
            d.polygon([(hx - 5, hy - 12), (hx + 2, hy - 20), (hx + 13, hy - 25), (hx + 10, hy - 20), (hx + 1, hy - 11)], fill=c["yellow"])
    else: # triple
        if crest in ("low", "hop_leap"):
            # 顺滑贴背 / 腾空风阻后掠
            draw_triple_crest_low(d, hx, hy)
        elif crest == "streamline":
            draw_triple_crest_streamline(d, hx, hy, wave_y=0)
        elif crest == "alert":
            # 笔直挺拔高耸
            draw_triple_crest_recurve(d, hx, hy, w1=-1.8, w2=-1.0, w3=0.3, lift=3.5)
        elif crest == "breath":
            draw_triple_crest_recurve(d, hx, hy, w1=-1.0, w2=-0.5, w3=0.2, lift=1.0)
        else:
            # 自然平静微弯 (包括 normal)
            draw_triple_crest_recurve(d, hx, hy, w1=0.0, w2=0.0, w3=0.0, fan=0.0, lift=0.0)

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

def sleeping_bird_q_optimized(puff=0, head=0, zzz=0, crest_style="triple"):
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
    
    # 顺滑贴背的呆毛 (可配置: 经典兔耳 vs 灵动三毛)
    if crest_style == "classic":
        d.polygon([(hx - 6, hy - 11), (hx + 7, hy - 15), (hx + 18, hy - 10), (hx + 7, hy - 8)], fill=c["shade"])
        d.line([(hx - 4, hy - 12), (hx + 17, hy - 11)], fill=c["yellow"], width=3)
    else:
        draw_triple_crest_low(d, hx, hy)
    
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
    crest_style="triple",
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

    # 7. CREST (羽冠 - 顺风流线型后掠，可配置: 经典兔耳 vs 灵动三毛)
    wave_y = 1 if wing_phase in (1, 2) else 0
    if crest_style == "classic":
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
    else: # triple
        draw_triple_crest_streamline(d, hx, hy, wave_y)

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

def render_true_ground_peck_frame(phase=0, crest_style="triple", with_grain=True):
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

    # 7. CREST INERTIA (羽冠惯性动力学 - 可配置: 经典兔耳 vs 灵动三毛)
    if crest_style == "classic":
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
    else: # triple
        if crest_mode == "peck_impact_whip":
            draw_triple_crest_peck_whip(d, hx, hy)
        elif crest_mode == "peck_rebound_lag":
            draw_triple_crest_peck_lag(d, hx, hy)
        elif crest_mode == "peck_aim":
            draw_triple_crest_peck_aim(d, hx, hy)
        else: # peck_recover_settle
            draw_triple_crest_recurve(d, hx, hy)

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

    if with_grain:
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

    # 11. GROUND GRAIN PARTICLES (自然取食地面金黄小米颗粒进食剧情: 方案A 经典金黄小米堆；兴奋敲桌时不绘制)
    if with_grain:
        def draw_single_millet(gx, gy, hl=False):
            d.point((gx, gy + 1), fill="#c67c00")      # 底部阴影
            d.point((gx + 1, gy + 1), fill="#b36200")  # 底部深暗角
            d.point((gx, gy), fill="#ffea75" if hl else "#ffd54f") # 浅金反光
            d.point((gx + 1, gy), fill="#ffa000")      # 暖金颗粒

        if phase == 0:
            # Phase 0: 瞄准准备，地面散落 4 粒金黄小米与细屑
            draw_single_millet(12, 68) # 目标小米 A (正对嘴喙俯探落点)
            draw_single_millet(7, 70)  # 旁侧小米 B
            draw_single_millet(17, 69) # 旁侧小米 C
            d.point((22, 71), fill="#ffd54f") # 散落小谷粒 D
            d.point((15, 71), fill="#ffa000") # 细微谷屑
        elif phase == 1:
            # Phase 1: 触地啄击，喙尖正中目标小米 A，邻近谷粒受冲击微跳 1px
            draw_single_millet(12, 67, hl=True) # 目标小米受压高光
            draw_single_millet(6, 69)  # 谷粒 B 受震动微跳
            draw_single_millet(18, 69) # 谷粒 C 微震
            d.point((22, 71), fill="#ffd54f") # 散落小谷粒 D
            d.point((10, 66), fill="#fff59d") # 冲击微粒
            d.point((15, 68), fill="#ffa000")
        elif phase == 2:
            # Phase 2: 触地回弹，目标小米已叼入口中，地面留下剩余 3 粒谷物与碎屑
            draw_single_millet(7, 70)  # 谷粒 B 回落平稳
            draw_single_millet(17, 70) # 谷粒 C 回落平稳
            d.point((22, 71), fill="#ffd54f") # 小谷粒 D
            d.point((13, 71), fill="#c67c00") # 目标小米被叼走后遗留的微粒碎屑
        else: # phase == 3
            # Phase 3: 顺势抬头惬意咀嚼，地面余粮安静等待下一次啄食
            draw_single_millet(7, 70)
            draw_single_millet(17, 70)
            d.point((22, 71), fill="#ffd54f")
            d.point((13, 71), fill="#c67c00")

    return im

def render_bonk_screen_frame(frame_idx=0, crest_style="triple"):
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

    # 7. CREST INERTIA (敲击屏幕惯性羽冠 - 可配置: 经典兔耳 vs 灵动三毛)
    if crest_style == "classic":
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
    else: # triple
        if crest_mode == "bonk_impact_whip":
            draw_triple_crest_bonk_whip(d, hx, hy)
        elif crest_mode == "bonk_lunge_wind":
            draw_triple_crest_bonk_lunge(d, hx, hy)
        elif crest_mode == "bonk_recoil_snap":
            draw_triple_crest_bonk_recoil(d, hx, hy)
        elif crest_mode == "bonk_windup":
            draw_triple_crest_bonk_windup(d, hx, hy)
        else: # bonk_settle_proud
            draw_triple_crest_recurve(d, hx, hy, w1=-1.8, w2=-1.0, w3=0.3, lift=3.5)

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

def render_preen_back_frame(phase=0, crest_style="triple"):
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

    # 9. CREST UNDULATION (理毛羽冠匀速小摆幅起伏: 纯刚体轴心严格匀速摆动，每帧绝对角位移严格恒定为 6°，绝对匀速不加速，羽长100%恒定守恒)
    # Phase 0: 探头就位 (angle = 0.0°)
    # Phase 1: 深入啄理，头部下潜，羽冠匀速微幅向下贴枕 (angle = -6.0°)
    # Phase 2: 挑羽回升，羽冠匀速回正 (angle = 0.0°)
    # Phase 3: 舒缓微扬，羽冠匀速微幅上扬 (angle = +6.0°)
    preen_angles = [0.0, -6.0, 0.0, 6.0]
    crest_ang = preen_angles[phase]

    if crest_style == "classic":
        draw_classic_crest_preen(d, hx, hy, angle_deg=crest_ang)
    else: # triple
        draw_triple_crest_preen(d, hx, hy, angle_deg=crest_ang)

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

# -------------------------------------------------------------
# 30秒闲置杂技踩球 (300帧 260x120 高清像素舞台)
# -------------------------------------------------------------
def render_pure_red_ball(size=36, squash_y=1.0):
    w = size
    h = max(4, int(size * squash_y))
    im = Image.new("RGBA", (w + 4, h + 4), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    ox, oy = 2, 2
    rx, ry = w / 2.0, h / 2.0
    cx, cy = ox + rx, oy + ry
    d.ellipse((ox, oy, ox + w - 1, oy + h - 1), fill="#3b0914")
    d.ellipse((ox + 1, oy + 1, ox + w - 2, oy + h - 2), fill="#e63946")
    d.ellipse((ox + 3, oy + 3, ox + w - 2, oy + h - 2), fill="#9b111e")
    d.ellipse((ox + 1, oy + 1, ox + w - 4, oy + h - 4), fill="#d90429")
    d.ellipse((ox + 2, oy + 2, ox + w - 5, oy + h - 5), fill="#e63946")
    hl_cx = cx - rx * 0.42
    hl_cy = cy - ry * 0.42
    d.ellipse((hl_cx - 3.5, hl_cy - 3.5, hl_cx + 3.5, hl_cy + 3.5), fill="#ff758f")
    d.ellipse((hl_cx - 2, hl_cy - 2, hl_cx + 2, hl_cy + 2), fill="#ffffff")
    d.point((int(hl_cx + 4), int(hl_cy - 1)), fill="#ffffff")
    return im

def draw_play_ball_shadow(d, cx, ground_y, radius=18, squash=1.0, alpha_factor=1.0, cw=260):
    sw = int(radius * 1.6 * squash)
    sh = int(radius * 0.42 * squash)
    if sw > 2 and sh > 1 and alpha_factor > 0.05 and cx > -20 and cx < cw + 20:
        d.ellipse(
            (int(cx - sw / 2), int(ground_y - sh / 2), int(cx + sw / 2), int(ground_y + sh / 2)),
            fill=(35, 35, 45, int(85 * alpha_factor))
        )

def draw_play_ball_bird_shadow(d, cx, ground_y, width=28, alpha_factor=1.0):
    d.ellipse(
        (int(cx - width / 2), int(ground_y - 2), int(cx + width / 2), int(ground_y + 3)),
        fill=(35, 35, 45, int(75 * alpha_factor))
    )

def draw_play_ball_feet(d, bird_x, bird_y, ball_cx, ball_top_y, step=0, sway=0, facing_right=False):
    c = C
    if not facing_right:
        leg_left_top = (bird_x + 48 + sway, bird_y + 64)
        leg_right_top = (bird_x + 58 + sway, bird_y + 64)
        if step == 0:
            l_foot = (ball_cx - 5, ball_top_y + 2)
            r_foot = (ball_cx + 6, ball_top_y + 2)
        elif step == 1:
            l_foot = (ball_cx - 8, ball_top_y + 4)
            r_foot = (ball_cx + 4, ball_top_y + 1)
        else:
            l_foot = (ball_cx - 4, ball_top_y + 1)
            r_foot = (ball_cx + 8, ball_top_y + 4)
        for (lx, ly), (tx, ty) in [(leg_left_top, l_foot), (leg_right_top, r_foot)]:
            d.line([(lx, ly), (tx, ty)], fill=c["ink"], width=3)
            d.line([(lx, ly), (tx, ty)], fill=c["foot"], width=2)
            d.line([(tx - 3, ty), (tx + 2, ty + 1)], fill=c["foot"], width=2)
    else:
        leg_left_top = (bird_x + 42 + sway, bird_y + 64)
        leg_right_top = (bird_x + 52 + sway, bird_y + 64)
        if step == 0:
            l_foot = (ball_cx - 6, ball_top_y + 2)
            r_foot = (ball_cx + 5, ball_top_y + 2)
        elif step == 1:
            l_foot = (ball_cx - 4, ball_top_y + 1)
            r_foot = (ball_cx + 8, ball_top_y + 4)
        else:
            l_foot = (ball_cx - 8, ball_top_y + 4)
            r_foot = (ball_cx + 4, ball_top_y + 1)
        for (lx, ly), (tx, ty) in [(leg_left_top, l_foot), (leg_right_top, r_foot)]:
            d.line([(lx, ly), (tx, ty)], fill=c["ink"], width=3)
            d.line([(lx, ly), (tx, ty)], fill=c["foot"], width=2)
            d.line([(tx - 2, ty + 1), (tx + 3, ty)], fill=c["foot"], width=2)

def draw_play_ball_sparkle(d, x, y, size=3, color="#ffd166"):
    d.line([(x - size, y), (x + size, y)], fill=color, width=1)
    d.line([(x, y - size), (x, y + size)], fill=color, width=1)
    d.point((x, y), fill="#ffffff")

# -------------------------------------------------------------
# Canonical 27-Degree Standing Legs Compositor (统一标准 27° 前倾站姿)
# -------------------------------------------------------------
_GROUND_Y = 73
_INK = (53, 52, 56, 255)
_INKISH = {(53, 52, 56, 255), (44, 43, 48, 255)}
_NEAR_HI = (234, 214, 207, 255)
_NEAR = (196, 171, 167, 255)
_NEAR_SH = (170, 145, 142, 255)
_FAR = (154, 130, 131, 255)
_FAR_SH = (132, 109, 110, 255)
_FAR_HI = (177, 153, 153, 255)
_LEG = {
    (187, 165, 165, 255),
    (165, 144, 144, 255),
    (200, 184, 181, 255),
}
_NEAR_SHIFT = 2
_HIP_FORWARD = 1

def clean_legs_local(im):
    out = im.copy()
    pixels = out.load()
    w, h = im.size
    leg_points = [
        (x, y)
        for y in range(55, h)
        for x in range(w)
        if im.getpixel((x, y)) in _LEG
    ]
    clear = set(leg_points)
    for x, y in leg_points:
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                qx, qy = x + dx, y + dy
                if 0 <= qx < w and 0 <= qy < h and im.getpixel((qx, qy)) in _INKISH:
                    clear.add((qx, qy))
    for x, y in clear:
        pixels[x, y] = (0, 0, 0, 0)
    return out

def body_bottom(body):
    w, h = body.size
    for y in range(h - 1, 54, -1):
        xs = [x for x in range(w) if body.getpixel((x, y))[3]]
        if len(xs) >= 4:
            return y, (min(xs) + max(xs)) // 2
    return 69, 50

def runs_at(im, y):
    w = im.size[0]
    xs = [x for x in range(w) if im.getpixel((x, y)) in _LEG]
    if not xs:
        return []
    runs = []
    start = prev = xs[0]
    for x in xs[1:]:
        if x != prev + 1:
            runs.append((start, prev))
            start = x
        prev = x
    runs.append((start, prev))
    return runs

def feet_centers(im):
    runs = runs_at(im, 73) or runs_at(im, 72)
    left = [r for r in runs if (r[0] + r[1]) / 2 < 49]
    right = [r for r in runs if (r[0] + r[1]) / 2 >= 49]
    front = (left[0][0] + left[0][1]) / 2 if left else 41.5
    back = (right[-1][0] + right[-1][1]) / 2 if right else 54.5
    return front, back

def _stroke(draw, points, fill, width):
    draw.line(points, fill=fill, width=width, joint="curve")
    radius = width // 2
    for x, y in points:
        draw.rectangle(
            (x - radius, y - radius, x - radius + width - 1, y - radius + width - 1),
            fill=fill,
        )

def _leg_points(hip, ankle, bend):
    t = 0.55
    return [
        hip,
        (
            round(hip[0] * (1 - t) + ankle[0] * t) + bend,
            round(hip[1] * (1 - t) + ankle[1] * t),
        ),
        ankle,
    ]

def _draw_far_leg(draw, hip, foot_x):
    foot = round(foot_x)
    ankle = (foot + 2, _GROUND_Y - 2)
    points = _leg_points(hip, ankle, 1)
    _stroke(draw, points, _FAR, 2)
    draw.point((points[1][0] - 1, points[1][1]), fill=_FAR_HI)
    draw.point((ankle[0] - 1, ankle[1] - 1), fill=_FAR_HI)
    top = _GROUND_Y - 1
    draw.rectangle((foot - 2, top, foot + 2, top + 1), fill=_FAR)
    draw.line((foot - 2, top + 1, foot + 2, top + 1), fill=_FAR_SH, width=1)
    draw.point((foot - 3, top + 1), fill=_FAR_SH)

def _draw_near_leg(draw, hip, foot_x):
    foot = round(foot_x)
    ankle = (foot + 2, _GROUND_Y - 2)
    points = _leg_points(hip, ankle, 1)
    _stroke(draw, points, _INK, 4)
    _stroke(draw, points, _NEAR, 2)
    _stroke(draw, [(x - 1, y) for x, y in points], _NEAR_HI, 1)
    top = _GROUND_Y - 1
    draw.rectangle((foot - 4, top, foot + 3, top + 1), fill=_NEAR)
    draw.line((foot - 4, top, foot + 2, top), fill=_NEAR_HI, width=1)
    draw.line((foot - 4, top + 1, foot + 3, top + 1), fill=_NEAR_SH, width=1)
    draw.point((foot + 3, top - 1), fill=_NEAR_SH)
    draw.point((foot + 2, top - 1), fill=_NEAR)

def render_standard_legs(im):
    w, h = im.size
    body = clean_legs_local(im)
    by, bc = body_bottom(body)
    front, back = feet_centers(im)
    front += _NEAR_SHIFT
    hip_y = max(65, by - 4)
    hip_x = round(front) + (6 if hip_y == 65 else 4) - _HIP_FORWARD

    canvas = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    far_layer = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    _draw_far_leg(ImageDraw.Draw(far_layer), (round(back) + 3, 63), back)
    canvas.alpha_composite(far_layer)
    canvas.alpha_composite(body)

    near_layer = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    _draw_near_leg(ImageDraw.Draw(near_layer), (hip_x, hip_y), front)
    canvas.alpha_composite(near_layer)

    for x in range(hip_x - 2, hip_x + 2):
        c = body.getpixel((x, hip_y - 1))
        if c[3]:
            canvas.putpixel((x, hip_y - 1), c)

    return canvas

def build_play_ball_frames(crest_style: str = "triple") -> dict:
    CW = 260
    CH = 120
    GY = 98
    BALL_SIZE = 36
    frames = []

    # Act 1: 0.0s - 2.5s (25 frames) - 初始站立与等待红球掉落
    ball_spawn_x = 110
    bird_start_cx = 175
    for _ in range(2):
        im = Image.new("RGBA", (CW, CH), (0, 0, 0, 0))
        d = ImageDraw.Draw(im)
        draw_play_ball_bird_shadow(d, bird_start_cx, GY)
        b_im = render_standard_legs(bird_q_optimized(crest_style=crest_style))
        im.paste(b_im, (bird_start_cx - 53, GY - 72), b_im)
        frames.append(im)
        
    fall_ys = [8, 32, 58, 80, GY]
    for i, fy in enumerate(fall_ys):
        im = Image.new("RGBA", (CW, CH), (0, 0, 0, 0))
        d = ImageDraw.Draw(im)
        draw_play_ball_bird_shadow(d, bird_start_cx, GY)
        if i < 2:
            b_im = bird_q_optimized(head=(-1, -1), crest="normal", crest_style=crest_style)
        elif i < 4:
            b_im = bird_q_optimized(head=(-2, -1), crest="high", crest_style=crest_style)
        else:
            b_im = bird_q_optimized(head=(-2, 0), crest="high", mouth="open", eye="open", crest_style=crest_style)
        b_im = render_standard_legs(b_im)
        im.paste(b_im, (bird_start_cx - 53, GY - 72), b_im)
        if fy < GY:
            ball_im = render_pure_red_ball(BALL_SIZE, squash_y=1.1)
            im.paste(ball_im, (ball_spawn_x - 18, fy - BALL_SIZE - 2), ball_im)
            draw_play_ball_shadow(d, ball_spawn_x, GY, radius=18, alpha_factor=max(0.1, fy / 100.0 * 0.7))
        else:
            ball_im = render_pure_red_ball(BALL_SIZE, squash_y=0.76)
            im.paste(ball_im, (ball_spawn_x - 18, GY - int(BALL_SIZE * 0.76) - 2), ball_im)
            draw_play_ball_shadow(d, ball_spawn_x, GY, radius=22, alpha_factor=1.0)
            d.line([(ball_spawn_x - 22, GY - 2), (ball_spawn_x - 25, GY - 5)], fill="#d6ccc2", width=2)
            d.line([(ball_spawn_x + 22, GY - 2), (ball_spawn_x + 25, GY - 5)], fill="#d6ccc2", width=2)
        frames.append(im)
        
    rebound_configs = [
        (GY - 45, 1.08, (-3, -1), "high", "whistle"),
        (GY - 38, 1.0, (-3, 0), "high", "normal"),
        (GY - BALL_SIZE, 1.0, (-4, 1), "high", "normal"),
        (GY - BALL_SIZE, 1.0, (-4, 2), "high", "normal"),
    ]
    for by, sq, h_off, cr, mth in rebound_configs:
        im = Image.new("RGBA", (CW, CH), (0, 0, 0, 0))
        d = ImageDraw.Draw(im)
        draw_play_ball_bird_shadow(d, bird_start_cx, GY)
        b_im = bird_q_optimized(lift=2 if h_off[1] > 0 else 0, head=h_off, crest=cr, mouth=mth, crest_style=crest_style)
        b_im = render_standard_legs(b_im)
        im.paste(b_im, (bird_start_cx - 53, GY - 72), b_im)
        draw_play_ball_shadow(d, ball_spawn_x, GY, radius=18, alpha_factor=0.9)
        ball_im = render_pure_red_ball(BALL_SIZE, squash_y=sq)
        im.paste(ball_im, (ball_spawn_x - 18, by - 2), ball_im)
        if mth == "whistle":
            d.text((bird_start_cx - 12, 32), "♪", fill="#ffb703")
        frames.append(im)
        
    flight_arc = [
        (165, GY - 10, "fly_up"),
        (154, GY - 20, "fly_mid"),
        (142, GY - 29, "fly_mid"),
        (130, GY - 35, "fly_mid"),
        (120, GY - 34, "fly_down"),
        (113, GY - 28, "fly_down"),
        (110, GY - 22, "fly_mid"),
        (110, GY - 18, "fly_mid"),
    ]
    for bcx, bby, w_mode in flight_arc:
        im = Image.new("RGBA", (CW, CH), (0, 0, 0, 0))
        d = ImageDraw.Draw(im)
        draw_play_ball_shadow(d, ball_spawn_x, GY, radius=18, alpha_factor=0.9)
        ball_im = render_pure_red_ball(BALL_SIZE, squash_y=1.0)
        im.paste(ball_im, (ball_spawn_x - 18, GY - BALL_SIZE - 2), ball_im)
        ground_dist = max(1, GY - bby)
        draw_play_ball_bird_shadow(d, bcx, GY, width=max(12, int(28 - ground_dist * 0.4)), alpha_factor=max(0.2, 0.7 - ground_dist * 0.015))
        b_im = bird_q_optimized(wing=w_mode, tuck_feet=True, crest="high", crest_style=crest_style)
        im.paste(b_im, (bcx - 53, bby - 72), b_im)
        frames.append(im)
        
    touchdown_sqs = [0.86, 0.92, 1.0, 1.0, 1.0, 1.0]
    for i, sq in enumerate(touchdown_sqs):
        im = Image.new("RGBA", (CW, CH), (0, 0, 0, 0))
        d = ImageDraw.Draw(im)
        draw_play_ball_shadow(d, ball_spawn_x, GY, radius=int(18 / sq), alpha_factor=0.95)
        ball_h = int(BALL_SIZE * sq)
        ball_top = GY - ball_h
        ball_im = render_pure_red_ball(BALL_SIZE, squash_y=sq)
        im.paste(ball_im, (ball_spawn_x - 18, ball_top - 2), ball_im)
        bird_x = ball_spawn_x - 53
        bird_y = ball_top - 64 + (2 if sq < 0.95 else 0)
        w_state = "fly_mid" if i < 2 else "fold"
        b_im = bird_q_optimized(wing=w_state, tuck_feet=True, crest="high" if i < 3 else "normal", crest_style=crest_style)
        im.paste(b_im, (bird_x, bird_y), b_im)
        draw_play_ball_feet(d, bird_x, bird_y, ball_spawn_x, ball_top, step=0)
        if i >= 3:
            draw_play_ball_sparkle(d, ball_spawn_x - 18, ball_top - 22, size=3, color="#ff477e")
        frames.append(im)

    # Act 2: Roll Left (50 frames)
    start_x, end_x = 110, 55
    for f in range(50):
        t = f / 49.0
        ease = t * t * (3 - 2 * t)
        cur_x = int(start_x + (end_x - start_x) * ease)
        step_type = 1 if (f // 2) % 2 == 0 else 2
        sway = -1 if step_type == 1 else 1
        im = Image.new("RGBA", (CW, CH), (0, 0, 0, 0))
        d = ImageDraw.Draw(im)
        draw_play_ball_shadow(d, cur_x, GY, radius=18, alpha_factor=0.9)
        ball_top = GY - BALL_SIZE
        ball_im = render_pure_red_ball(BALL_SIZE, squash_y=1.0)
        im.paste(ball_im, (cur_x - 18, ball_top - 2), ball_im)
        bird_x = cur_x - 53 + sway
        bird_y = ball_top - 64
        w_mode = "fly_mid" if f in [12, 13, 28, 29] else "fold"
        b_im = bird_q_optimized(wing=w_mode, tuck_feet=True, crest="high" if w_mode != "fold" else "normal", body_roll=sway, crest_style=crest_style)
        im.paste(b_im, (bird_x, bird_y), b_im)
        draw_play_ball_feet(d, bird_x, bird_y, cur_x, ball_top, step=step_type, sway=sway)
        if f in [15, 16, 17]:
            d.text((cur_x - 12, ball_top - 26), "♪", fill="#ffb703")
        elif f in [35, 36]:
            draw_play_ball_sparkle(d, cur_x - 16, ball_top - 22, size=3, color="#4cc9f0")
        frames.append(im)

    # Act 3: Balance (30 frames)
    for f in range(30):
        wobble = int(1.5 * math.sin(f * 0.4))
        cur_x = 55 + wobble
        im = Image.new("RGBA", (CW, CH), (0, 0, 0, 0))
        d = ImageDraw.Draw(im)
        draw_play_ball_shadow(d, cur_x, GY, radius=18, alpha_factor=0.9)
        ball_top = GY - BALL_SIZE
        ball_im = render_pure_red_ball(BALL_SIZE, squash_y=1.0)
        im.paste(ball_im, (cur_x - 18, ball_top - 2), ball_im)
        bird_x = cur_x - 53
        bird_y = ball_top - 64
        w_mode = "fly_up" if (f // 3) % 2 == 0 else "fly_mid"
        b_im = bird_q_optimized(wing=w_mode, tuck_feet=True, crest="high", tail_wag=2 if (f // 4) % 2 == 0 else -2, crest_style=crest_style)
        im.paste(b_im, (bird_x, bird_y), b_im)
        draw_play_ball_feet(d, bird_x, bird_y, cur_x, ball_top, step=0, sway=wobble)
        if f % 8 < 3:
            draw_play_ball_sparkle(d, cur_x + 18, ball_top - 24, size=3, color="#ffd166")
        frames.append(im)

    # Act 4: Sprint Right (60 frames)
    start_x, end_x = 55, 195
    for f in range(60):
        t = f / 59.0
        ease = t * t * (3 - 2 * t)
        cur_x = int(start_x + (end_x - start_x) * ease)
        step_type = 1 if (f // 2) % 2 == 0 else 2
        sway = 1 if step_type == 1 else -1
        im = Image.new("RGBA", (CW, CH), (0, 0, 0, 0))
        d = ImageDraw.Draw(im)
        draw_play_ball_shadow(d, cur_x, GY, radius=18, alpha_factor=0.9)
        ball_top = GY - BALL_SIZE
        ball_im = render_pure_red_ball(BALL_SIZE, squash_y=1.0)
        im.paste(ball_im, (cur_x - 18, ball_top - 2), ball_im)
        bird_x = cur_x - 47 + sway
        bird_y = ball_top - 64
        w_mode = "fly_mid" if f in [18, 19, 40, 41] else "fold"
        b_base = bird_q_optimized(wing=w_mode, tuck_feet=True, crest="high" if w_mode != "fold" else "normal", body_roll=-sway, crest_style=crest_style)
        b_flipped = b_base.transpose(Image.FLIP_LEFT_RIGHT)
        im.paste(b_flipped, (bird_x, bird_y), b_flipped)
        draw_play_ball_feet(d, bird_x, bird_y, cur_x, ball_top, step=step_type, sway=sway, facing_right=True)
        if f in [10, 11, 12, 32, 33]:
            d.text((cur_x + 12, ball_top - 26), "♪", fill="#ffb703")
        elif f in [22, 23, 50, 51]:
            draw_play_ball_sparkle(d, cur_x + 18, ball_top - 22, size=3, color="#ff477e")
        frames.append(im)

    # Act 5: Joyful Hops (30 frames)
    hop_frames = [
        (0, "fold", 0.92, True, "normal"),
        (-5, "fly_up", 1.04, True, "open"),
        (-10, "fly_mid", 1.0, True, "open"),
        (-12, "fly_mid", 1.0, True, "normal"),
        (-9, "fly_down", 1.0, True, "normal"),
        (-4, "fly_down", 1.0, True, "normal"),
        (0, "fly_mid", 0.86, True, "normal"),
        (0, "fold", 0.94, True, "whistle"),
        (0, "fold", 1.0, True, "normal"),
        (0, "fold", 1.0, True, "normal"),
        (0, "fold", 1.0, True, "normal"),
        (0, "fold", 1.0, True, "normal"),
        (0, "fold", 1.0, True, "normal"),
        (0, "fold", 0.94, True, "normal"),
        (0, "fold", 0.90, True, "normal"),
        (-4, "fly_up", 1.04, True, "open"),
        (-9, "fly_mid", 1.0, True, "open"),
        (-13, "fly_up", 1.0, False, "open"),
        (-11, "fly_mid", 1.0, False, "normal"),
        (-6, "fly_down", 1.0, False, "normal"),
        (-2, "fly_down", 1.0, False, "normal"),
        (0, "fly_mid", 0.86, False, "normal"),
        (0, "fold", 0.94, False, "whistle"),
        (0, "fold", 1.0, False, "normal"),
        (0, "fold", 1.0, False, "normal"),
        (0, "fold", 1.0, False, "normal"),
        (0, "fold", 1.0, False, "normal"),
        (0, "fold", 1.0, False, "normal"),
        (0, "fold", 1.0, False, "normal"),
        (0, "fold", 1.0, False, "normal"),
    ]
    cur_x = 195
    for (hop_y, w_mode, sq, is_facing_right, mth) in hop_frames:
        im = Image.new("RGBA", (CW, CH), (0, 0, 0, 0))
        d = ImageDraw.Draw(im)
        draw_play_ball_shadow(d, cur_x, GY, radius=int(18 / sq), alpha_factor=0.9)
        ball_h = int(BALL_SIZE * sq)
        ball_top = GY - ball_h
        ball_im = render_pure_red_ball(BALL_SIZE, squash_y=sq)
        im.paste(ball_im, (cur_x - 18, ball_top - 2), ball_im)
        bird_cx_off = 47 if is_facing_right else 53
        bird_x = cur_x - bird_cx_off
        bird_y = ball_top - 64 + hop_y
        b_base = bird_q_optimized(wing=w_mode, tuck_feet=True, crest="high", mouth=mth, crest_style=crest_style)
        if is_facing_right:
            b_base = b_base.transpose(Image.FLIP_LEFT_RIGHT)
        im.paste(b_base, (bird_x, bird_y), b_base)
        if hop_y == 0:
            draw_play_ball_feet(d, bird_x, bird_y, cur_x, ball_top, step=0, facing_right=is_facing_right)
        if mth == "whistle":
            d.text((cur_x - 10 if not is_facing_right else cur_x + 10, ball_top - 26), "♪", fill="#ffb703")
        frames.append(im)

    # Act 6: Roll Center (50 frames)
    start_x, end_x = 195, 125
    for f in range(50):
        t = f / 49.0
        ease = t * t * (3 - 2 * t)
        cur_x = int(start_x + (end_x - start_x) * ease)
        step_type = 1 if (f // 2) % 2 == 0 else 2
        sway = -1 if step_type == 1 else 1
        im = Image.new("RGBA", (CW, CH), (0, 0, 0, 0))
        d = ImageDraw.Draw(im)
        draw_play_ball_shadow(d, cur_x, GY, radius=18, alpha_factor=0.9)
        ball_top = GY - BALL_SIZE
        ball_im = render_pure_red_ball(BALL_SIZE, squash_y=1.0)
        im.paste(ball_im, (cur_x - 18, ball_top - 2), ball_im)
        bird_x = cur_x - 53 + sway
        bird_y = ball_top - 64
        w_mode = "fly_mid" if f in [14, 15, 36, 37] else "fold"
        b_im = bird_q_optimized(wing=w_mode, tuck_feet=True, crest="high" if w_mode != "fold" else "normal", body_roll=sway, crest_style=crest_style)
        im.paste(b_im, (bird_x, bird_y), b_im)
        draw_play_ball_feet(d, bird_x, bird_y, cur_x, ball_top, step=step_type, sway=sway)
        if f in [10, 11, 28, 29]:
            d.text((cur_x - 14, ball_top - 26), "♪", fill="#ffb703")
        elif f in [20, 21]:
            draw_play_ball_sparkle(d, cur_x - 18, ball_top - 22, size=3, color="#ffd166")
        frames.append(im)

    # Act 7: Feint brake (30 frames)
    for f in range(30):
        if f < 15:
            cur_x = int(125 - 10 * (f / 14.0))
        else:
            cur_x = int(115 + 5 * ((f - 15) / 14.0))
        step_type = 1 if (f // 2) % 2 == 0 else 2
        sway = -1 if step_type == 1 else 1
        im = Image.new("RGBA", (CW, CH), (0, 0, 0, 0))
        d = ImageDraw.Draw(im)
        draw_play_ball_shadow(d, cur_x, GY, radius=18, alpha_factor=0.9)
        ball_top = GY - BALL_SIZE
        ball_im = render_pure_red_ball(BALL_SIZE, squash_y=1.0)
        im.paste(ball_im, (cur_x - 18, ball_top - 2), ball_im)
        bird_x = cur_x - 53 + (sway if f < 25 else 0)
        bird_y = ball_top - 64
        w_mode = "fly_mid" if f >= 18 else "fold"
        b_im = bird_q_optimized(wing=w_mode, tuck_feet=True, crest="high", body_roll=sway if f < 25 else 0, crest_style=crest_style)
        im.paste(b_im, (bird_x, bird_y), b_im)
        draw_play_ball_feet(d, bird_x, bird_y, cur_x, ball_top, step=step_type if f < 25 else 0, sway=sway if f < 25 else 0)
        if f % 6 < 2:
            draw_play_ball_sparkle(d, cur_x - 20, ball_top - 24, size=3, color="#4cc9f0")
        frames.append(im)

    # Act 8: 华丽大谢幕与展翅着陆 (25 frames)
    final_x = 120
    ball_top = GY - BALL_SIZE
    # 8.1: Heart wings & singing on ball (10 frames)
    for i in range(10):
        im = Image.new("RGBA", (CW, CH), (0, 0, 0, 0))
        d = ImageDraw.Draw(im)
        draw_play_ball_shadow(d, final_x, GY, radius=18, alpha_factor=0.9)
        ball_im = render_pure_red_ball(BALL_SIZE, squash_y=1.0)
        im.paste(ball_im, (final_x - 18, ball_top - 2), ball_im)
        bird_x = final_x - 53
        bird_y = ball_top - 64
        b_im = bird_q_optimized(wing="heart", puff=1, crest="high", mouth="open" if i % 2 == 1 else "whistle", tail_wag=2 if i % 4 < 2 else -2, tuck_feet=True, crest_style=crest_style)
        im.paste(b_im, (bird_x, bird_y), b_im)
        draw_play_ball_feet(d, bird_x, bird_y, final_x, ball_top, step=0)
        draw_play_ball_sparkle(d, final_x - 25, ball_top - 30, size=4, color="#ffd166")
        draw_play_ball_sparkle(d, final_x + 25, ball_top - 26, size=3, color="#ff758f")
        if i % 3 == 1:
            d.text((final_x - 6, ball_top - 42), "♥", fill="#ff4d6d")
        frames.append(im)

    # 8.2: 展翅飞下地面 (7 frames) + 红球从身边顺势向前滚走消失
    flight_descent = [
        # (bcx, bby, wing, ball_x, lift)
        (120, ball_top + 64, "fly_up", 120, 2),  # 下蹲起飞预备
        (114, 56, "fly_up", 115, 0),             # 腾空起飞脱离球顶
        (106, 68, "fly_mid", 100, 0),            # 展翅平滑前下方俯冲滑翔
        (98, 79, "fly_down", 78, 0),             # 下扑翅膀减速缓冲
        (90, 89, "fly_mid", 52, 0),              # 贴近地面展翅
        (84, GY, "fly_down", 24, 2),             # 双爪稳稳触地，身体下沉缓冲
        (84, GY, "fold", -4, 0),                 # 站定收翅，红球滚出视野
    ]
    for (bcx, bby, w_mode, bx, l_val) in flight_descent:
        im = Image.new("RGBA", (CW, CH), (0, 0, 0, 0))
        d = ImageDraw.Draw(im)
        # 1. 红球在鸟身后滚过
        if bx > -25:
            draw_play_ball_shadow(d, bx, GY, radius=18, alpha_factor=max(0.2, (bx + 20) / 100.0 * 0.8))
            ball_im = render_pure_red_ball(BALL_SIZE, squash_y=1.0)
            im.paste(ball_im, (bx - 18, GY - BALL_SIZE - 2), ball_im)
        # 2. 小鸟地面投影
        ground_dist = max(1, GY - bby)
        draw_play_ball_bird_shadow(d, bcx, GY, width=max(14, int(28 - ground_dist * 0.3)), alpha_factor=max(0.25, 0.85 - ground_dist * 0.012))
        # 3. 小鸟飞行姿态与着陆
        if bby == GY and w_mode == "fly_down":
            # 触地瞬间 (frame 290): 双爪稳稳触地，屈腿缓冲下沉 2px
            b_touch = bird_q_optimized(wing="fly_down", tuck_feet=False, lift=l_val, crest="normal", crest_style=crest_style)
            b_im = render_standard_legs(b_touch)
        elif bby == GY and w_mode == "fold":
            # 站定收翅 (frame 291): 恢复标准 27° 站立腿姿
            b_fold = bird_q_optimized(wing="fold", lift=l_val, crest="normal", crest_style=crest_style)
            b_im = render_standard_legs(b_fold)
        else:
            b_im = bird_q_optimized(wing=w_mode, tuck_feet=(bby < GY), lift=l_val, crest="high" if bby < GY else "normal", crest_style=crest_style)
        im.paste(b_im, (bcx - 53, bby - 72), b_im)
        frames.append(im)

    # 8.3: 平静站立在地面，红球已完全消失 (8 frames)
    for i in range(8):
        im = Image.new("RGBA", (CW, CH), (0, 0, 0, 0))
        d = ImageDraw.Draw(im)
        draw_play_ball_bird_shadow(d, 84, GY, width=28, alpha_factor=0.85)
        is_blinking = (2 <= i <= 5)
        b_base = bird_q_optimized(wing="fold", puff=1 if i < 4 else 0, eye="blink" if is_blinking else "open", crest="normal", tuck_feet=False, crest_style=crest_style)
        b_im = render_standard_legs(b_base)
        im.paste(b_im, (84 - 53, GY - 72), b_im)
        frames.append(im)

    return {f"play_ball_{idx}": img for idx, img in enumerate(frames)}

def build_suite_frames(crest_style="triple"):
    """Build all procedural animation frames using the specified crest_style ('classic' or 'triple')."""
    frames = {
        # 呼吸发呆
        "idle_0": bird_q_optimized(crest_style=crest_style),
        "idle_1": bird_q_optimized(eye="closed", crest_style=crest_style),
        "idle_2": bird_q_optimized(puff=1, head=(0, -1), crest="breath", crest_style=crest_style),
        
        # 左右摇摆外八字鸭子步
        "waddle_0": bird_q_optimized(crest_style=crest_style),
        "waddle_1": bird_q_optimized(step=1, head=(-2, 0), body_roll=-1, tail_wag=2, crest_style=crest_style),
        "waddle_2": bird_q_optimized(crest_style=crest_style),
        "waddle_3": bird_q_optimized(step=2, head=(1, 1), body_roll=1, tail_wag=-2, crest_style=crest_style),
        
        # 真实触地啄桌面与嚼食 - 闲置自然取食 (带地面金黄小米堆与进食咀嚼)
        "peck_0": render_true_ground_peck_frame(phase=0, crest_style=crest_style, with_grain=True),
        "peck_1": render_true_ground_peck_frame(phase=1, crest_style=crest_style, with_grain=True),
        "peck_2": render_true_ground_peck_frame(phase=2, crest_style=crest_style, with_grain=True),
        "peck_3": render_true_ground_peck_frame(phase=3, crest_style=crest_style, with_grain=True),
        "chew_0": bird_q_optimized(head=(-3, 3), crest_style=crest_style),
        "chew_1": bird_q_optimized(head=(-5, 4), mouth="bite", crumbs=True, crest_style=crest_style),
        
        # 兴奋连环双击啄桌面 (敲桌自嗨无谷物)
        "double_peck_0": render_true_ground_peck_frame(phase=0, crest_style=crest_style, with_grain=False),
        "double_peck_1": render_true_ground_peck_frame(phase=1, crest_style=crest_style, with_grain=False),
        "double_peck_2": render_true_ground_peck_frame(phase=2, crest_style=crest_style, with_grain=False),
        "double_peck_3": render_true_ground_peck_frame(phase=3, crest_style=crest_style, with_grain=False),
        
        # 蓬毛团子
        "fluff_0": bird_q_optimized(puff=3, eye="closed", crest="low", crest_style=crest_style),
        "fluff_1": bird_q_optimized(puff=5, eye="closed", crest="low", lift=-1, crest_style=crest_style),
        
        # 整理羽毛 (转头180°埋进背后羽毛细致啄理)
        "preen_0": render_preen_back_frame(phase=0, crest_style=crest_style),
        "preen_1": render_preen_back_frame(phase=1, crest_style=crest_style),
        "preen_2": render_preen_back_frame(phase=2, crest_style=crest_style),
        "preen_3": render_preen_back_frame(phase=3, crest_style=crest_style),
        
        # 求摸摸 (注入极致享受眯眯笑眼 ^_^)
        "bow_0": bird_q_optimized(head=(-5, 7), eye="closed", crest="low", crest_style=crest_style),
        "bow_1": bird_q_optimized(head=(-8, 13), eye="happy", crest="low", crest_style=crest_style),
        
        # 雀跃小跳 (4帧连环物理惯性跳跃: 蹲踞蓄力高耸 -> 腾空冲刺风阻后掠贴背 -> 落地触地回弹眯眼笑 -> 顺势回弹起立立正)
        "hop_0": bird_q_optimized(lift=2, body_roll=1, tail_wag=-1, head=(-2, 2), crest="alert", eye="open", step=0, tuck_feet=False, crest_style=crest_style),
        "hop_1": bird_q_optimized(lift=-9, body_roll=-4, tail_wag=5, head=(-4, -1), crest="low", eye="wide", step=0, tuck_feet=True, wing="heart", crest_style=crest_style),
        "hop_2": bird_q_optimized(lift=1, body_roll=-2, tail_wag=2, head=(-3, 3), crest="normal", eye="happy", puff=0, step=0, tuck_feet=False, crest_style=crest_style),
        "hop_3": bird_q_optimized(lift=-2, body_roll=-1, tail_wag=1, head=(0, 0), crest="alert", eye="open", step=0, tuck_feet=False, crest_style=crest_style),
        
        # 点头打节拍
        "bob_0": bird_q_optimized(head=(0, -2), crest_style=crest_style),
        "bob_1": bird_q_optimized(head=(-3, 6), crest_style=crest_style),
        
        # 心形翅膀
        "heart_wings_0": bird_q_optimized(wing="heart", crest_style=crest_style),
        "heart_wings_1": bird_q_optimized(wing="heart", head=(0, -1), crest_style=crest_style),
        
        # 唱歌独奏 (结合心形翅膀更蠢萌)
        "sing_0": bird_q_optimized(wing="heart", mouth="sing", note=1, crest="alert", crest_style=crest_style),
        "sing_1": bird_q_optimized(wing="heart", mouth="sing", note=2, head=(0, -1), crest="alert", crest_style=crest_style),
        "sing_2": bird_q_optimized(wing="heart", mouth="closed", head=(0, -1), crest_style=crest_style),
        
        # 警觉
        "alert_0": bird_q_optimized(head=(0, -4), crest="alert", eye="wide", crest_style=crest_style),
        
        # 敲击屏幕 (5帧物理冲击：迎风后掠、撞屏大甩鞭、余震反抽)
        "bonk_0": render_bonk_screen_frame(frame_idx=0, crest_style=crest_style),
        "bonk_1": render_bonk_screen_frame(frame_idx=1, crest_style=crest_style),
        "bonk_2": render_bonk_screen_frame(frame_idx=2, crest_style=crest_style),
        "bonk_3": render_bonk_screen_frame(frame_idx=3, crest_style=crest_style),
        "bonk_4": render_bonk_screen_frame(frame_idx=4, crest_style=crest_style),

        # 反咬受惊威慑 (以嘴巴为发散原点向前方辐射展开金黄三向音波)
        "bite_0": bird_q_optimized(head=(1, -2), body_roll=1, tail_wag=-1, crest="alert", eye="wide", mouth="closed", crest_style=crest_style),
        "bite_1": draw_mouth_radiating_sound(bird_q_optimized(head=(-1, -1), body_roll=-1, tail_wag=3, crest="alert", eye="wide", mouth="bite", crest_style=crest_style), mouth_origin=(15, 35), gap=4.5),
        "bite_2": draw_mouth_radiating_sound(bird_q_optimized(head=(0, 0), body_roll=-1, tail_wag=2, crest="alert", eye="wide", mouth="bite", crest_style=crest_style), mouth_origin=(16, 36), gap=4.5),
        "bite_3": bird_q_optimized(head=(-1, -1), body_roll=0, tail_wag=1, crest="alert", eye="wide", mouth="closed", crest_style=crest_style),
        
        # 哈气
        "hiss_0": bird_q_optimized(head=(-2, 2), puff=2, crest="alert", eye="wide", mouth="hiss", crest_style=crest_style),
        "hiss_1": bird_q_optimized(head=(-4, 4), puff=5, crest="alert", eye="wide", mouth="hiss", lift=-1, crest_style=crest_style),
        
        # 飞行 (4帧有机动力学扑翼：风阻流线羽冠、升力沉浮、柔韧折翼)
        "fly_0": render_bird_flight_custom(wing_phase=0, lift=-4, head=(-2, -1), tail_angle=0, crest_style=crest_style),
        "fly_1": render_bird_flight_custom(wing_phase=1, lift=-6, head=(-3, 0), tail_angle=2, crest_style=crest_style),
        "fly_2": render_bird_flight_custom(wing_phase=2, lift=-8, head=(-3, 0), tail_angle=1, crest_style=crest_style),
        "fly_3": render_bird_flight_custom(wing_phase=3, lift=-5, head=(-2, -1), tail_angle=0, crest_style=crest_style),
        
        # 母鸡蹲睡觉 (双脚彻底收进肚子里，软糖压扁)
        "sleep_0": sleeping_bird_q_optimized(puff=0, head=-1, zzz=1, crest_style=crest_style),
        "sleep_1": sleeping_bird_q_optimized(puff=2, head=0, zzz=2, crest_style=crest_style),
        "wake_0": sleeping_bird_q_optimized(puff=0, head=-1, crest_style=crest_style),
        "wake_1": bird_q_optimized(crest="alert", eye="wide", head=(0, -2), crest_style=crest_style),
    }
    # 30秒闲置杂技踩球 (300帧 260x120 高清像素舞台)
    frames.update(build_play_ball_frames(crest_style=crest_style))
    return frames

def generate_optimized_suite():
    # 1. 生成经典兔耳羽冠包 (Classic Rabbit-Ear)
    classic_frames = build_suite_frames(crest_style="classic")
    out_classic = Path(r"D:\pets\assets\sprites_classic")
    out_classic.mkdir(parents=True, exist_ok=True)
    out_new_classic = Path(r"D:\pets\2d-new\sprites_classic")
    out_new_classic.mkdir(parents=True, exist_ok=True)
    for name, img in classic_frames.items():
        img.save(out_classic / f"{name}.png")
        img.save(out_new_classic / f"{name}.png")
    print(f"Generated {len(classic_frames)} classic sprites in {out_classic}")

    # 2. 生成灵动三毛羽冠包 (Modern Triple-Tuft Recurve)
    triple_frames = build_suite_frames(crest_style="triple")
    out_triple = Path(r"D:\pets\assets\sprites_triple")
    out_triple.mkdir(parents=True, exist_ok=True)
    out_new_triple = Path(r"D:\pets\2d-new\sprites_triple")
    out_new_triple.mkdir(parents=True, exist_ok=True)
    for name, img in triple_frames.items():
        img.save(out_triple / f"{name}.png")
        img.save(out_new_triple / f"{name}.png")
    print(f"Generated {len(triple_frames)} triple sprites in {out_triple}")

    # 3. 默认将 classic (经典双叉兔耳羽冠) 写入生产 assets/sprites 与 2d-new/sprites
    assets_sprites = Path(r"D:\pets\assets\sprites")
    assets_sprites.mkdir(parents=True, exist_ok=True)
    for name, img in classic_frames.items():
        img.save(assets_sprites / f"{name}.png")
        img.save(OUT_NEW / f"{name}.png")
    print(f"Synced {len(classic_frames)} default classic sprites to {assets_sprites}")

    # Also copy original backup sprites for 1-to-1 comparison
    src_orig = Path(r"D:\pets\backup_original\assets\sprites")
    if src_orig.exists():
        for f in src_orig.glob("*.png"):
            img = Image.open(f)
            img.save(OUT_ORIG / f.name)

    print("Dual crest sprite suites generated successfully!")

if __name__ == "__main__":
    generate_optimized_suite()
