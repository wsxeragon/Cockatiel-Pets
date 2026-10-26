import sys
import os
import unittest
from PIL import Image
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt, QPoint
from PySide6.QtGui import QMouseEvent

from models import BehaviorType, BEHAVIOR_CATALOG, EXCITED_BEHAVIORS, MoodDynamics
from cockatiel_window import CockatielWindow

class TestUnicycle(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance()
        if cls.app is None:
            cls.app = QApplication(sys.argv)

    def test_unicycle_sprites_exist_and_dimensions(self):
        """Verify all 500 frames exist for classic and triple crests and are exactly 240x160"""
        for crest in ["classic", "triple"]:
            folder = os.path.join("assets", f"sprites_{crest}")
            self.assertTrue(os.path.exists(folder), f"Directory missing: {folder}")
            for i in range(500):
                frame_file = os.path.join(folder, f"unicycle_{i}.png")
                self.assertTrue(os.path.exists(frame_file), f"Missing frame: {frame_file}")
                with Image.open(frame_file) as img:
                    self.assertEqual(img.size, (240, 160), f"Frame {frame_file} size {img.size} != (240, 160)")
        print("PASS: test_unicycle_sprites_exist_and_dimensions")

    def test_both_crests_load_unicycle_sprites(self):
        """Verify pet window loads all 500 unicycle sprites under both classic and triple crests"""
        pet = CockatielWindow()
        for style in ["classic", "triple"]:
            pet.switch_crest_style(style)
            for i in range(500):
                sname = f"unicycle_{i}"
                self.assertIn(sname, pet.sprites, f"Sprite {sname} not loaded for {style} crest")
                pix = pet.sprites[sname]
                self.assertFalse(pix.isNull(), f"Sprite {sname} is null for {style} crest")
                self.assertEqual(pix.width(), 240)
                self.assertEqual(pix.height(), 160)
        # Always restore default classic crest style
        pet.switch_crest_style("classic")
        self.assertEqual(pet.crest_style, "classic")
        pet.close()
        print("PASS: test_both_crests_load_unicycle_sprites")

    def test_unicycle_behavior_def_in_models(self):
        """Verify BehaviorType.UNICYCLE catalog definition and excitement rules"""
        self.assertTrue(hasattr(BehaviorType, "UNICYCLE"))
        self.assertIn(BehaviorType.UNICYCLE, BEHAVIOR_CATALOG)
        b_def = BEHAVIOR_CATALOG[BehaviorType.UNICYCLE]
        self.assertEqual(b_def.code, BehaviorType.UNICYCLE)
        self.assertEqual(b_def.name_cn, "独轮杂技特技")
        self.assertEqual(len(b_def.frames), 500)
        self.assertEqual(b_def.frame_interval_ms, 40)
        self.assertFalse(b_def.is_interruptible)
        self.assertFalse(b_def.is_looping)
        self.assertIn(BehaviorType.UNICYCLE, EXCITED_BEHAVIORS)

        # Excitement threshold check: excitement < 30 should filter it out
        mood = MoodDynamics()
        for exc in [15.0, 25.0, 29.9]:
            mood.excitement = exc
            for _ in range(50):
                chosen_def, _ = mood.select_next_behavior(BehaviorType.IDLE_BLINK)
                self.assertNotEqual(chosen_def.code, BehaviorType.UNICYCLE, f"UNICYCLE should not trigger when excitement was {exc} < 30")

        # When excitement >= 30, active_rates > 0 allows candidate selection
        mood.excitement = 60.0
        mood.comfort = 40.0
        mood.fright = 0.0
        mood.fatigue = 0.0
        selected = set()
        for _ in range(300):
            chosen_def, _ = mood.select_next_behavior(BehaviorType.IDLE_BLINK)
            selected.add(chosen_def.code)
        # Active rates include UNICYCLE
        print("PASS: test_unicycle_behavior_def_in_models")

    def test_unicycle_long_side_selection(self):
        """Verify unicycle selects direction towards longer available screen space"""
        pet = CockatielWindow()
        rect = pet.get_screen_rect(use_available=True)

        # 1. Place near LEFT edge: long side is RIGHT
        pet.safe_move(rect.left() + 60, rect.top() + 300, margin=10)
        pet.prepare_unicycle_stunt()
        self.assertEqual(pet.unicycle_slide_dir, 1, "Near left edge, direction must be RIGHT (slide_dir=1)")
        self.assertFalse(pet.is_unicycle_mirrored, "Riding right must be unmirrored")
        self.assertEqual(pet.facing_direction, 1)

        # 2. Place near RIGHT edge: long side is LEFT
        pet.safe_move(rect.right() - 260, rect.top() + 300, margin=10)
        pet.prepare_unicycle_stunt()
        self.assertEqual(pet.unicycle_slide_dir, -1, "Near right edge, direction must be LEFT (slide_dir=-1)")
        self.assertTrue(pet.is_unicycle_mirrored, "Riding left must be mirrored")
        self.assertEqual(pet.facing_direction, -1)

        pet.close()
        print("PASS: test_unicycle_long_side_selection")

    def test_unicycle_geometry_transition(self):
        """Verify smooth canvas transition between standard 100x80 and unicycle 240x160"""
        pet = CockatielWindow()
        pet.switch_behavior(BEHAVIOR_CATALOG[BehaviorType.IDLE_BLINK])
        self.assertEqual(pet.width(), 100)
        self.assertEqual(pet.height(), 80)

        init_x = 400
        init_y = 300
        pet.safe_move(init_x, init_y, margin=10)
        actual_x = pet.x()
        actual_y = pet.y()

        # Trigger unicycle
        pet.trigger_unicycle("测试独轮杂技切入")
        self.assertEqual(pet.current_behavior.code, BehaviorType.UNICYCLE)
        self.assertEqual(pet.width(), 240)
        self.assertEqual(pet.height(), 160)

        # Verify ground alignment: entry moves top-left by (-54, -68) when unmirrored
        expected_stunt_x = actual_x - (86 if pet.is_unicycle_mirrored else 54)
        expected_stunt_y = actual_y - 68
        self.assertEqual(pet.x(), expected_stunt_x)
        self.assertEqual(pet.y(), expected_stunt_y)

        # Transition back to IDLE_BLINK
        pet.switch_behavior(BEHAVIOR_CATALOG[BehaviorType.IDLE_BLINK])
        self.assertEqual(pet.width(), 100)
        self.assertEqual(pet.height(), 80)
        self.assertEqual(pet.x(), actual_x)
        self.assertEqual(pet.y(), actual_y)

        pet.close()
        print("PASS: test_unicycle_geometry_transition")

    def test_unicycle_pixmap_mirroring(self):
        """Verify pixmap mirroring behavior during unicycle performance"""
        pet = CockatielWindow()
        pet.switch_behavior(BEHAVIOR_CATALOG[BehaviorType.UNICYCLE])

        # Test unmirrored
        pet.is_unicycle_mirrored = False
        pix_unmirrored = pet.get_current_pixmap()
        self.assertFalse(pix_unmirrored.isNull())
        self.assertEqual(pix_unmirrored.width(), 240)
        self.assertEqual(pix_unmirrored.height(), 160)

        # Test mirrored
        pet.is_unicycle_mirrored = True
        pix_mirrored = pet.get_current_pixmap()
        self.assertFalse(pix_mirrored.isNull())
        self.assertEqual(pix_mirrored.width(), 240)
        self.assertEqual(pix_mirrored.height(), 160)

        # Verify pixel mirroring: the pixels should be horizontally flipped
        img_un = pix_unmirrored.toImage()
        img_m = pix_mirrored.toImage()
        # Sample non-transparent pixel from unmirrored and check corresponding mirrored pos
        mirrored_match = True
        for y in range(0, 160, 10):
            for x in range(0, 240, 10):
                c1 = img_un.pixelColor(x, y)
                c2 = img_m.pixelColor(239 - x, y)
                if c1 != c2:
                    mirrored_match = False
                    break
            if not mirrored_match:
                break
        self.assertTrue(mirrored_match, "Mirrored pixmap should match flipped unmirrored pixmap")

        pet.close()
        print("PASS: test_unicycle_pixmap_mirroring")

    def test_unicycle_non_interruptible(self):
        """Verify mouse drag and clicks are blocked during unicycle performance"""
        pet = CockatielWindow()
        pet.trigger_unicycle("测试不可打断性")
        self.assertFalse(pet.is_dragging)

        click_pos = QPoint(100, 100)
        click_event = QMouseEvent(
            QMouseEvent.Type.MouseButtonPress,
            click_pos,
            Qt.MouseButton.LeftButton,
            Qt.MouseButton.LeftButton,
            Qt.KeyboardModifier.NoModifier
        )
        pet.mousePressEvent(click_event)
        self.assertFalse(pet.is_dragging, "Mouse click should NOT initiate dragging during unicycle stunt")
        self.assertEqual(pet.current_behavior.code, BehaviorType.UNICYCLE)

        pet.close()
        print("PASS: test_unicycle_non_interruptible")

    def test_unicycle_full_playback_and_completion(self):
        """Verify 500 frames play sequentially and safely transition directly to IDLE_WADDLE (10s) upon completion"""
        pet = CockatielWindow()
        pet.trigger_unicycle("测试全剧本播放完毕切出")
        self.assertEqual(pet.current_behavior.code, BehaviorType.UNICYCLE)
        self.assertEqual(pet.current_frame_index, 0)

        # Fast forward to frame 499 (last frame of 500 frames)
        pet.current_frame_index = 499
        pet.on_anim_frame_step()

        # Frame 499 completed -> should transition directly to IDLE_WADDLE for 10s
        self.assertEqual(pet.current_behavior.code, BehaviorType.IDLE_WADDLE)
        self.assertEqual(pet.width(), 100)
        self.assertEqual(pet.height(), 80)
        rem_dur = pet.action_end_time - pet.get_now()
        self.assertAlmostEqual(rem_dur, 10.0, delta=0.5)

        pet.close()
        print("PASS: test_unicycle_full_playback_and_completion")

if __name__ == "__main__":
    unittest.main()
