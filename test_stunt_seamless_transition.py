import sys
import os
import time
import unittest
from PySide6.QtWidgets import QApplication
from models import BehaviorType, BEHAVIOR_CATALOG
from cockatiel_window import CockatielWindow

class TestStuntSeamlessTransition(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance()
        if cls.app is None:
            cls.app = QApplication(sys.argv)

    def test_skateboard_seamless_transition_flow(self):
        """Verify Skateboard stunt completion:
        1. Single or final round dismount (frame 199) -> switches to IDLE_BLINK for 1.0s (closed-eye daze)
        2. Geometry restores to 100x80 without flicker, eye closed (idle_1)
        3. Pending next behavior is set to IDLE_WADDLE for 5.0s
        4. When 1s IDLE_BLINK expires -> switches to IDLE_WADDLE for 5.0s
        """
        pet = CockatielWindow()
        pet.safe_move(500, 500, margin=10)
        # Test explicit 1-round flow
        pet.trigger_skateboard("测试滑板衔接", repeats=1)
        self.assertEqual(pet.current_behavior.code, BehaviorType.SKATEBOARD)
        self.assertEqual(pet.width(), 200)
        self.assertEqual(pet.height(), 110)

        # Force to last frame
        pet.current_frame_index = 199

        # Trigger final step
        pet.on_anim_frame_step()

        # Step 1: Must enter IDLE_BLINK for 1.0s
        self.assertEqual(pet.current_behavior.code, BehaviorType.IDLE_BLINK)
        self.assertEqual(pet.width(), 100)
        self.assertEqual(pet.height(), 80)
        self.assertAlmostEqual(pet.action_end_time - time.time(), 1.0, delta=0.5)
        self.assertEqual(pet.pending_next_behavior, BehaviorType.IDLE_WADDLE)
        self.assertEqual(pet.pending_next_duration, 5.0)
        # Verify closed-eye pose is active
        self.assertEqual(pet._idle_frame_name(), "idle_1", "Must display closed-eye idle_1 during post-stunt daze")

        # Step 2: Advance past 1.0s IDLE_BLINK
        pet.action_end_time = time.time() - 0.1
        pet.on_main_tick()

        # Step 3: Must enter IDLE_WADDLE for 5.0s
        self.assertEqual(pet.current_behavior.code, BehaviorType.IDLE_WADDLE)
        self.assertEqual(pet.width(), 100)
        self.assertEqual(pet.height(), 80)
        self.assertAlmostEqual(pet.action_end_time - time.time(), 5.0, delta=0.5)
        self.assertIsNone(pet.pending_next_behavior)
        self.assertIn("5秒", pet.last_feedback)

        # Also verify random 1~3 rounds default initialization
        pet.trigger_skateboard("测试随机轮次")
        self.assertIn(pet.skateboard_total_repeats, [1, 2, 3], "Default repeats must be in [1, 2, 3]")

        pet.close()
        print("PASS: test_skateboard_seamless_transition_flow")

    def test_unicycle_seamless_transition_flow(self):
        """Verify Unicycle stunt completion:
        1. Frame 499 dismount completes -> switches to IDLE_BLINK for 1.0s (closed-eye daze)
        2. Geometry restores to 100x80 without flicker, eye closed (idle_1)
        3. Pending next behavior is set to IDLE_WADDLE for 5.0s
        4. When 1s IDLE_BLINK expires -> switches to IDLE_WADDLE for 5.0s
        """
        pet = CockatielWindow()
        pet.safe_move(500, 500, margin=10)
        pet.trigger_unicycle("测试独轮衔接")
        self.assertEqual(pet.current_behavior.code, BehaviorType.UNICYCLE)
        self.assertEqual(pet.width(), 240)
        self.assertEqual(pet.height(), 160)

        # Force to last frame
        pet.current_frame_index = 499

        # Trigger final step
        pet.on_anim_frame_step()

        # Step 1: Must enter IDLE_BLINK for 1.0s
        self.assertEqual(pet.current_behavior.code, BehaviorType.IDLE_BLINK)
        self.assertEqual(pet.width(), 100)
        self.assertEqual(pet.height(), 80)
        self.assertAlmostEqual(pet.action_end_time - time.time(), 1.0, delta=0.5)
        self.assertEqual(pet.pending_next_behavior, BehaviorType.IDLE_WADDLE)
        self.assertEqual(pet.pending_next_duration, 5.0)
        # Verify closed-eye pose is active
        self.assertEqual(pet._idle_frame_name(), "idle_1", "Must display closed-eye idle_1 during post-stunt daze")

        # Step 2: Advance past 1.0s IDLE_BLINK
        pet.action_end_time = time.time() - 0.1
        pet.on_main_tick()

        # Step 3: Must enter IDLE_WADDLE for 5.0s
        self.assertEqual(pet.current_behavior.code, BehaviorType.IDLE_WADDLE)
        self.assertEqual(pet.width(), 100)
        self.assertEqual(pet.height(), 80)
        self.assertAlmostEqual(pet.action_end_time - time.time(), 5.0, delta=0.5)
        self.assertIsNone(pet.pending_next_behavior)
        self.assertIn("5秒", pet.last_feedback)

        pet.close()
        print("PASS: test_unicycle_seamless_transition_flow")

if __name__ == '__main__':
    unittest.main()
