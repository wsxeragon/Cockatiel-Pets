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
    assert wake_def.frames == ["wake_0", "wake_1"], f"REST_WAKE frames mismatch: {wake_def.frames}"

    bite_def = BEHAVIOR_CATALOG[BehaviorType.FRIGHT_BITE]
    assert bite_def.is_looping is False, f"FRIGHT_BITE is_looping should be False, got {bite_def.is_looping}"
    print("PASS: test_models_definitions")

def test_wake_no_flicker_flow():
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)

    from cockatiel_window import CockatielWindow

    pet = CockatielWindow()

    # 1. Force into sleep
    pet.force_sleep("测试进入睡眠")
    assert pet.current_behavior.code == BehaviorType.REST_SLEEP
    assert pet.mood.fatigue == 100.0

    # 2. Clear fatigue while sleeping
    pet.clear_fatigue("测试清空疲劳")
    assert pet.mood.fatigue == 0.0
    assert pet.current_behavior.code == BehaviorType.REST_WAKE
    assert pet.current_frame_index == 0
    assert pet.current_behavior.frames[pet.current_frame_index] == "wake_0"

    # 3. Step animation timer once -> advances to wake_1 (standing alert)
    pet.on_anim_frame_step()
    assert pet.current_frame_index == 1
    assert pet.current_behavior.frames[pet.current_frame_index] == "wake_1"

    # 4. Step animation timer again -> MUST STAY AT wake_1 (is_looping=False), NO FLICKER BACK TO wake_0!
    pet.on_anim_frame_step()
    assert pet.current_frame_index == 1, f"Expected frame_index to stay at 1, but got {pet.current_frame_index} (flicker bug!)"
    assert pet.current_behavior.frames[pet.current_frame_index] == "wake_1"

    # 5. Advance time beyond action_end_time and tick main loop -> transitions cleanly to IDLE_BLINK
    pet.action_end_time = time.time() - 0.1
    pet.on_main_tick()
    assert pet.current_behavior.code == BehaviorType.IDLE_BLINK, f"Expected IDLE_BLINK, got {pet.current_behavior.code}"
    assert pet.current_frame_index == 0
    assert pet.current_behavior.frames[pet.current_frame_index] == "idle_0"

    pet.close()
    print("PASS: test_wake_no_flicker_flow")

def test_sprite_integrity():
    required_sprites = [
        "peck_0", "peck_1", "peck_2", "peck_3",
        "bonk_0", "bonk_1", "bonk_2", "bonk_3", "bonk_4",
        "wake_0", "wake_1", "sleep_0", "sleep_1",
        "preen_0", "preen_1", "preen_2", "preen_3"
    ]

    for s in required_sprites:
        p_assets = Path("assets/sprites") / f"{s}.png"
        p_2d = Path("2d-new/sprites") / f"{s}.png"
        assert p_assets.exists(), f"Missing {p_assets}"
        assert p_2d.exists(), f"Missing {p_2d}"

        img_a = Image.open(p_assets)
        img_2 = Image.open(p_2d)
        assert img_a.size == (100, 80), f"Size mismatch for {p_assets}: {img_a.size}"
        assert img_2.size == (100, 80), f"Size mismatch for {p_2d}: {img_2.size}"

    print("PASS: test_sprite_integrity")

if __name__ == "__main__":
    test_models_definitions()
    test_wake_no_flicker_flow()
    test_sprite_integrity()
    print("ALL TESTS PASSED!")
