"""Q-Version Cockatiel Animation Optimization Suite.
Generates refined 100x80 procedural pixel sprites into D:\pets\2d-new\sprites.
"""
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
        
        # 啄地与拆家 (带打击回弹与喷溅碎屑)
        "peck_0": bird_q_optimized(head=(-3, 4)),
        "peck_1": bird_q_optimized(head=(-6, 12), tail_wag=2), # 触地顿挫尾巴弹起
        "chew_0": bird_q_optimized(head=(-3, 3)),
        "chew_1": bird_q_optimized(head=(-5, 4), mouth="bite", crumbs=True),
        
        # 蓬毛团子
        "fluff_0": bird_q_optimized(puff=3, eye="closed", crest="low"),
        "fluff_1": bird_q_optimized(puff=5, eye="closed", crest="low", lift=-1),
        
        # 整理羽毛
        "preen_0": bird_q_optimized(head=(4, 4), eye="closed"),
        "preen_1": bird_q_optimized(head=(7, 7), eye="closed"),
        
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
        
        # 反咬
        "bite_0": bird_q_optimized(head=(-8, -1), crest="alert", eye="wide", mouth="bite"),
        "bite_1": bird_q_optimized(head=(-3, 0), crest="alert", eye="wide", mouth="bite"),
        
        # 哈气
        "hiss_0": bird_q_optimized(head=(-2, 2), crest="alert", eye="wide", mouth="hiss"),
        
        # 飞行 (小短腿紧贴肚皮，3段流线型扑翼)
        "fly_0": bird_q_optimized(wing="fly_up", lift=-5, crest="alert", tuck_feet=True),
        "fly_1": bird_q_optimized(wing="fly_mid", lift=-5, crest="alert", tuck_feet=True),
        "fly_2": bird_q_optimized(wing="fly_down", lift=-7, crest="alert", tuck_feet=True),
        
        # 母鸡蹲睡觉 (双脚彻底收进肚子里，软糖压扁)
        "sleep_0": sleeping_bird_q_optimized(puff=0, head=-1, zzz=1),
        "sleep_1": sleeping_bird_q_optimized(puff=2, head=0, zzz=2),
        "wake_0": sleeping_bird_q_optimized(puff=0, head=-1),
        "wake_1": bird_q_optimized(crest="alert", eye="wide", head=(0, -2)),
    }
    
    # Save optimized sprites
    for name, img in frames.items():
        img.save(OUT_NEW / f"{name}.png")
    
    # Also copy original backup sprites for 1-to-1 comparison
    src_orig = Path(r"D:\pets\backup_original\assets\sprites")
    if src_orig.exists():
        for f in src_orig.glob("*.png"):
            img = Image.open(f)
            img.save(OUT_ORIG / f.name)

    print(f"Generated {len(frames)} optimized Q-version sprites in {OUT_NEW}")

if __name__ == "__main__":
    generate_optimized_suite()
