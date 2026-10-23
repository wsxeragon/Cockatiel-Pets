import sys
import os
import time
import unittest
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt

from models import BehaviorType, BEHAVIOR_CATALOG
from cockatiel_window import CockatielWindow

class TestMagicTrick(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance()
        if cls.app is None:
            cls.app = QApplication(sys.argv)

    def test_magic_trick_sprites_exist(self):
        """Verify all 110 frames exist for classic and triple crests"""
        for crest in ["classic", "triple"]:
            folder = os.path.join("assets", f"sprites_{crest}")
            for i in range(110):
                frame_file = os.path.join(folder, f"magic_trick_{i}.png")
                self.assertTrue(os.path.exists(frame_file), f"Missing frame: {frame_file}")

    def test_magic_trick_execution_flow(self):
        """Test full single-round flow: enter, expand window, teleport at frame 51, finish, restore size"""
        pet = CockatielWindow()
        
        # 1. Trigger magic trick with repeats=1
        pet.trigger_magic_trick("测试变魔术", repeats=1)
        self.assertEqual(pet.current_behavior.code, BehaviorType.MAGIC_TRICK)
        self.assertEqual(pet.width(), 260)
        self.assertEqual(pet.height(), 120)
        self.assertEqual(pet.current_frame_index, 0)
        self.assertEqual(pet.magic_remaining_repeats, 1)

        # 2. Step frames up to 50
        for idx in range(1, 51):
            pet.on_anim_frame_step()
            self.assertEqual(pet.current_frame_index, idx)
            
        # Pos before teleport
        pre_teleport_pos = (pet.x(), pet.y())

        # 3. Step to frame 51 (Teleport Frame)
        pet.on_anim_frame_step()
        self.assertEqual(pet.current_frame_index, 51)
        post_teleport_pos = (pet.x(), pet.y())
        
        # Pos should have changed due to safe teleport
        print(f"Pre-teleport pos: {pre_teleport_pos}, Post-teleport pos: {post_teleport_pos}")
        self.assertNotEqual(pre_teleport_pos, post_teleport_pos, "Window should have teleported at frame 51!")

        # 4. Step from frame 52 to 109 (last frame)
        for idx in range(52, 110):
            pet.on_anim_frame_step()
            self.assertEqual(pet.current_frame_index, idx)
            self.assertEqual(pet.current_behavior.code, BehaviorType.MAGIC_TRICK)

        # Step off frame 109 should switch to IDLE_WADDLE
        pet.on_anim_frame_step()
        self.assertEqual(pet.current_behavior.code, BehaviorType.IDLE_WADDLE)
        self.assertEqual(pet.width(), 100)
        self.assertEqual(pet.height(), 80)
        self.assertEqual(pet.facing_direction, 1)

        pet.close()
        print("PASS: test_magic_trick_execution_flow")

    def test_magic_trick_repeats_flow(self):
        """Test random repeats (e.g. repeats=2): loops back to frame 0, teleports again, finishes on round 2"""
        pet = CockatielWindow()
        
        pet.trigger_magic_trick("测试连变2次魔术", repeats=2)
        self.assertEqual(pet.magic_remaining_repeats, 2)
        self.assertEqual(pet.magic_total_repeats, 2)

        # Round 1:
        # Step through 0..50
        for _ in range(1, 51):
            pet.on_anim_frame_step()
        # Teleport 1 at frame 51
        pet.on_anim_frame_step()
        self.assertEqual(pet.current_frame_index, 51)
        pos_after_t1 = (pet.x(), pet.y())
        
        # Step through 52..109
        for _ in range(52, 110):
            pet.on_anim_frame_step()
            
        # Stepping off frame 109 on Round 1 should loop back to frame 0
        pet.on_anim_frame_step()
        self.assertEqual(pet.current_behavior.code, BehaviorType.MAGIC_TRICK)
        self.assertEqual(pet.current_frame_index, 0)
        self.assertEqual(pet.magic_remaining_repeats, 1)
        self.assertEqual(pet.width(), 260)
        
        # Round 2:
        for _ in range(1, 51):
            pet.on_anim_frame_step()
        # Teleport 2 at frame 51
        pet.on_anim_frame_step()
        self.assertEqual(pet.current_frame_index, 51)
        pos_after_t2 = (pet.x(), pet.y())
        self.assertNotEqual(pos_after_t1, pos_after_t2, "Should teleport to a new location in Round 2")

        # Step through 52..109
        for _ in range(52, 110):
            pet.on_anim_frame_step()

        # Stepping off frame 109 on Round 2 should finish to IDLE_WADDLE
        pet.on_anim_frame_step()
        self.assertEqual(pet.current_behavior.code, BehaviorType.IDLE_WADDLE)
        self.assertEqual(pet.width(), 100)
        self.assertEqual(pet.height(), 80)

        pet.close()
        print("PASS: test_magic_trick_repeats_flow")

    def test_magic_trick_random_repeats_range(self):
        """Test default trigger chooses random repeats between 1 and 4"""
        pet = CockatielWindow()
        
        found_repeats = set()
        for _ in range(40):
            pet.trigger_magic_trick("测试随机次数")
            r = pet.magic_remaining_repeats
            self.assertIn(r, [1, 2, 3, 4])
            found_repeats.add(r)
            pet.switch_behavior(BEHAVIOR_CATALOG[BehaviorType.IDLE_BLINK], 1.0)
            
        print("Observed random repeat counts:", found_repeats)
        self.assertTrue(len(found_repeats) >= 3, "Should observe variety of 1-4 repeats")
        pet.close()
        print("PASS: test_magic_trick_random_repeats_range")

    def test_both_crests_load_magic_sprites(self):
        """Test switching crest styles and verifying sprites load"""
        pet = CockatielWindow()
        
        for crest in ["classic", "triple"]:
            pet.switch_crest_style(crest)
            for i in [0, 51, 109]:
                frame_name = f"magic_trick_{i}"
                self.assertIn(frame_name, pet.sprites)
                self.assertFalse(pet.sprites[frame_name].isNull())
                
        pet.switch_crest_style("classic")
        pet.close()
        print("PASS: test_both_crests_load_magic_sprites")

    def test_default_crest_is_classic(self):
        """Test default crest style is classic (rabbit ears)"""
        pet = CockatielWindow()
        self.assertEqual(pet.load_saved_crest_style(), "classic")
        self.assertEqual(pet.crest_style, "classic")
        pet.close()
        print("PASS: test_default_crest_is_classic")

    def test_magic_trick_repeats_mirroring_flow(self):
        """Test magic trick alternates mirroring between repeats so bird never has to turn around"""
        pet = CockatielWindow()
        # Ensure pet is facing left
        pet.facing_direction = -1
        # Place window away from edges
        pet.safe_move(500, 500)
        
        pet.trigger_magic_trick("测试镜像交替", repeats=3)
        self.assertFalse(pet.is_magic_mirrored, "Round 1 facing left should start non-mirrored")
        self.assertEqual(pet.facing_direction, -1)
        
        # Step through Round 1 to frame 109
        for _ in range(109):
            pet.on_anim_frame_step()
        self.assertEqual(pet.current_frame_index, 109)
        # In non-mirrored frame 109, bird is at bx=155, facing right
        bird_global_x_end_r1 = pet.x() + 155
        
        # Step off frame 109 -> transition to Round 2
        pet.on_anim_frame_step()
        self.assertEqual(pet.current_frame_index, 0)
        self.assertTrue(pet.is_magic_mirrored, "Round 2 should alternate to mirrored")
        self.assertEqual(pet.facing_direction, 1, "Bird should face right in Round 2 without turning")
        # In mirrored frame 0, bird is at bx=5
        bird_global_x_start_r2 = pet.x() + 5
        self.assertEqual(bird_global_x_end_r1, bird_global_x_start_r2, "Bird global position must remain identical across repeat transition!")

        # Step through Round 2 to frame 109
        for _ in range(109):
            pet.on_anim_frame_step()
        self.assertEqual(pet.current_frame_index, 109)
        # In mirrored frame 109, bird is at bx=5, facing left
        bird_global_x_end_r2 = pet.x() + 5

        # Step off frame 109 -> transition to Round 3
        pet.on_anim_frame_step()
        self.assertEqual(pet.current_frame_index, 0)
        self.assertFalse(pet.is_magic_mirrored, "Round 3 should alternate back to non-mirrored")
        self.assertEqual(pet.facing_direction, -1, "Bird should face left in Round 3 without turning")
        bird_global_x_start_r3 = pet.x() + 155
        self.assertEqual(bird_global_x_end_r2, bird_global_x_start_r3, "Bird global position must remain identical across repeat transition!")

        # Step through Round 3 to end
        for _ in range(109):
            pet.on_anim_frame_step()
        # Exit to IDLE_WADDLE
        pet.on_anim_frame_step()
        self.assertEqual(pet.current_behavior.code, BehaviorType.IDLE_WADDLE)
        self.assertEqual(pet.facing_direction, 1, "Final exit from non-mirrored should face right")
        self.assertEqual(pet.waddle_direction, 1)

        pet.close()
        print("PASS: test_magic_trick_repeats_mirroring_flow")

    def test_no_closed_eyes_or_posture_flip_at_end(self):
        """Verify frames 102..109 do not flip posture and keep open eyes (no fluff_0)"""
        from PIL import Image
        for crest in ["classic", "triple"]:
            folder = os.path.join("assets", f"sprites_{crest}")
            idle_0 = Image.open(os.path.join(folder, "idle_0.png"))
            idle_r = idle_0.transpose(Image.FLIP_LEFT_RIGHT)
            
            for i in range(102, 110):
                f_path = os.path.join(folder, f"magic_trick_{i}.png")
                frame = Image.open(f_path)
                # Crop the bird region in the stage: (155, 26, 255, 106)
                bird_crop = frame.crop((155, 26, 255, 106))
                
                # Check that pixels match idle_r (bird proudly facing right with open eyes)
                diff = sum(abs(a - b) for a, b in zip(bird_crop.tobytes(), idle_r.tobytes()))
                self.assertEqual(diff, 0, f"Frame {i} in {crest} has unexpected posture flip or closed eyes!")
        print("PASS: test_no_closed_eyes_or_posture_flip_at_end")

    def test_magic_trick_exit_waddle_10s_and_clean_transitions(self):
        """Verify magic trick exits into 10.0s IDLE_WADDLE and all transitions maintain clean canvas alignment"""
        pet = CockatielWindow()
        pet.trigger_magic_trick(repeats=1)
        # Step through 109 frames to frame 109
        for _ in range(109):
            pet.on_anim_frame_step()
        # Next frame triggers exit to IDLE_WADDLE
        pet.on_anim_frame_step()
        self.assertEqual(pet.current_behavior.code, BehaviorType.IDLE_WADDLE)
        rem_time = pet.action_end_time - time.time()
        self.assertTrue(9.0 <= rem_time <= 10.5, f"Expected 10.0s waddle duration, got {rem_time:.2f}s")

        # Verify play_ball exit transition has no geometry-pixmap mismatch
        paints = []
        orig_paint = pet.paintEvent
        def record_paint(event):
            pix = pet.get_current_pixmap()
            paints.append((pet.current_behavior.code.value, pet.width(), pet.height(), pix.width(), pix.height()))
            orig_paint(event)
        pet.paintEvent = record_paint

        pet.switch_behavior(BEHAVIOR_CATALOG[BehaviorType.EXCITE_PLAY_BALL])
        QApplication.processEvents()
        pet.current_frame_index = 299
        paints.clear()

        pet.on_anim_frame_step()
        QApplication.processEvents()

        for b_name, w_w, w_h, p_w, p_h in paints:
            self.assertEqual(w_w, p_w, f"Window width {w_w} must match pixmap width {p_w}")
            self.assertEqual(w_h, p_h, f"Window height {w_h} must match pixmap height {p_h}")

        pet.close()
        print("PASS: test_magic_trick_exit_waddle_10s_and_clean_transitions")

if __name__ == "__main__":
    unittest.main()

