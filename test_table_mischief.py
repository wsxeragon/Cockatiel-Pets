import sys
import os
import time
import unittest
from PIL import Image
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt, QPoint
from PySide6.QtGui import QMouseEvent

from models import BehaviorType, BEHAVIOR_CATALOG, STAGE_STUNT_BEHAVIORS
from cockatiel_window import CockatielWindow

class TestTableMischief(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance()
        if cls.app is None:
            cls.app = QApplication(sys.argv)

    def test_table_mischief_sprites_exist_and_dimensions(self):
        """Verify all 400 frames exist for classic and triple crests and are exactly 320x200"""
        for crest in ["classic", "triple"]:
            folder = os.path.join("assets", f"sprites_{crest}")
            self.assertTrue(os.path.exists(folder), f"Directory missing: {folder}")
            for i in range(400):
                frame_file = os.path.join(folder, f"table_mischief_{i}.png")
                self.assertTrue(os.path.exists(frame_file), f"Missing frame: {frame_file}")
                with Image.open(frame_file) as img:
                    self.assertEqual(img.size, (320, 200), f"Frame {frame_file} size {img.size} != (320, 200)")
        print("PASS: test_table_mischief_sprites_exist_and_dimensions")

    def test_both_crests_load_table_mischief_sprites(self):
        """Verify pet window loads all 400 table mischief sprites under both classic and triple crests"""
        pet = CockatielWindow()
        for style in ["classic", "triple"]:
            pet.switch_crest_style(style)
            for i in range(400):
                sname = f"table_mischief_{i}"
                self.assertIn(sname, pet.sprites, f"Sprite {sname} not loaded for {style} crest")
                pix = pet.sprites[sname]
                self.assertFalse(pix.isNull(), f"Sprite {sname} is null for {style} crest")
                self.assertEqual(pix.width(), 320)
                self.assertEqual(pix.height(), 200)
        pet.switch_crest_style("classic")
        self.assertEqual(pet.crest_style, "classic")
        pet.close()
        print("PASS: test_both_crests_load_table_mischief_sprites")

    def test_table_mischief_behavior_def_in_models(self):
        """Verify BehaviorDef in BEHAVIOR_CATALOG and STAGE_STUNT_BEHAVIORS"""
        self.assertIn(BehaviorType.TABLE_MISCHIEF, BEHAVIOR_CATALOG)
        b_def = BEHAVIOR_CATALOG[BehaviorType.TABLE_MISCHIEF]
        self.assertEqual(b_def.code, BehaviorType.TABLE_MISCHIEF)
        self.assertEqual(len(b_def.frames), 400)
        self.assertEqual(b_def.frame_interval_ms, 40)
        self.assertFalse(b_def.is_interruptible)
        self.assertFalse(b_def.is_looping)
        # TABLE_MISCHIEF is temporarily hidden from STAGE_STUNT_BEHAVIORS as per user instruction during tuning
        # self.assertIn(BehaviorType.TABLE_MISCHIEF, STAGE_STUNT_BEHAVIORS)
        print("PASS: test_table_mischief_behavior_def_in_models")

    def test_table_mischief_multiphase_flow(self):
        """Verify the full 5-phase organic sequence:
        Phase 1: 5s pre-walk -> Phase 2: fly to distant desk -> Phase 3: 400-frame desk stunt (320x200) ->
        Phase 4: fly landing (100x80) -> Phase 5: 10s post-walk stroll on desktop
        """
        pet = CockatielWindow()
        pet.mood.excitement = 85.0
        pet.safe_move(300, 500, margin=10)

        # 1. Trigger full stunt sequence
        pet.trigger_table_mischief("测试完整多阶段恶作剧")
        self.assertEqual(pet._table_mischief_phase, "pre_walk")
        self.assertEqual(pet.current_behavior.code, BehaviorType.IDLE_WADDLE)
        self.assertEqual(pet.width(), 100)
        self.assertEqual(pet.height(), 80)
        self.assertIn("迈着小碎步搜寻作案目标", pet.last_feedback)

        # 2. Advance past 5s pre-walk
        pet.action_end_time = time.time() - 1.0
        pet.on_main_tick()
        self.assertEqual(pet._table_mischief_phase, "fly_to_desk")
        self.assertTrue(pet.is_flying)
        self.assertEqual(pet.flight_purpose, "table_mischief_approach")
        self.assertEqual(pet.current_behavior.code, BehaviorType.IDLE_FLY)

        # 3. Complete flight arrival at desk
        pet.fly_progress = 1.0
        pet.on_fly_step()
        self.assertFalse(pet.is_flying)
        self.assertEqual(pet._table_mischief_phase, "desk_stunt")
        self.assertEqual(pet.current_behavior.code, BehaviorType.TABLE_MISCHIEF)
        self.assertEqual(pet.width(), 320)
        self.assertEqual(pet.height(), 200)

        # 4. Advance through 400 frames of desk stunt to the end
        pet.current_frame_index = 398
        pet.on_anim_frame_step()
        self.assertEqual(pet.current_frame_index, 399)

        # Final frame step triggers flight away & landing transition
        pet.on_anim_frame_step()
        self.assertEqual(pet._table_mischief_phase, "fly_landing")
        self.assertTrue(pet.is_flying)
        self.assertEqual(pet.flight_purpose, "table_mischief_landing")
        self.assertEqual(pet.width(), 100)
        self.assertEqual(pet.height(), 80)

        # 5. Complete landing flight
        pet.fly_progress = 1.0
        pet.on_fly_step()
        self.assertFalse(pet.is_flying)
        self.assertEqual(pet._table_mischief_phase, "post_walk")
        self.assertEqual(pet.current_behavior.code, BehaviorType.IDLE_WADDLE)
        self.assertEqual(pet.width(), 100)
        self.assertEqual(pet.height(), 80)
        self.assertEqual(pet.mood.excitement, 0.0, "Excitement must be cleared to 0 upon completion")
        self.assertIn("开心溜达10秒", pet.last_feedback)

        # 6. Advance past 10s post-walk
        pet.action_end_time = time.time() - 1.0
        pet.on_main_tick()
        self.assertIsNone(pet._table_mischief_phase)

        pet.close()
        print("PASS: test_table_mischief_multiphase_flow")

    def test_table_mischief_skip_pre_walk_direct_desk(self):
        """Verify skip_pre_walk=True directly launches the 320x200 desk mischief"""
        pet = CockatielWindow()
        pet.trigger_table_mischief("直接入席", skip_pre_walk=True)
        self.assertEqual(pet._table_mischief_phase, "desk_stunt")
        self.assertEqual(pet.current_behavior.code, BehaviorType.TABLE_MISCHIEF)
        self.assertEqual(pet.width(), 320)
        self.assertEqual(pet.height(), 200)
        pet.close()
        print("PASS: test_table_mischief_skip_pre_walk_direct_desk")

    def test_table_mischief_context_menu_trigger(self):
        """Verify right click context menu can trigger TABLE_MISCHIEF flow"""
        pet = CockatielWindow()
        pet.trigger_table_mischief("右键菜单触发：桌霸大恶作剧！")
        self.assertEqual(pet._table_mischief_phase, "pre_walk")
        self.assertEqual(pet.current_behavior.code, BehaviorType.IDLE_WADDLE)
        self.assertIn("桌霸大恶作剧", pet.last_feedback)
        pet.close()
        print("PASS: test_table_mischief_context_menu_trigger")

    def test_table_mischief_never_auto_selected(self):
        """桌霸大恶作剧只允许右键菜单手动触发，绝不进入自发行为轮盘"""
        from models import MoodDynamics
        for excitement in (0.0, 15.0, 30.0, 60.0, 100.0):
            mood = MoodDynamics()
            mood.excitement = excitement
            for _ in range(1500):
                b_def, _duration = mood.select_next_behavior(BehaviorType.IDLE_BLINK, is_at_edge=False)
                self.assertNotEqual(b_def.code, BehaviorType.TABLE_MISCHIEF,
                                    f"兴奋度 {excitement} 时轮盘仍抽到了桌霸大恶作剧，会自动触发！")
        print("PASS: test_table_mischief_never_auto_selected")

if __name__ == '__main__':
    unittest.main()
