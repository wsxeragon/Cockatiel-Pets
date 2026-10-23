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
    assert APP_VERSION == "0.0.7", f"APP_VERSION should be '0.0.7', got {APP_VERSION}"
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
    print("PASS: test_updater_version_and_integration")

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
    print("ALL TESTS PASSED!")
