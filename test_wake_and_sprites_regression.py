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
    assert waddle_def.frames == ["waddle_0", "waddle_1", "waddle_2", "waddle_3", "waddle_4", "waddle_5"], f"IDLE_WADDLE frames mismatch: {waddle_def.frames}"
    assert waddle_def.frame_interval_ms == 130, f"IDLE_WADDLE frame_interval_ms mismatch: {waddle_def.frame_interval_ms}"
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

    print("PASS: test_sprite_integrity")

if __name__ == "__main__":
    test_models_definitions()
    test_wake_no_flicker_flow()
    test_yawn_behavior_flow()
    test_waddle_dual_mode_behavior()
    test_sprite_integrity()
    print("ALL TESTS PASSED!")
