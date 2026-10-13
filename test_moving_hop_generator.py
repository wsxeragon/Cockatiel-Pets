"""Refined moving hop animation generator with inertia-driven crest dynamics.
Frame 0: Alert crest (prep)
Frame 1: Low crest flattened back by inertia & air resistance during leap!
Frame 2: Normal crest springing back on landing impact (touchdown & happy smile)
Frame 3: Alert crest fully restored (rebound)
"""
from pathlib import Path
from PIL import Image, ImageDraw
import shutil
import sys

sys.path.append(r"D:\pets\2d-new")
from generate_sprites_q_optimized import bird_q_optimized, C

OUT_DIR = Path(r"D:\pets\test_hop")
OUT_DIR.mkdir(parents=True, exist_ok=True)
ARTIFACT_DIR = Path(r"C:\Users\26893\.gemini\antigravity\brain\5df30705-c1cf-4a9e-883a-019811f74aae")

def build_refined_hop_suite():
    # 4 Key Frames:
    # Frame 0: 蹲踞蓄力 (Crouch / Squat Preparation)
    # 冠羽高耸竖立 (crest="alert")
    f0 = bird_q_optimized(
        lift=2,
        body_roll=1,
        tail_wag=-1,
        head=(-2, 2),
        crest="alert",
        eye="open",
        step=0,
        tuck_feet=False
    )

    # Frame 1: 腾空前跃 (Airborne Leap: crest flattened back by inertia!)
    # 冠羽因惯性与风阻顺滑贴脑后掠 (crest="low")！流线型小炮弹！
    f1 = bird_q_optimized(
        lift=-9,
        body_roll=-4,
        tail_wag=5,
        head=(-4, -1),
        crest="low",
        eye="wide",
        step=0,
        tuck_feet=True,
        wing="heart"
    )

    # Frame 2: 双脚触地缓冲 (Landing Touchdown: crest rebounds forward on impact)
    # 触地刹车冲击，冠羽顺着惯性向前弹起微弯 (crest="normal"), 眯眯笑眼 (^v^)
    f2 = bird_q_optimized(
        lift=1,
        body_roll=-2,
        tail_wag=2,
        head=(-3, 3),
        crest="normal",
        eye="happy",
        puff=0,
        step=0,
        tuck_feet=False
    )

    # Frame 3: 回弹顺势起立 (Rebound / Follow-through: alert crest restored)
    # 回弹直立，冠羽重新高耸竖起 (crest="alert")，准备接下一跳
    f3 = bird_q_optimized(
        lift=-2,
        body_roll=-1,
        tail_wag=1,
        head=(0, 0),
        crest="alert",
        eye="open",
        step=0,
        tuck_feet=False
    )

    frames = [f0, f1, f2, f3]

    # Save individual frames
    for idx, f in enumerate(frames):
        f.save(OUT_DIR / f"hop_move_{idx}.png")

    # Spritesheet (1x & 2x)
    sheet_w = 100 * 4
    sheet_h = 80
    sheet = Image.new("RGBA", (sheet_w, sheet_h), (255, 255, 255, 0))
    d_sheet = ImageDraw.Draw(sheet)
    for idx, f in enumerate(frames):
        ox = idx * 100
        sheet.paste(f, (ox, 0), f)
        if idx > 0:
            d_sheet.line([(ox, 0), (ox, sheet_h)], fill="#d5dae2", width=1)
    sheet.save(OUT_DIR / "hop_spritesheet.png")
    sheet_2x = sheet.resize((sheet_w * 2, sheet_h * 2), Image.NEAREST)
    sheet_2x.save(OUT_DIR / "hop_spritesheet_2x.png")

    # In-place Cycle GIF (3x)
    durations = [140, 180, 140, 120]
    scaled_cycle = [f.resize((300, 240), Image.NEAREST) for f in frames]
    scaled_cycle[0].save(
        OUT_DIR / "hop_cycle_3x.gif",
        save_all=True,
        append_images=scaled_cycle[1:],
        duration=durations,
        loop=0,
        disposal=2
    )

    # REAL MOVING SIMULATION GIF (2x):
    # Showing continuous happy hopping across screen:
    # 4 consecutive hops moving to the left, total distance = ~56px.
    sim_w, sim_h = 240, 90
    sim_frames = []
    sim_durations = []

    start_x = 135
    ground_y = 5

    base_canvas = Image.new("RGBA", (sim_w, sim_h), (246, 248, 250, 255))
    d_base = ImageDraw.Draw(base_canvas)
    d_base.line([(0, 77), (sim_w, 77)], fill="#d8dde4", width=1)

    # Start with standing idle pause
    idle_frame = base_canvas.copy()
    idle_frame.paste(frames[0], (start_x, ground_y), frames[0])
    sim_frames.append(idle_frame)
    sim_durations.append(350)

    cur_x = start_x
    for hop_idx in range(4):
        # Frame 0: Squat
        f_img = base_canvas.copy()
        f_img.paste(frames[0], (cur_x, ground_y), frames[0])
        sim_frames.append(f_img)
        sim_durations.append(120)

        # Frame 1: Mid-air peak (crest flattened back by inertia!)
        cur_x -= 8
        f_img = base_canvas.copy()
        f_img.paste(frames[1], (cur_x, ground_y), frames[1])
        sim_frames.append(f_img)
        sim_durations.append(160)

        # Frame 2: Landing impact (crest springs forward, advance 5px)
        cur_x -= 5
        f_img = base_canvas.copy()
        f_img.paste(frames[2], (cur_x, ground_y), frames[2])
        sim_frames.append(f_img)
        sim_durations.append(130)

        # Frame 3: Bounce recover (advance 2px)
        cur_x -= 2
        f_img = base_canvas.copy()
        f_img.paste(frames[3], (cur_x, ground_y), frames[3])
        sim_frames.append(f_img)
        sim_durations.append(110)

    # Final resting pause
    f_img = base_canvas.copy()
    f_img.paste(frames[0], (cur_x, ground_y), frames[0])
    sim_frames.append(f_img)
    sim_durations.append(500)

    scaled_sim = [sf.resize((sim_w * 2, sim_h * 2), Image.NEAREST) for sf in sim_frames]
    scaled_sim[0].save(
        OUT_DIR / "hop_moving_simulation_2x.gif",
        save_all=True,
        append_images=scaled_sim[1:],
        duration=sim_durations,
        loop=0,
        disposal=2
    )

    # Two-way (left & right) moving hop demonstration
    two_way_frames = []
    two_way_durations = []
    tw_w, tw_h = 240, 90
    tw_base = Image.new("RGBA", (tw_w, tw_h), (246, 248, 250, 255))
    d_tw = ImageDraw.Draw(tw_base)
    d_tw.line([(0, 77), (tw_w, 77)], fill="#d8dde4", width=1)

    # 1. Hop left 2 times
    cur_x = 100
    for hop_idx in range(2):
        for f_i, (f_img_base, dx, dur) in enumerate([(frames[0], 0, 120), (frames[1], -8, 160), (frames[2], -5, 130), (frames[3], -2, 110)]):
            cur_x += dx
            f_frame = tw_base.copy()
            f_frame.paste(f_img_base, (cur_x, ground_y), f_img_base)
            two_way_frames.append(f_frame)
            two_way_durations.append(dur)

    # Pause and turn around
    frames_right = [f.transpose(Image.FLIP_LEFT_RIGHT) for f in frames]
    pause_f = tw_base.copy()
    pause_f.paste(frames_right[0], (cur_x, ground_y), frames_right[0])
    two_way_frames.append(pause_f)
    two_way_durations.append(350)

    # 2. Hop right 2 times
    for hop_idx in range(2):
        for f_i, (f_img_base, dx, dur) in enumerate([(frames_right[0], 0, 120), (frames_right[1], 8, 160), (frames_right[2], 5, 130), (frames_right[3], 2, 110)]):
            cur_x += dx
            f_frame = tw_base.copy()
            f_frame.paste(f_img_base, (cur_x, ground_y), f_img_base)
            two_way_frames.append(f_frame)
            two_way_durations.append(dur)

    scaled_tw = [tf.resize((tw_w * 2, tw_h * 2), Image.NEAREST) for tf in two_way_frames]
    scaled_tw[0].save(
        OUT_DIR / "hop_two_way_demo_2x.gif",
        save_all=True,
        append_images=scaled_tw[1:],
        duration=two_way_durations,
        loop=0,
        disposal=2
    )

    # Copy all assets to artifact directory
    if ARTIFACT_DIR.exists():
        shutil.copy(OUT_DIR / "hop_spritesheet_2x.png", ARTIFACT_DIR / "hop_spritesheet_2x.png")
        shutil.copy(OUT_DIR / "hop_cycle_3x.gif", ARTIFACT_DIR / "hop_cycle_3x.gif")
        shutil.copy(OUT_DIR / "hop_moving_simulation_2x.gif", ARTIFACT_DIR / "hop_moving_simulation_2x.gif")
        shutil.copy(OUT_DIR / "hop_two_way_demo_2x.gif", ARTIFACT_DIR / "hop_two_way_demo_2x.gif")
        for idx in range(4):
            shutil.copy(OUT_DIR / f"hop_move_{idx}.png", ARTIFACT_DIR / f"hop_move_{idx}.png")
        print("Copied all inertial hop assets to artifact directory.")

    print("Refined moving hop suite complete!")

if __name__ == "__main__":
    build_refined_hop_suite()
