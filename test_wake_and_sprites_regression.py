import os
import sys
import time
from pathlib import Path
from PIL import Image

# Ensure project root is in sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from models import BehaviorType, BEHAVIOR_CATALOG, MoodDynamics
from PySide6.QtWidgets import QApplication

def test_models_definitions():
    wake_def = BEHAVIOR_CATALOG[BehaviorType.REST_WAKE]
    assert wake_def.is_looping is False, f"REST_WAKE is_looping should be False, got {wake_def.is_looping}"
    assert wake_def.frames == ["wake_0", "wake_1", "wake_2", "wake_3", "wake_4", "wake_5"], f"REST_WAKE frames mismatch: {wake_def.frames}"

    wake_curious_def = BEHAVIOR_CATALOG[BehaviorType.REST_WAKE_CURIOUS]
    assert wake_curious_def.is_looping is False, f"REST_WAKE_CURIOUS is_looping should be False, got {wake_curious_def.is_looping}"
    assert wake_curious_def.frames == ["wake_0", "wake_1", "wake_c_2", "wake_c_3", "wake_3", "wake_4", "wake_5"], f"REST_WAKE_CURIOUS frames mismatch: {wake_curious_def.frames}"

    fall_asleep_def = BEHAVIOR_CATALOG[BehaviorType.REST_FALL_ASLEEP]
    assert fall_asleep_def.is_looping is False, f"REST_FALL_ASLEEP is_looping should be False, got {fall_asleep_def.is_looping}"
    assert fall_asleep_def.frames == ["fall_asleep_0", "fall_asleep_1", "fall_asleep_2", "fall_asleep_3"], f"REST_FALL_ASLEEP frames mismatch: {fall_asleep_def.frames}"

    bite_def = BEHAVIOR_CATALOG[BehaviorType.FRIGHT_BITE]
    assert bite_def.is_looping is False, f"FRIGHT_BITE is_looping should be False, got {bite_def.is_looping}"

    fluff_def = BEHAVIOR_CATALOG[BehaviorType.COMFORT_FLUFF]
    assert fluff_def.frames == ["fluff_0", "fluff_1"], f"COMFORT_FLUFF frames mismatch: {fluff_def.frames}"
    assert fluff_def.frame_interval_ms == 900, f"COMFORT_FLUFF frame_interval_ms mismatch: {fluff_def.frame_interval_ms}"

    waddle_def = BEHAVIOR_CATALOG[BehaviorType.IDLE_WADDLE]
    assert waddle_def.frames == ["waddle_0", "waddle_1", "waddle_2", "waddle_3",
                                  "waddle_4", "waddle_5", "waddle_6", "waddle_7"], \
        f"IDLE_WADDLE frames mismatch: {waddle_def.frames}"
    assert waddle_def.frame_interval_ms == 120, f"IDLE_WADDLE frame_interval_ms mismatch: {waddle_def.frame_interval_ms}"
    print("PASS: test_models_definitions")

def test_wake_no_flicker_flow():
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)

    from cockatiel_window import CockatielWindow
    from unittest import mock

    pet = CockatielWindow()

    # 1. Force into sleep triggers REST_FALL_ASLEEP transition
    pet.force_sleep("测试进入睡眠")
    assert pet.current_behavior.code == BehaviorType.REST_FALL_ASLEEP
    assert pet.mood.fatigue == 100.0

    # Step through fall asleep frames -> enters REST_SLEEP
    for _ in range(3):
        pet.on_anim_frame_step()
    pet.on_anim_frame_step() # frame 3 finishes -> switches to REST_SLEEP
    assert pet.current_behavior.code == BehaviorType.REST_SLEEP

    # 2. Test Option 1: REST_WAKE (6 frames)
    with mock.patch("random.choice", return_value=BehaviorType.REST_WAKE):
        pet.clear_fatigue("测试清空疲劳 - 方案一")
    assert pet.mood.fatigue == 0.0
    assert pet.current_behavior.code == BehaviorType.REST_WAKE
    assert pet.current_frame_index == 0
    assert pet.current_behavior.frames[pet.current_frame_index] == "wake_0"

    # Step animation timer -> advances through 6 wake frames (0 -> 1 -> 2 -> 3 -> 4 -> 5)
    for expected_idx in range(1, 6):
        pet.on_anim_frame_step()
        assert pet.current_frame_index == expected_idx
        assert pet.current_behavior.frames[pet.current_frame_index] == f"wake_{expected_idx}"

    # Step animation timer again -> switches to IDLE_BLINK
    pet.on_anim_frame_step()
    assert pet.current_behavior.code == BehaviorType.IDLE_BLINK
    assert pet.current_frame_index == 0
    assert pet.current_behavior.frames[pet.current_frame_index] == "idle_0"

    # 3. Test Option 2: REST_WAKE_CURIOUS (7 frames)
    pet.force_sleep("测试进入睡眠2")
    for _ in range(4):
        pet.on_anim_frame_step()
    assert pet.current_behavior.code == BehaviorType.REST_SLEEP

    with mock.patch("random.choice", return_value=BehaviorType.REST_WAKE_CURIOUS):
        pet.wake_up("测试唤醒 - 方案二")
    assert pet.current_behavior.code == BehaviorType.REST_WAKE_CURIOUS
    assert pet.current_frame_index == 0
    assert len(pet.current_behavior.frames) == 7

    for expected_idx in range(1, 7):
        pet.on_anim_frame_step()
        assert pet.current_frame_index == expected_idx

    pet.on_anim_frame_step()
    assert pet.current_behavior.code == BehaviorType.IDLE_BLINK

    # 4. Test high fatigue (>= 90%) wake-up stays awake (does not instantly re-sleep on next tick)
    pet.force_sleep("测试进入高疲劳睡眠")
    for _ in range(4):
        pet.on_anim_frame_step()
    assert pet.current_behavior.code == BehaviorType.REST_SLEEP
    assert pet.mood.fatigue == 100.0

    # User clicks on sleeping pet
    from PySide6.QtCore import Qt, QPointF
    from PySide6.QtGui import QMouseEvent
    event = QMouseEvent(QMouseEvent.Type.MouseButtonPress, QPointF(50, 50), Qt.LeftButton, Qt.LeftButton, Qt.NoModifier)
    pet.mousePressEvent(event)
    assert pet.current_behavior.code in (BehaviorType.REST_WAKE, BehaviorType.REST_WAKE_CURIOUS)

    # Step through wake sequence
    for _ in range(len(pet.current_behavior.frames)):
        pet.on_anim_frame_step()
    assert pet.current_behavior.code == BehaviorType.IDLE_BLINK

    # Next tick MUST NOT force immediate sleep
    pet.on_main_tick()
    assert pet.current_behavior.code == BehaviorType.IDLE_BLINK, f"Must stay awake in IDLE_BLINK, got {pet.current_behavior.code}"
    assert pet.mood.fatigue <= 80.0, f"Fatigue should be lowered below threshold, got {pet.mood.fatigue}"

    pet.close()
    print("PASS: test_wake_no_flicker_flow")

def test_yawn_behavior_flow():
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)

    from cockatiel_window import CockatielWindow

    pet = CockatielWindow()

    # 1. Spontaneous selection exclusion test
    # COMFORT_YAWN and EXCITE_HEART_WINGS should never be selected directly by select_next_behavior
    for _ in range(50):
        chosen, _ = pet.mood.select_next_behavior()
        assert chosen.code != BehaviorType.COMFORT_YAWN, "COMFORT_YAWN should not be spontaneously selected!"
        assert chosen.code != BehaviorType.EXCITE_HEART_WINGS, "EXCITE_HEART_WINGS should not be spontaneously selected!"

    # 2. Trigger single yawn test (repeats=1)
    pet.trigger_yawn("测试单次伸脖打哈欠", repeats=1)
    assert pet.current_behavior.code == BehaviorType.COMFORT_YAWN
    assert pet.current_frame_index == 0
    assert pet.current_behavior.frames[pet.current_frame_index] == "yawn_0"
    assert pet.anim_timer.interval() == 280

    expected_intervals = [280, 220, 260, 450, 340, 240, 260, 300]
    for idx in range(1, 8):
        pet.on_anim_frame_step()
        assert pet.current_frame_index == idx
        assert pet.current_behavior.frames[idx] == f"yawn_{idx}"
        assert pet.anim_timer.interval() == expected_intervals[idx]

    # After frame 7 of the last repeat, transitions to IDLE_BLINK
    pet.on_anim_frame_step()
    assert pet.current_behavior.code == BehaviorType.IDLE_BLINK, f"Expected IDLE_BLINK, got {pet.current_behavior.code}"
    assert pet.current_frame_index == 0

    # 3. Multi-yawn test (repeats=3)
    pet.trigger_yawn("测试连打3次哈欠", repeats=3)
    assert pet.yawn_remaining_repeats == 3
    for r in range(3):
        # Round r: step through frames 1..7
        for idx in range(1, 8):
            pet.on_anim_frame_step()
            assert pet.current_frame_index == idx
        # Step off frame 7
        pet.on_anim_frame_step()
        if r < 2:
            assert pet.current_behavior.code == BehaviorType.COMFORT_YAWN, f"Round {r} should loop to next yawn"
            assert pet.current_frame_index == 0
            assert pet.yawn_remaining_repeats == (2 - r)
        else:
            assert pet.current_behavior.code == BehaviorType.IDLE_BLINK, "Final round should transition to IDLE_BLINK"
            assert pet.yawn_remaining_repeats == 0

    # 4. Post-preen 30% trigger test
    # (a) When random.random() < 0.30 -> triggers yawn with 3-5 repeats
    pet.switch_behavior(BEHAVIOR_CATALOG[BehaviorType.COMFORT_PREEN], 10.0)
    pet.action_end_time = time.time() - 0.1
    import unittest.mock as mock
    with mock.patch("random.random", return_value=0.25):
        pet.on_main_tick()
    assert pet.current_behavior.code == BehaviorType.COMFORT_YAWN
    assert 3 <= pet.yawn_remaining_repeats <= 5

    # (b) When random.random() >= 0.30 -> does NOT trigger yawn
    pet.switch_behavior(BEHAVIOR_CATALOG[BehaviorType.COMFORT_PREEN], 10.0)
    pet.action_end_time = time.time() - 0.1
    with mock.patch("random.random", return_value=0.50):
        pet.on_main_tick()
    assert pet.current_behavior.code != BehaviorType.COMFORT_YAWN

    pet.close()
    print("PASS: test_yawn_behavior_flow")

def test_waddle_dual_mode_behavior():
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)

    from cockatiel_window import CockatielWindow

    pet = CockatielWindow()

    # 1. Switch into IDLE_WADDLE initializes mode and direction
    pet.switch_behavior(BEHAVIOR_CATALOG[BehaviorType.IDLE_WADDLE], 100.0)
    assert pet.current_behavior.code == BehaviorType.IDLE_WADDLE
    assert pet.waddle_mode in ("origin_pacing", "straight_to_edge")
    assert pet.waddle_direction in (-1, 1)
    assert pet.waddle_consecutive_steps == 0
    assert pet.waddle_origin_x == pet.x()

    # 2. Test origin_pacing: turning probability increases with steps
    pet.waddle_mode = "origin_pacing"
    pet.waddle_direction = 1
    pet.facing_direction = 1
    pet.waddle_consecutive_steps = 20

    # Steps <= 35: does not turn around
    import unittest.mock as mock
    with mock.patch("random.random", return_value=0.0001):
        pet.on_main_tick()
    assert pet.waddle_direction == 1, "Should not turn when consecutive steps <= 35"

    # Steps > 35: with turn_prob met, turns around and resets consecutive steps
    pet.waddle_consecutive_steps = 90
    with mock.patch("random.random", return_value=0.05):
        pet.on_main_tick()
    assert pet.waddle_direction == -1, "Should turn around when turn probability threshold is met"
    assert pet.waddle_consecutive_steps == 0

    # 3. Test straight_to_edge mode: hitting boundary with high excitement triggers bonk
    pet.waddle_mode = "straight_to_edge"
    rect = pet.get_screen_rect(use_available=True)
    pet.move(rect.left() + 26, pet.y()) # 1 step from min_waddle_x
    pet.waddle_direction = -1
    pet.facing_direction = -1
    pet.mood.excitement = 90.0 # High excitement
    pet.mood.fright = 0.0

    with mock.patch("random.random", return_value=0.10): # below bonk_prob (approx 0.87)
        pet.on_main_tick()
    assert pet.current_behavior.code == BehaviorType.EXCITE_BONK, "High excitement at edge should trigger bonk!"

    # 4. Test hitting boundary with low excitement / no bonk -> turns around and walks back
    pet.switch_behavior(BEHAVIOR_CATALOG[BehaviorType.IDLE_WADDLE], 100.0)
    pet.waddle_mode = "straight_to_edge"
    pet.move(rect.left() + 26, pet.y())
    pet.waddle_direction = -1
    pet.facing_direction = -1
    pet.mood.excitement = 10.0 # Low excitement

    with mock.patch("random.random", return_value=0.99): # above bonk_prob -> turns back
        pet.on_main_tick()
    assert pet.current_behavior.code == BehaviorType.IDLE_WADDLE
    assert pet.waddle_direction == 1, "Should turn around away from edge when not bonking"

    pet.close()
    print("PASS: test_waddle_dual_mode_behavior")

def test_sprite_integrity():
    required_sprites = [
        "peck_0", "peck_1", "peck_2", "peck_3",
        "bite_0", "bite_1", "bite_2", "bite_3",
        "bonk_0", "bonk_1", "bonk_2", "bonk_3", "bonk_4",
        "wake_0", "wake_1", "wake_2", "wake_3", "wake_4", "wake_5",
        "wake_c_2", "wake_c_3",
        "fall_asleep_0", "fall_asleep_1", "fall_asleep_2", "fall_asleep_3",
        "sleep_0", "sleep_1",
        "preen_0", "preen_1", "preen_2", "preen_3",
        "yawn_0", "yawn_1", "yawn_2", "yawn_3", "yawn_4", "yawn_5", "yawn_6", "yawn_7",
        "waddle_0", "waddle_1", "waddle_2", "waddle_3", "waddle_4", "waddle_5",
        "fluff_0", "fluff_1"
    ]

    for s in required_sprites:
        p_assets = Path("assets/sprites") / f"{s}.png"
        p_classic = Path("assets/sprites_classic") / f"{s}.png"
        p_triple = Path("assets/sprites_triple") / f"{s}.png"
        p_2d = Path("2d-new/sprites") / f"{s}.png"
        assert p_assets.exists(), f"Missing {p_assets}"
        assert p_classic.exists(), f"Missing {p_classic}"
        assert p_triple.exists(), f"Missing {p_triple}"
        assert p_2d.exists(), f"Missing {p_2d}"

        img_a = Image.open(p_assets)
        img_c = Image.open(p_classic)
        img_t = Image.open(p_triple)
        img_2 = Image.open(p_2d)
        assert img_a.size == (100, 80), f"Size mismatch for {p_assets}: {img_a.size}"
        assert img_c.size == (100, 80), f"Size mismatch for {p_classic}: {img_c.size}"
        assert img_t.size == (100, 80), f"Size mismatch for {p_triple}: {img_t.size}"
        assert img_2.size == (100, 80), f"Size mismatch for {p_2d}: {img_2.size}"

    # The active runtime sets (classic/triple) use the new 8-frame walk and
    # the relayered idle blink/relaxed/breath-down variants.
    for s in ("waddle_6", "waddle_7",
              "idle_0", "idle_1", "idle_2",
              "idle_0_dn", "idle_1_dn", "idle_2_dn"):
        for d in ("assets/sprites_classic", "assets/sprites_triple"):
            p = Path(d) / f"{s}.png"
            assert p.exists(), f"Missing {p}"
            img = Image.open(p)
            assert img.size == (100, 80), f"Size mismatch for {p}: {img.size}"

    # Verify play_ball start, landing cushion, and ending frames align with 27-deg standing stance
    for d in ("assets/sprites_classic", "assets/sprites_triple"):
        idle = Image.open(Path(d) / "idle_0.png").convert("RGBA")
        pb0 = Image.open(Path(d) / "play_ball_0.png").convert("RGBA")
        pb290 = Image.open(Path(d) / "play_ball_290.png").convert("RGBA")
        pb299 = Image.open(Path(d) / "play_ball_299.png").convert("RGBA")
        assert pb0.size == (260, 120), f"Size mismatch for play_ball_0 in {d}"
        assert pb290.size == (260, 120), f"Size mismatch for play_ball_290 in {d}"
        assert pb299.size == (260, 120), f"Size mismatch for play_ball_299 in {d}"

        # 1. Entry frame 0 bird matches idle_0 at (122, 26)
        crop_pb0 = pb0.crop((122, 26, 222, 106))
        diff_0 = sum(1 for y in range(80) for x in range(100) if idle.getpixel((x, y))[3] > 0 and crop_pb0.getpixel((x, y)) != idle.getpixel((x, y)))
        assert diff_0 == 0, f"play_ball_0 bird pixels mismatch idle_0 in {d}: {diff_0}"

        # 2. Touchdown frame 290 has grounded feet pixels at contact level
        crop_pb290 = pb290.crop((31, 26, 131, 106))
        feet_290 = sum(1 for x in range(35, 65) if crop_pb290.getpixel((x, 73))[3] > 0)
        assert feet_290 > 0, f"play_ball_290 missing grounded cushion feet in {d}"

        # 3. Exit frame 299 bird matches idle_0 at (31, 26)
        crop_pb299 = pb299.crop((31, 26, 131, 106))
        diff_299 = sum(1 for y in range(80) for x in range(100) if idle.getpixel((x, y))[3] > 0 and crop_pb299.getpixel((x, y)) != idle.getpixel((x, y)))
        assert diff_299 == 0, f"play_ball_299 bird pixels mismatch idle_0 in {d}: {diff_299}"

    print("PASS: test_sprite_integrity")

def test_head_chin_hit_zone():
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)

    from cockatiel_window import CockatielWindow
    from PySide6.QtCore import QPoint
    from PySide6.QtGui import QMouseEvent
    from PySide6.QtCore import Qt

    pet = CockatielWindow()

    # 1. 待机状态 (面向左 facing_direction == -1)
    pet.switch_behavior(BEHAVIOR_CATALOG[BehaviorType.IDLE_BLINK], 10.0)
    pet.facing_direction = -1

    # 头部与下巴/喉部正向用例 (必须判定为 True)
    assert pet.is_head_neck_zone(QPoint(24, 45)), "下巴点 (24, 45) 应该判定为头颈可摸区域"
    assert pet.is_head_neck_zone(QPoint(22, 42)), "嘴壳下沿 (22, 42) 应该判定为头颈可摸区域"
    assert pet.is_head_neck_zone(QPoint(26, 48)), "下巴下缘 (26, 48) 应该判定为头颈可摸区域"
    assert pet.is_head_neck_zone(QPoint(30, 50)), "喉部前侧 (30, 50) 应该判定为头颈可摸区域"
    assert pet.is_head_neck_zone(QPoint(35, 20)), "羽冠部位 (35, 20) 应该判定为头颈可摸区域"
    assert pet.is_head_neck_zone(QPoint(28, 30)), "眼眶额头 (28, 30) 应该判定为头颈可摸区域"
    assert pet.is_head_neck_zone(QPoint(20, 36)), "嘴壳中央 (20, 36) 应该判定为头颈可摸区域"
    assert pet.is_head_neck_zone(QPoint(36, 38)), "腮红脸颊 (36, 38) 应该判定为头颈可摸区域"
    assert pet.is_head_neck_zone(QPoint(48, 35)), "后颈上方 (48, 35) 应该判定为头颈可摸区域"

    # 躯干禁区反向用例 (必须判定为 False，触发戳身子生气)
    assert not pet.is_head_neck_zone(QPoint(65, 40)), "背部羽毛 (65, 40) 应该是身体禁区"
    assert not pet.is_head_neck_zone(QPoint(60, 52)), "翅膀中段 (60, 52) 应该是身体禁区"
    assert not pet.is_head_neck_zone(QPoint(80, 55)), "尾羽部位 (80, 55) 应该是身体禁区"
    assert not pet.is_head_neck_zone(QPoint(45, 65)), "腹部下方 (45, 65) 应该是身体禁区"

    # 2. 镜像朝右状态 (facing_direction == 1)
    pet.facing_direction = 1
    # 朝右时，下巴镜像位置在 100 - 1 - 24 = 75
    assert pet.is_head_neck_zone(QPoint(75, 45)), "朝右时下巴点 (75, 45) 应该判定为头颈可摸区域"
    assert pet.is_head_neck_zone(QPoint(73, 48)), "朝右时下巴点 (73, 48) 应该判定为头颈可摸区域"
    # 朝右时，背部镜像位置在 100 - 1 - 65 = 34
    assert not pet.is_head_neck_zone(QPoint(34, 40)), "朝右时背部 (34, 40) 应该是身体禁区"
    assert not pet.is_head_neck_zone(QPoint(39, 52)), "朝右时翅膀 (39, 52) 应该是身体禁区"

    # 3. 低头享受姿态 (COMFORT_BOW): 头部深低前探
    pet.facing_direction = -1
    pet.switch_behavior(BEHAVIOR_CATALOG[BehaviorType.COMFORT_BOW], 4.0)
    assert pet.is_head_neck_zone(QPoint(18, 48)), "低头姿势下巴 (18, 48) 应该判定为头颈可摸区域"
    assert pet.is_head_neck_zone(QPoint(22, 54)), "低头姿势喉咙 (22, 54) 应该判定为头颈可摸区域"
    assert pet.is_head_neck_zone(QPoint(26, 56)), "低头姿势喉部下段 (26, 56) 应该判定为头颈可摸区域"
    assert not pet.is_head_neck_zone(QPoint(60, 45)), "低头姿势背部 (60, 45) 应该是身体禁区"

    # 4. 真实点击事件交互流测试
    # 4.1 点击下巴 (28, 45 为下巴可视羽毛) -> 触发摸头享受 (COMFORT_BOW)
    pet.switch_behavior(BEHAVIOR_CATALOG[BehaviorType.IDLE_BLINK], 10.0)
    pet.facing_direction = -1
    chin_event = QMouseEvent(QMouseEvent.Type.MouseButtonPress, QPoint(28, 45), Qt.LeftButton, Qt.LeftButton, Qt.NoModifier)
    pet.mousePressEvent(chin_event)
    assert pet.current_behavior.code == BehaviorType.COMFORT_BOW, f"点击下巴应触发 COMFORT_BOW，实际为 {pet.current_behavior.code}"
    assert pet.head_pet_active is True, "摸头后应标记 head_pet_active 为 True"
    assert pet.head_pet_count == 1, "摸头 1 次计数应为 1"
    assert abs(pet.get_head_pet_preen_prob() - 0.20) < 1e-5, "摸头 1 次理毛概率应为 20%"

    # 4.2 点击背部 -> 触发戳身子生气反击 (FRIGHT_BITE)
    pet.switch_behavior(BEHAVIOR_CATALOG[BehaviorType.IDLE_BLINK], 10.0)
    body_event = QMouseEvent(QMouseEvent.Type.MouseButtonPress, QPoint(65, 40), Qt.LeftButton, Qt.LeftButton, Qt.NoModifier)
    pet.mousePressEvent(body_event)
    assert pet.current_behavior.code == BehaviorType.FRIGHT_BITE, f"戳背部应触发 FRIGHT_BITE，实际为 {pet.current_behavior.code}"

    pet.close()
    print("PASS: test_head_chin_hit_zone")

def test_sleep_unmirrored_z_both_directions():
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)

    from cockatiel_window import CockatielWindow

    pet = CockatielWindow()

    # 1. 验证素材完整性：sleep_0_r 和 sleep_1_r 必须在所有装扮目录存在且为 100x80
    for s in ["sleep_0_r", "sleep_1_r"]:
        for d in ["assets/sprites", "assets/sprites_classic", "assets/sprites_triple", "2d-new/sprites"]:
            p = Path(d) / f"{s}.png"
            assert p.exists(), f"缺少右朝向睡觉精灵帧: {p}"
            img = Image.open(p)
            assert img.size == (100, 80), f"尺寸不符合 100x80: {p} 为 {img.size}"

    # 2. 验证左朝向睡觉
    pet.switch_behavior(BEHAVIOR_CATALOG[BehaviorType.REST_SLEEP], 10.0)
    pet.facing_direction = -1
    pix_left = pet.get_current_pixmap()
    assert not pix_left.isNull(), "左朝向睡觉 Pixmap 不应为空"

    # 3. 验证右朝向睡觉：必须取到 sleep_0_r / sleep_1_r，且 Z 字符正向（非反向镜像 Ƶ）
    pet.facing_direction = 1
    pix_right = pet.get_current_pixmap()
    assert not pix_right.isNull(), "右朝向睡觉 Pixmap 不应为空"

    # 检查返回图像中大 Z 对角线的斜率方向：正向 Z 的对角线自右上向左下倾斜 (y 越小 x 越大)
    qimg = pix_right.toImage()
    # 大 Z 位于 x 在 14..24 之间，y 在 5..15 之间
    y8_xs = [x for x in range(14, 24) if qimg.pixelColor(x, 8).alpha() > 100]
    y11_xs = [x for x in range(14, 24) if qimg.pixelColor(x, 11).alpha() > 100]
    assert len(y8_xs) > 0 and len(y11_xs) > 0, "右朝向大 Z 应有实体像素"
    assert min(y8_xs) > min(y11_xs), f"Z 字符必须保持正向！y=8 的对角线起点({min(y8_xs)})应大于 y=11 的对角线终点({min(y11_xs)})"

    pet.close()
    print("PASS: test_sleep_unmirrored_z_both_directions")

def test_head_pet_probabilistic_preen_flow():
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)

    from cockatiel_window import CockatielWindow
    import unittest.mock as mock

    pet = CockatielWindow()

    # 1. 验证梯度递增概率公式：点1下20%, 点2下30%, 点3下40%... 9下及以上100%
    pet.head_pet_count = 0
    assert pet.get_head_pet_preen_prob() == 0.0
    pet.head_pet_count = 1
    assert abs(pet.get_head_pet_preen_prob() - 0.20) < 1e-5
    pet.head_pet_count = 2
    assert abs(pet.get_head_pet_preen_prob() - 0.30) < 1e-5
    pet.head_pet_count = 3
    assert abs(pet.get_head_pet_preen_prob() - 0.40) < 1e-5
    pet.head_pet_count = 4
    assert abs(pet.get_head_pet_preen_prob() - 0.50) < 1e-5
    pet.head_pet_count = 9
    assert abs(pet.get_head_pet_preen_prob() - 1.00) < 1e-5
    pet.head_pet_count = 12
    assert abs(pet.get_head_pet_preen_prob() - 1.00) < 1e-5

    # 2. 模拟连续点击摸头 3 次
    pet.head_pet_count = 0
    pet.handle_pet_head()
    assert pet.head_pet_count == 1
    assert pet.current_behavior.code == BehaviorType.COMFORT_BOW
    assert pet.head_pet_active is True
    assert abs(pet.get_head_pet_preen_prob() - 0.20) < 1e-5

    pet.handle_pet_head()
    assert pet.head_pet_count == 2
    assert abs(pet.get_head_pet_preen_prob() - 0.30) < 1e-5

    pet.handle_pet_head()
    assert pet.head_pet_count == 3
    assert abs(pet.get_head_pet_preen_prob() - 0.40) < 1e-5

    # 3. 验证命中理毛分支 (random < 0.40 时触发理毛)
    assert "概率" not in pet.last_feedback and "%" not in pet.last_feedback, "摸头反馈中不应暴露概率信息"
    pet.action_end_time = time.time() - 0.1
    with mock.patch("random.random", return_value=0.35):
        pet.on_main_tick()
    assert pet.current_behavior.code == BehaviorType.COMFORT_PREEN, "命中概率应触发转头理毛"
    assert pet.head_pet_active is False, "触发理毛后 head_pet_active 应清空"
    assert pet.head_pet_count == 0, "触发理毛后摸头累计应清零"
    assert "概率" not in pet.last_feedback and "%" not in pet.last_feedback, "理毛触发反馈中不应暴露概率信息"

    # 4. 验证未命中理毛分支 (点1下 20%，random >= 0.20 时不触发理毛，转入发呆)
    pet.switch_behavior(BEHAVIOR_CATALOG[BehaviorType.IDLE_BLINK], 10.0)
    pet.handle_pet_head()
    assert pet.head_pet_count == 1
    assert abs(pet.get_head_pet_preen_prob() - 0.20) < 1e-5
    assert "概率" not in pet.last_feedback and "%" not in pet.last_feedback, "摸头反馈中不应暴露概率信息"

    pet.action_end_time = time.time() - 0.1
    with mock.patch("random.random", return_value=0.25):
        pet.on_main_tick()
    assert pet.current_behavior.code == BehaviorType.IDLE_BLINK, "未命中理毛应平稳切入发呆站立"
    assert pet.head_pet_active is False, "摸头后单次动作判定完毕，head_pet_active 必须置为 False"
    assert "概率" not in pet.last_feedback and "%" not in pet.last_feedback, "未触发理毛反馈中不应暴露概率信息"

    # 5. 验证“该概率只影响摸头后的下一个动作”：后续自主轮转不受影响
    pet.action_end_time = time.time() - 0.1
    with mock.patch("random.random", return_value=0.01):
        pet.on_main_tick()
    assert pet.head_pet_active is False

    # 6. 验证戳身体清零摸头计数
    pet.handle_pet_head()
    assert pet.head_pet_count > 0
    pet.handle_touch_body()
    assert pet.head_pet_count == 0
    assert pet.head_pet_active is False

    pet.close()
    print("PASS: test_head_pet_probabilistic_preen_flow")

def test_updater_version_and_integration():
    import updater
    from config import APP_VERSION

    # 1. 验证版本号纯数字定义（无 V 前缀）
    assert APP_VERSION == "0.0.9", f"APP_VERSION should be '0.0.9', got {APP_VERSION}"
    assert not APP_VERSION.lower().startswith("v"), "APP_VERSION must NOT start with 'v' or 'V'!"

    # 2. 验证多形态版本号解析与比较（严格去除 V / v，纯数字比较）
    assert updater.normalize_version("V0.0.7") == (0, 0, 7)
    assert updater.normalize_version("0.0.7") == (0, 0, 7)
    assert updater.normalize_version("v0.0.6") == (0, 0, 6)
    assert updater.normalize_version("V0.0.10") == (0, 0, 10)
    assert updater.is_newer_version("V0.0.7", "0.0.7") is False
    assert updater.is_newer_version("0.0.7", "0.0.7") is False
    assert updater.is_newer_version("V0.0.6", "0.0.7") is False
    assert updater.is_newer_version("V0.0.8", "0.0.7") is True
    assert updater.is_newer_version("0.0.8", "0.0.7") is True
    assert updater.is_newer_version("V0.1.0", "0.0.7") is True
    assert updater.is_newer_version("V1.0.0", "0.0.7") is True

    # 3. 验证窗口集成
    app = QApplication.instance()
    if not app:
        app = QApplication(sys.argv)
    from cockatiel_window import CockatielWindow
    win = CockatielWindow()
    assert hasattr(win, "check_for_updates"), "CockatielWindow must have check_for_updates"
    assert hasattr(win, "on_check_update_finished"), "CockatielWindow must have on_check_update_finished"
    assert hasattr(win, "start_download_update"), "CockatielWindow must have start_download_update"
    win.close()

    # 4. 验证智能选包策略与大小提前比对逻辑 (select_best_release_asset)
    # 场景 A: 典型发布 (增量 Patch 4.5MB vs 全量 54MB) -> 极速增量优先
    assets_standard = [
        {"name": "Cockatiel-Pets-v0.0.7-Patch-x64.zip", "size": 4791992, "browser_download_url": "http://patch.zip"},
        {"name": "Cockatiel-Pets-v0.0.7-Full-Setup.zip", "size": 56668160, "browser_download_url": "http://full.zip"},
    ]
    target, pkg_type, reason = updater.select_best_release_asset(assets_standard)
    assert pkg_type == "patch"
    assert target["name"] == "Cockatiel-Pets-v0.0.7-Patch-x64.zip"
    assert "节省约" in reason

    # 场景 B: 增量膨胀达 80% 阈值 (增量 45MB vs 全量 50MB) -> 自动熔断选择全量包
    assets_bloated_patch = [
        {"name": "Cockatiel-Pets-v0.0.8-Patch-x64.zip", "size": 45 * 1024 * 1024, "browser_download_url": "http://patch.zip"},
        {"name": "Cockatiel-Pets-v0.0.8-Full-Setup.zip", "size": 50 * 1024 * 1024, "browser_download_url": "http://full.zip"},
    ]
    target, pkg_type, reason = updater.select_best_release_asset(assets_bloated_patch)
    assert pkg_type == "full", f"Expected full package due to 80% threshold, got {pkg_type}"
    assert target["name"] == "Cockatiel-Pets-v0.0.8-Full-Setup.zip"
    assert "80%" in reason

    # 场景 C: 增量包异常大于全量包 (增量 60MB vs 全量 50MB) -> 自动切换全量包
    assets_larger_patch = [
        {"name": "Cockatiel-Pets-v0.0.8-Patch-x64.zip", "size": 60 * 1024 * 1024, "browser_download_url": "http://patch.zip"},
        {"name": "Cockatiel-Pets-v0.0.8-Full-Setup.zip", "size": 50 * 1024 * 1024, "browser_download_url": "http://full.zip"},
    ]
    target, pkg_type, reason = updater.select_best_release_asset(assets_larger_patch)
    assert pkg_type == "full"
    assert target["name"] == "Cockatiel-Pets-v0.0.8-Full-Setup.zip"
    assert "大于或等于全量包" in reason

    # 场景 D: 仅提供全量包
    assets_only_full = [
        {"name": "Cockatiel-Pets-v0.0.8-Full-Setup.zip", "size": 50 * 1024 * 1024, "browser_download_url": "http://full.zip"},
    ]
    target, pkg_type, reason = updater.select_best_release_asset(assets_only_full)
    assert pkg_type == "full"
    assert target["name"] == "Cockatiel-Pets-v0.0.8-Full-Setup.zip"

    # 场景 E: 仅提供补丁包 (兼容通用名与版本化命名)
    assets_only_patch = [
        {"name": "Cockatiel-Pets-v0.0.7-Patch-x64.zip", "size": 4 * 1024 * 1024, "browser_download_url": "http://patch.zip"},
    ]
    target, pkg_type, reason = updater.select_best_release_asset(assets_only_patch)
    assert pkg_type == "patch"
    assert target["name"] == "Cockatiel-Pets-v0.0.7-Patch-x64.zip"

    print("PASS: test_updater_version_and_integration")

def test_poop_behavior_flow():
    """验证大小便行为动力学、大便悬浮窗物理下落与清理动效、配置持久化与右键禁用"""
    from models import BehaviorType, BEHAVIOR_CATALOG
    from config import is_poop_disabled, set_poop_disabled
    from poop_item_window import PoopItemWindow

    # 1. 模型目录完整性与帧参数定义
    assert BehaviorType.POOP in BEHAVIOR_CATALOG
    poop_def = BEHAVIOR_CATALOG[BehaviorType.POOP]
    assert len(poop_def.frames) == 14
    assert poop_def.is_interruptible is False
    assert poop_def.is_looping is False
    assert len(poop_def.frame_intervals_ms) == 14

    # 2. 静态像素资产尺寸与马赛克格式检查 (16x14 紧凑马赛克大便)
    poop_asset_dir = Path("assets/poop")
    expected_sizes = {
        "poop_idle": (16, 14),
        "poop_fall": (14, 16),
        "poop_land": (18, 12),
        "poop_clean_0": (24, 20),
        "poop_clean_1": (24, 20),
        "poop_clean_2": (24, 20),
        "poop_clean_3": (24, 20),
    }
    for name, expected_size in expected_sizes.items():
        p = poop_asset_dir / f"{name}.png"
        assert p.exists(), f"Missing poop asset: {p}"
        img = Image.open(p)
        assert img.size == expected_size, f"Size mismatch for {p}: expected {expected_size}, got {img.size}"

    for idx in range(14):
        for sdir in ["assets/sprites", "assets/sprites_classic", "assets/sprites_triple"]:
            sp = Path(sdir) / f"poop_{idx}.png"
            assert sp.exists(), f"Missing bird poop frame: {sp}"
            simg = Image.open(sp)
            assert simg.size == (100, 80), f"Size mismatch for {sp}: {simg.size}"

    # 3. 实体交互与下落物理测试
    app = QApplication.instance() or QApplication(sys.argv)
    from cockatiel_window import CockatielWindow

    pet = CockatielWindow()
    # 确保测试前重置为允许排泄
    set_poop_disabled(False)
    pet.is_poop_disabled = False

    # 触发后退深蹲排便
    res = pet.trigger_poop("测试触发排便")
    assert res is True
    assert pet.current_behavior.code == BehaviorType.POOP
    assert pet.current_frame_index == 0

    # 步进前 8 帧，验证尚未掉落
    initial_poop_count = len(pet.active_poops)
    for _ in range(8):
        pet.on_anim_frame_step()
    assert pet.current_frame_index == 8
    assert len(pet.active_poops) == initial_poop_count

    # 步进至第 9 帧 (泄殖腔释放瞬间，生成大便实体悬浮窗)
    pet.on_anim_frame_step()
    assert pet.current_frame_index == 9
    assert len(pet.active_poops) == initial_poop_count + 1
    spawned_poop = pet.active_poops[-1]
    assert isinstance(spawned_poop, PoopItemWindow)
    assert spawned_poop.isVisible()

    # 步进至动作播放完毕，平稳收尾切出至 IDLE_BLINK
    for _ in range(4): # frames 10, 11, 12, 13
        pet.on_anim_frame_step()
    pet.on_anim_frame_step() # 结束切出
    assert pet.current_behavior.code == BehaviorType.IDLE_BLINK
    assert "轻松舒爽" in pet.last_feedback

    # 4. 验证点击清理动画
    cleaned_signals = []
    spawned_poop.cleaned.connect(lambda obj: cleaned_signals.append(obj))
    spawned_poop.start_cleanup()
    assert spawned_poop.state == "clean"
    # 模拟 4 帧清理闪烁
    for _ in range(4):
        spawned_poop._on_clean_tick()
    assert len(cleaned_signals) == 1
    assert spawned_poop not in pet.active_poops

    # 5. 验证禁止大小便开关与持久化
    pet.toggle_disable_poop()
    assert pet.is_poop_disabled is True
    assert is_poop_disabled() is True
    assert not pet.poop_timer.isActive()

    # 禁止后无法触发排便
    assert pet.trigger_poop("禁止后尝试排便") is False
    assert pet.current_behavior.code == BehaviorType.IDLE_BLINK

    # 再次切换恢复为允许排泄
    pet.toggle_disable_poop()
    assert pet.is_poop_disabled is False
    assert is_poop_disabled() is False
    assert pet.poop_timer.isActive()

    # 6. 验证排便概率模型：前30分钟严格为0，30~60分钟从0线性增长至100%
    now_t = time.time()
    # 模拟刚排便完成 (t=0)
    pet.last_poop_time = now_t
    assert pet.get_poop_probability() == 0.0

    # 模拟前 15 分钟 (900秒) -> 概率依然为 0
    pet.last_poop_time = now_t - 900.0
    assert pet.get_poop_probability() == 0.0

    # 模拟第 29.5 分钟 (1770秒) -> 概率依然为 0
    pet.last_poop_time = now_t - 1770.0
    assert pet.get_poop_probability() == 0.0

    # 模拟恰好 30 分钟 (1800秒) -> 概率为 0.0 (微秒时间戳浮动容差)
    pet.last_poop_time = time.time() - 1800.0
    assert pet.get_poop_probability() < 1e-3

    # 模拟 37.5 分钟 (2250秒，即 30~60 分钟的 25% 进度) -> 概率为 0.25
    pet.last_poop_time = now_t - 2250.0
    assert abs(pet.get_poop_probability() - 0.25) < 1e-4

    # 模拟 45 分钟 (2700秒，即 30~60 分钟的 50% 进度) -> 概率为 0.50
    pet.last_poop_time = now_t - 2700.0
    assert abs(pet.get_poop_probability() - 0.50) < 1e-4

    # 模拟 52.5 分钟 (3150秒，即 30~60 分钟的 75% 进度) -> 概率为 0.75
    pet.last_poop_time = now_t - 3150.0
    assert abs(pet.get_poop_probability() - 0.75) < 1e-4

    # 模拟 60 分钟 (3600秒，到达满额) -> 概率为 1.0 (100%)
    pet.last_poop_time = now_t - 3600.0
    assert pet.get_poop_probability() == 1.0

    # 模拟 80 分钟 (4800秒，超时保护) -> 概率稳定为 1.0 (100%)
    pet.last_poop_time = now_t - 4800.0
    assert pet.get_poop_probability() == 1.0

    # 7. 验证一键铲屎 (clean_all_poop) 清理屏幕上所有大便
    p1 = PoopItemWindow(100, 100)
    p2 = PoopItemWindow(200, 100)
    p3 = PoopItemWindow(300, 100)
    pet.active_poops.extend([p1, p2, p3])
    p1.cleaned.connect(pet._on_poop_cleaned)
    p2.cleaned.connect(pet._on_poop_cleaned)
    p3.cleaned.connect(pet._on_poop_cleaned)
    assert len(pet.active_poops) == 3

    cleaned_count = pet.clean_all_poop("测试一键铲屎")
    assert cleaned_count == 3
    assert p1.state == "clean"
    assert p2.state == "clean"
    assert p3.state == "clean"

    # 推进 4 帧清理闪烁
    for _ in range(4):
        p1._on_clean_tick()
        p2._on_clean_tick()
        p3._on_clean_tick()
    assert len(pet.active_poops) == 0
    assert "已清理桌面 3 坨便便" in pet.last_feedback

    # 桌面没有便便时再次调用 clean_all_poop
    assert pet.clean_all_poop() == 0
    assert "没有便便需要清理" in pet.last_feedback

    # 清理关闭窗口
    pet.close()

    print("PASS: test_poop_behavior_flow")

def test_context_menu_poop_option_in_release_vs_dev():
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)

    from cockatiel_window import CockatielWindow
    from PySide6.QtWidgets import QMenu
    from PySide6.QtCore import QPoint
    from unittest.mock import patch

    pet = CockatielWindow()

    last_actions = []
    class MockMenu(QMenu):
        def exec(self, *args, **kwargs):
            last_actions.clear()
            last_actions.extend([a.text() for a in self.actions()])
            return None

    # 1. 验证发布模式 (is_dev_mode 返回 False)：右键菜单必须完全隐藏“禁止随地大小便”
    with patch("cockatiel_window.QMenu", MockMenu):
        with patch("cockatiel_window.is_dev_mode", return_value=False):
            pet.show_context_menu(QPoint(10, 10))
            assert len(last_actions) > 0, "发布模式右键菜单未成功构建"
            assert not any("禁止随地大小便" in text for text in last_actions), \
                f"发布版本右键菜单中严禁出现‘禁止随地大小便’选项！当前菜单为: {last_actions}"
            assert any("一键铲屎" in text for text in last_actions), \
                f"发布版本右键菜单中必须包含‘一键铲屎’选项！当前菜单为: {last_actions}"

    # 2. 验证开发调试模式 (is_dev_mode 返回 True)：右键菜单正常保留“禁止随地大小便”与“一键铲屎”以供测试
    class MockMenuDev(QMenu):
        def exec(self, *args, **kwargs):
            last_actions.clear()
            last_actions.extend([a.text() for a in self.actions()])
            for a in self.actions():
                if "禁止随地大小便" in a.text():
                    return a
            return None

    with patch("cockatiel_window.QMenu", MockMenuDev):
        with patch("cockatiel_window.is_dev_mode", return_value=True):
            initial_state = pet.is_poop_disabled
            pet.show_context_menu(QPoint(10, 10))
            assert any("禁止随地大小便" in text for text in last_actions), \
                f"开发模式右键菜单中应保留‘禁止随地大小便’选项以供调试！当前菜单为: {last_actions}"
            assert any("一键铲屎" in text for text in last_actions), \
                f"开发模式右键菜单中应保留‘一键铲屎’选项！当前菜单为: {last_actions}"
            assert pet.is_poop_disabled != initial_state, "开发模式下点击菜单应成功切换大小便禁用状态"

    # 3. 验证点击“一键铲屎”成功触发 clean_all_poop
    class MockMenuCleanPoop(QMenu):
        def exec(self, *args, **kwargs):
            for a in self.actions():
                if "一键铲屎" in a.text():
                    return a
            return None

    with patch("cockatiel_window.QMenu", MockMenuCleanPoop):
        with patch.object(pet, "clean_all_poop", return_value=3) as mock_clean:
            pet.show_context_menu(QPoint(10, 10))
            mock_clean.assert_called_once()

    pet.close()
    print("PASS: test_context_menu_poop_option_in_release_vs_dev")

def test_head_hover_2s_trigger_flow():
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)

    from cockatiel_window import CockatielWindow
    from PySide6.QtCore import QEvent, QPoint

    pet = CockatielWindow()
    pet.facing_direction = -1
    pet.switch_behavior(BEHAVIOR_CATALOG[BehaviorType.IDLE_BLINK], 10.0)
    pet.mood.fright = 0.0

    # 1. 模拟鼠标移入头颈部 (28, 30 为头部正中)
    t0 = 1000.0
    head_pos = QPoint(28, 30)
    assert pet.is_head_neck_zone(head_pos) is True

    # 刚移入 (t = 0s)
    pet.update_head_hover(local_pos=head_pos, now=t0)
    assert pet.hover_head_start_time == t0
    assert pet.current_behavior.code == BehaviorType.IDLE_BLINK

    # 停留 0.5 秒 (t = 0.5s) -> 不触发 (未满2秒)
    pet.update_head_hover(local_pos=head_pos, now=t0 + 0.5)
    assert pet.current_behavior.code == BehaviorType.IDLE_BLINK

    # 停留 0.6 秒 (原旧版本阈值) -> 依然不触发 (必须超过2秒)
    pet.update_head_hover(local_pos=head_pos, now=t0 + 0.6)
    assert pet.current_behavior.code == BehaviorType.IDLE_BLINK

    # 停留 1.5 秒 -> 依然不触发
    pet.update_head_hover(local_pos=head_pos, now=t0 + 1.5)
    assert pet.current_behavior.code == BehaviorType.IDLE_BLINK

    # 2. 模拟移开到身体部位 (65, 40 为背部/身体) -> 重置悬停时间
    body_pos = QPoint(65, 40)
    assert pet.is_head_neck_zone(body_pos) is False
    pet.update_head_hover(local_pos=body_pos, now=t0 + 1.8)
    assert pet.hover_head_start_time is None
    assert pet.current_behavior.code == BehaviorType.IDLE_BLINK

    # 3. 再次移入头部，必须重新计算 2 秒
    t1 = 2000.0
    pet.update_head_hover(local_pos=head_pos, now=t1)
    assert pet.hover_head_start_time == t1

    # 停留 1.9 秒 -> 不触发
    pet.update_head_hover(local_pos=head_pos, now=t1 + 1.9)
    assert pet.current_behavior.code == BehaviorType.IDLE_BLINK

    # 停留恰好达到/超过 2.0 秒 (t = 2.05s) -> 成功触发低头求撸 (COMFORT_BOW)
    triggered = pet.update_head_hover(local_pos=head_pos, now=t1 + 2.05)
    assert triggered is True
    assert pet.current_behavior.code == BehaviorType.COMFORT_BOW
    assert "超过2秒" in pet.last_feedback
    # 触发后悬停起始时间重置为 None
    assert pet.hover_head_start_time is None

    # 4. 模拟 leaveEvent 移出窗口重置
    pet.switch_behavior(BEHAVIOR_CATALOG[BehaviorType.IDLE_BLINK], 10.0)
    t2 = 3000.0
    pet.update_head_hover(local_pos=head_pos, now=t2)
    assert pet.hover_head_start_time == t2

    dummy_event = QEvent(QEvent.Type.Leave)
    pet.leaveEvent(dummy_event)
    assert pet.hover_head_start_time is None

    # 移出后 10 秒再次移入，不会因为历史时间差瞬发触发
    pet.update_head_hover(local_pos=head_pos, now=t2 + 10.0)
    assert pet.hover_head_start_time == t2 + 10.0
    assert pet.current_behavior.code == BehaviorType.IDLE_BLINK

    # 5. 模拟惊吓戒备状态 (fright >= 25.0) 下不会触发主动求撸
    pet.switch_behavior(BEHAVIOR_CATALOG[BehaviorType.IDLE_BLINK], 10.0)
    pet.mood.fright = 30.0
    t3 = 4000.0
    pet.update_head_hover(local_pos=head_pos, now=t3)
    triggered = pet.update_head_hover(local_pos=head_pos, now=t3 + 2.5)
    assert triggered is False
    assert pet.current_behavior.code == BehaviorType.IDLE_BLINK

    pet.close()
    print("PASS: test_head_hover_2s_trigger_flow")

def test_startup_fly_in_and_exit_fly_out_flow():
    """验证开机从屏幕外呼啸飞入降落动画，以及告别退出时向上飞离屏幕外再退出的全套动力学"""
    app = QApplication.instance() or QApplication(sys.argv)
    from cockatiel_window import CockatielWindow
    from models import BehaviorType

    # 1. 测试开机飞入动力学 (start_fly_in)
    pet = CockatielWindow(start_with_fly_in=True)
    assert pet.is_flying is True
    assert pet.flight_purpose == "fly_in"
    assert pet.current_behavior.code == BehaviorType.IDLE_FLY

    # 基于飞入目标所在屏幕获取可视矩形，避免多显示器将屏幕外坐标误判为副屏内坐标
    target_screen = QApplication.screenAt(pet.fly_target_pos.toPoint()) or QApplication.primaryScreen()
    rect = target_screen.availableGeometry()
    # 起点必定在屏幕外 (x < rect.left() or x > rect.right() - w or y < rect.top())
    start_x = pet.fly_start_pos.x()
    start_y = pet.fly_start_pos.y()
    is_outside = (
        start_x < rect.left()
        or start_x > rect.right() - pet.width()
        or start_y < rect.top()
    )
    assert is_outside, f"Fly-in start pos ({start_x}, {start_y}) must be outside screen {rect}!"

    # 终点必定在屏幕可视区域内
    target_x = pet.fly_target_pos.x()
    target_y = pet.fly_target_pos.y()
    assert rect.left() <= target_x <= rect.right() - pet.width()
    assert rect.top() <= target_y <= rect.bottom() - pet.height()

    # 步进飞行动力学插值
    while pet.is_flying:
        pet.on_fly_step()

    assert pet.is_flying is False
    assert pet.fly_progress == 1.0
    # 触地降落位置已就绪
    assert abs(pet.x() - int(target_x)) <= 15
    assert abs(pet.y() - int(target_y)) <= 15
    # 落地动作播放
    assert pet.current_behavior.code in (BehaviorType.COMFORT_BOW, BehaviorType.COMFORT_FLUFF, BehaviorType.IDLE_BLINK)

    # 2. 测试告别退出飞离动力学 (start_fly_out_and_quit)
    quit_called = []
    pet._on_fly_out_finished = lambda: quit_called.append(True)

    pet.start_fly_out_and_quit()
    assert pet.is_exiting is True
    assert pet.is_flying is True
    assert pet.flight_purpose == "fly_out"
    assert pet.current_behavior.code == BehaviorType.IDLE_FLY

    # 离场目标坐标必定在屏幕上方外部
    assert pet.fly_target_pos.y() < rect.top()

    # 步进插值直到完全飞离屏幕
    while pet.is_flying:
        pet.on_fly_step()

    assert pet.is_flying is False
    assert len(quit_called) == 1, "Exit callback must be triggered once cockatiel leaves the screen!"

    pet.close()
    print("PASS: test_startup_fly_in_and_exit_fly_out_flow")

if __name__ == "__main__":
    test_models_definitions()
    test_wake_no_flicker_flow()
    test_yawn_behavior_flow()
    test_waddle_dual_mode_behavior()
    test_sprite_integrity()
    test_head_chin_hit_zone()
    test_sleep_unmirrored_z_both_directions()
    test_head_pet_probabilistic_preen_flow()
    test_updater_version_and_integration()
    test_poop_behavior_flow()
    test_context_menu_poop_option_in_release_vs_dev()
    test_head_hover_2s_trigger_flow()
    test_startup_fly_in_and_exit_fly_out_flow()
    print("ALL TESTS PASSED!")
