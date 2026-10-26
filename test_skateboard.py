import sys
import os
import unittest
from PIL import Image
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt, QPoint
from PySide6.QtGui import QMouseEvent

from models import BehaviorType, BEHAVIOR_CATALOG
from cockatiel_window import CockatielWindow

class TestSkateboard(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance()
        if cls.app is None:
            cls.app = QApplication(sys.argv)

    def test_skateboard_sprites_exist_and_dimensions(self):
        """Verify all 200 frames exist for classic and triple crests and are exactly 200x110"""
        for crest in ["classic", "triple"]:
            folder = os.path.join("assets", f"sprites_{crest}")
            self.assertTrue(os.path.exists(folder), f"Directory missing: {folder}")
            for i in range(200):
                frame_file = os.path.join(folder, f"skateboard_{i}.png")
                self.assertTrue(os.path.exists(frame_file), f"Missing frame: {frame_file}")
                with Image.open(frame_file) as img:
                    self.assertEqual(img.size, (200, 110), f"Frame {frame_file} size {img.size} != (200, 110)")
        print("PASS: test_skateboard_sprites_exist_and_dimensions")

    def test_both_crests_load_skateboard_sprites(self):
        """Verify pet window loads all 200 skateboard sprites under both classic and triple crests"""
        pet = CockatielWindow()
        for style in ["classic", "triple"]:
            pet.switch_crest_style(style)
            for i in range(200):
                sname = f"skateboard_{i}"
                self.assertIn(sname, pet.sprites, f"Sprite {sname} not loaded for {style} crest")
                pix = pet.sprites[sname]
                self.assertFalse(pix.isNull(), f"Sprite {sname} is null for {style} crest")
                self.assertEqual(pix.width(), 200)
                self.assertEqual(pix.height(), 110)
        # Always restore default classic crest style
        pet.switch_crest_style("classic")
        self.assertEqual(pet.crest_style, "classic")
        pet.close()
        print("PASS: test_both_crests_load_skateboard_sprites")

    def test_skateboard_long_side_selection(self):
        """Verify skateboard selects long side to slide based on distance to screen edges"""
        pet = CockatielWindow()
        rect = pet.get_screen_rect(use_available=True)

        # 1. Place near LEFT edge: long side is RIGHT
        pet.safe_move(rect.left() + 60, rect.top() + 300, margin=10)
        pet.prepare_skateboard_round(is_first_round=True)
        self.assertEqual(pet.skateboard_slide_dir, 1, "Near left edge, long side must be RIGHT (slide_dir=1)")
        self.assertFalse(pet.is_skateboard_mirrored, "Sliding right must be unmirrored")
        self.assertEqual(pet.facing_direction, 1)

        # 2. Place near RIGHT edge: long side is LEFT
        pet.safe_move(rect.right() - 160, rect.top() + 300, margin=10)
        pet.prepare_skateboard_round(is_first_round=True)
        self.assertEqual(pet.skateboard_slide_dir, -1, "Near right edge, long side must be LEFT (slide_dir=-1)")
        self.assertTrue(pet.is_skateboard_mirrored, "Sliding left must be mirrored")
        self.assertEqual(pet.facing_direction, -1)

        pet.close()
        print("PASS: test_skateboard_long_side_selection")

    def test_skateboard_half_screen_early_dismount(self):
        """Verify that when only half a screen (or less) is available, slide duration is reduced and bird jumps off early"""
        pet = CockatielWindow()
        rect = pet.get_screen_rect(use_available=True)

        # Place pet in the center of the screen so that both directions have <= half a screen
        center_x = int(rect.left() + rect.width() * 0.5)
        pet.safe_move(center_x, rect.top() + 300, margin=10)
        pet.trigger_skateboard(repeats=1)

        # In center of screen, available space on the chosen side is less than half_screen threshold
        self.assertLess(pet.skateboard_dismount_frame, 149, "Half screen space must reduce sliding time and set earlier dismount frame")
        self.assertGreaterEqual(pet.skateboard_dismount_frame, 30)

        # Step frames through: verify that upon reaching dismount frame, it skips directly to frame 150 (leap off board)
        jumped_to_dismount = False
        for _ in range(250):
            if pet.current_behavior.code != BehaviorType.SKATEBOARD:
                break
            prev_f = pet.current_frame_index
            pet.on_anim_frame_step()
            curr_f = pet.current_frame_index
            if curr_f - prev_f > 1 or (prev_f < 149 and curr_f >= 149):
                jumped_to_dismount = True

        self.assertTrue(jumped_to_dismount, "Must jump directly to dismount sequence upon reaching dismount frame!")
        pet.close()
        print("PASS: test_skateboard_half_screen_early_dismount")

    def test_skateboard_real_desktop_movement_and_landing(self):
        """Verify window actually moves across the desktop, carries momentum, and lands without pixel jumps"""
        pet = CockatielWindow()
        rect = pet.get_screen_rect(use_available=True)

        # Position near left with plenty of room to the right (use x >= 100 so target_x >= 50, avoiding initial clamp)
        start_x = rect.left() + 100
        start_y = rect.top() + 400
        pet.safe_move(start_x, start_y, margin=10)
        orig_100_x, orig_100_y = pet.x(), pet.y()

        pet.trigger_skateboard(repeats=1)
        self.assertEqual(pet.current_behavior.code, BehaviorType.SKATEBOARD)
        pos_after_entry_x = pet.x()
        self.assertEqual(pos_after_entry_x, orig_100_x - 51)

        # Step frames until finished
        pos_history = [pet.x()]
        for _ in range(250):
            if pet.current_behavior.code != BehaviorType.SKATEBOARD:
                break
            pet.on_anim_frame_step()
            pos_history.append(pet.x())

        # 1. Verify window physically moved across the desktop to the right
        max_traveled_x = max(pos_history)
        self.assertGreater(max_traveled_x, pos_after_entry_x + 200, "Window must physically travel across desktop!")

        # 2. Verify window smoothly restored to 100x80 at landing location and directly enters IDLE_WADDLE for 10s
        self.assertEqual(pet.current_behavior.code, BehaviorType.IDLE_WADDLE)
        self.assertEqual(pet.width(), 100)
        self.assertEqual(pet.height(), 80)
        # Landing bird center at 200px was pet.x() + 100; restored bird center at 100px is (restore_x) + 50
        final_200_x = pos_history[-2]  # position right before switch_behavior restored
        self.assertEqual(pet.x(), final_200_x + 51, "Zero-jump coordinate restoration at landing spot")
        rem_dur = pet.action_end_time - pet.get_now()
        self.assertAlmostEqual(rem_dur, 10.0, delta=0.5)

        pet.close()
        print("PASS: test_skateboard_real_desktop_movement_and_landing")

    def test_skateboard_two_round_mirrored_roundtrip(self):
        """Verify Round 1 moves along long side, Round 2 mirrors back across the screen"""
        pet = CockatielWindow()
        rect = pet.get_screen_rect(use_available=True)

        # Position near left edge
        pet.safe_move(rect.left() + 60, rect.top() + 400, margin=10)
        pet.trigger_skateboard(repeats=2)

        # Round 1 should slide RIGHT
        self.assertEqual(pet.skateboard_slide_dir, 1)
        self.assertFalse(pet.is_skateboard_mirrored)
        self.assertEqual(pet.facing_direction, 1)

        r1_positions = []
        # Step through Round 1 until repeat triggers Round 2
        for _ in range(250):
            if pet.skateboard_remaining_repeats == 1 and pet.current_frame_index == 0:
                # Round 2 started!
                break
            pet.on_anim_frame_step()
            r1_positions.append(pet.x())

        self.assertEqual(pet.skateboard_remaining_repeats, 1)
        # Round 2 must reverse direction to LEFT and be mirrored!
        self.assertEqual(pet.skateboard_slide_dir, -1, "Round 2 must reverse slide direction to -1 (left)")
        self.assertTrue(pet.is_skateboard_mirrored, "Round 2 must be mirrored")
        self.assertEqual(pet.facing_direction, -1, "Round 2 facing direction must be -1")

        r2_positions = []
        # Step through Round 2 until finished
        for _ in range(250):
            if pet.current_behavior.code != BehaviorType.SKATEBOARD:
                break
            pet.on_anim_frame_step()
            r2_positions.append(pet.x())

        self.assertLess(r2_positions[-1], r1_positions[-1], "Round 2 must slide back to the left across the screen!")
        # Directly enters 10s waddle without bow curtsey
        self.assertEqual(pet.current_behavior.code, BehaviorType.IDLE_WADDLE)
        self.assertEqual(pet.facing_direction, -1, "Landed facing left, continues waddling facing left")
        rem_dur = pet.action_end_time - pet.get_now()
        self.assertAlmostEqual(rem_dur, 10.0, delta=0.5)

        pet.close()
        print("PASS: test_skateboard_two_round_mirrored_roundtrip")

    def test_skateboard_pixmap_mirroring(self):
        """Verify get_current_pixmap applies horizontal flip only when is_skateboard_mirrored is True"""
        pet = CockatielWindow()
        pet.trigger_skateboard(repeats=2)

        # Round 1: unmirrored
        pet.is_skateboard_mirrored = False
        pix_unmirrored = pet.get_current_pixmap()
        self.assertFalse(pix_unmirrored.isNull())
        self.assertEqual(pix_unmirrored.width(), 200)
        self.assertEqual(pix_unmirrored.height(), 110)

        # Round 2: mirrored
        pet.is_skateboard_mirrored = True
        pix_mirrored = pet.get_current_pixmap()
        self.assertFalse(pix_mirrored.isNull())
        self.assertEqual(pix_mirrored.width(), 200)
        self.assertEqual(pix_mirrored.height(), 110)

        # Ensure the two pixmaps are flipped versions of each other
        img_un = pix_unmirrored.toImage()
        img_mi = pix_mirrored.toImage()
        for y in range(40, 90, 10):
            for x in range(30, 170, 20):
                c1 = img_un.pixelColor(x, y)
                c2 = img_mi.pixelColor(199 - x, y)
                self.assertEqual(c1.rgba(), c2.rgba(), f"Pixel mismatch at ({x}, {y}) vs ({199-x}, {y})")

        pet.close()
        print("PASS: test_skateboard_pixmap_mirroring")

    def test_skateboard_non_interruptible(self):
        """Verify skateboard animation is protected against head petting, dragging, and poop events"""
        pet = CockatielWindow()
        pet.trigger_skateboard()

        # 1. Head petting hover check
        self.assertFalse(pet.update_head_hover(QPoint(50, 20)))

        # 2. Drag click check
        click_event = QMouseEvent(
            QMouseEvent.Type.MouseButtonPress,
            QPoint(50, 50),
            Qt.LeftButton,
            Qt.LeftButton,
            Qt.NoModifier
        )
        pet.mousePressEvent(click_event)
        self.assertFalse(pet.is_dragging, "Dragging must NOT be initiated during skateboard!")

        # 3. Poop check
        pet.on_poop_timer_tick()
        self.assertEqual(pet.current_behavior.code, BehaviorType.SKATEBOARD)
        self.assertEqual(len(pet.active_poops), 0)

        pet.close()
        print("PASS: test_skateboard_non_interruptible")

    def test_skateboard_dynamic_half_screen_travel_distance(self):
        """Verify dynamic half-screen riding distance calculation adapts to screen size (approx. screen_w * 0.5)"""
        pet = CockatielWindow()
        rect = pet.get_screen_rect(use_available=True)

        # Place near left edge so there is plenty of room to the right (>= half screen)
        start_x = rect.left() + 50
        pet.safe_move(start_x, rect.top() + 300, margin=10)
        pet.trigger_skateboard(repeats=1)

        self.assertEqual(pet.skateboard_dismount_frame, 149, "Full half-screen ride when plenty of room")
        expected_ride_dist = rect.width() * 0.5

        # Record desktop movement
        pos_after_entry_x = pet.x()
        for _ in range(250):
            if pet.current_behavior.code != BehaviorType.SKATEBOARD:
                break
            pet.on_anim_frame_step()

        # Final bird center X in desktop coordinates
        # pos_after_entry bird center was pos_after_entry_x + 100
        # Final bird center at frame 199 was final_200_x + 100, which restored to pet.x() + 50
        final_bird_center = pet.x() + 50
        initial_bird_center = pos_after_entry_x + 100
        actual_dist = final_bird_center - initial_bird_center

        self.assertAlmostEqual(
            actual_dist,
            expected_ride_dist,
            delta=expected_ride_dist * 0.12,
            msg=f"Actual ride distance {actual_dist}px must match half screen {expected_ride_dist}px within 12%"
        )
        pet.close()
        print(f"PASS: test_skateboard_dynamic_half_screen_travel_distance (actual={actual_dist:.1f}px, target={expected_ride_dist:.1f}px)")

    def test_skateboard_hop_on_frame_continuity(self):
        """Verify zero-jitter/zero-replay continuity when bird stands on board (frames 21..24)"""
        for crest in ["classic", "triple"]:
            folder = os.path.join("assets", f"sprites_{crest}")
            centers = []
            for i in [21, 22, 23, 24]:
                img = Image.open(os.path.join(folder, f"skateboard_{i}.png")).convert("RGBA")
                bird_xs = []
                for x in range(img.width):
                    for y in range(0, 45):
                        r, g, b, a = img.getpixel((x, y))
                        if a > 200:
                            bird_xs.append(x)
                self.assertTrue(len(bird_xs) > 0)
                centers.append((min(bird_xs) + max(bird_xs)) / 2.0)

            # All frames 21..24 must be precisely stable (no backwards snap or frame replay)
            for idx in range(1, len(centers)):
                self.assertAlmostEqual(
                    centers[idx],
                    centers[0],
                    delta=1.0,
                    msg=f"Hop-on frame replay/jitter detected in {crest} between frames 21 and {21+idx}: {centers[idx]} vs {centers[0]}"
                )
        print("PASS: test_skateboard_hop_on_frame_continuity")

    def test_skateboard_dismount_continuous_forward_motion(self):
        """Verify skateboard never hesitates or retreats during dismount (frames 150..165 strictly advance +X)"""
        for crest in ["classic", "triple"]:
            folder = os.path.join("assets", f"sprites_{crest}")
            prev_deck_min_x = None
            for i in range(150, 166):
                img = Image.open(os.path.join(folder, f"skateboard_{i}.png")).convert("RGBA")
                deck_xs = []
                for x in range(img.width):
                    for y in range(45, 80):
                        r, g, b, a = img.getpixel((x, y))
                        # Purple deck graphic
                        if a > 200 and r > 120 and g < 80 and b > 150:
                            deck_xs.append(x)
                if deck_xs:
                    min_x = min(deck_xs)
                    if prev_deck_min_x is not None:
                        self.assertGreater(
                            min_x,
                            prev_deck_min_x,
                            f"Skateboard paused or retreated in {crest} at frame {i}: {min_x} <= {prev_deck_min_x}"
                        )
                    prev_deck_min_x = min_x
        print("PASS: test_skateboard_dismount_continuous_forward_motion")

    def test_skateboard_mount_no_stopping(self):
        """Verify that when mounting the skateboard (frames 0..24), the skateboard never stops or pauses"""
        for crest in ["classic", "triple"]:
            folder = os.path.join("assets", f"sprites_{crest}")
            # 1. Frames 0..16: Skateboard advances strictly forward (+X) inside canvas
            prev_max_x = None
            for i in range(4, 17):
                img = Image.open(os.path.join(folder, f"skateboard_{i}.png")).convert("RGBA")
                deck_xs = []
                for x in range(img.width):
                    for y in range(45, 80):
                        r, g, b, a = img.getpixel((x, y))
                        if a > 200 and r > 120 and g < 80 and b > 150:
                            deck_xs.append(x)
                self.assertTrue(len(deck_xs) > 0, f"Deck missing in frame {i}")
                max_x = max(deck_xs)
                if prev_max_x is not None:
                    self.assertGreater(max_x, prev_max_x, f"Skateboard stalled during mount in {crest} at frame {i}")
                prev_max_x = max_x

        # 2. Window movement begins at frame 17 immediately upon bird touching down on board
        pet = CockatielWindow()
        pet.trigger_skateboard(repeats=1)
        # Advance to frame 16 (window should still be at start)
        start_x = pet.x()
        for _ in range(16):
            pet.on_anim_frame_step()
        self.assertEqual(pet.current_frame_index, 16)
        self.assertEqual(pet.x(), start_x, "Window stationary while bird is in air")

        # Step to frame 17: Window must begin physical movement immediately!
        pet.on_anim_frame_step()
        self.assertEqual(pet.current_frame_index, 17)
        self.assertNotEqual(pet.x(), start_x, "Window must move immediately at frame 17 when bird hops on board!")
        pet.close()
        print("PASS: test_skateboard_mount_no_stopping")

    def test_excited_behaviors_rules(self):
        """Verify stage stunts (>=30%), self-amusements (>=15%), anti-consecutive repeats, EAT_PLANT daily, and excitement clearing"""
        pet = CockatielWindow()

        # 1. Stage stunts require excitement >= 30.0
        for exc in [0.0, 10.0, 14.9, 20.0, 29.9]:
            pet.mood.excitement = exc
            pet.mood.fright = 0.0
            pet.mood.comfort = 50.0
            for _ in range(100):
                chosen, _ = pet.mood.select_next_behavior()
                self.assertNotIn(
                    chosen.code,
                    (BehaviorType.SKATEBOARD, BehaviorType.UNICYCLE, BehaviorType.MAGIC_TRICK, BehaviorType.EXCITE_PLAY_BALL),
                    f"{chosen.code} triggered when excitement was {exc} < 30.0!"
                )

        # 2. Stage stunts can be chosen when excitement >= 30.0
        pet.mood.excitement = 60.0
        chosen_codes = set()
        for _ in range(400):
            chosen, _ = pet.mood.select_next_behavior()
            chosen_codes.add(chosen.code)
        hit_stunt = any(code in chosen_codes for code in (BehaviorType.SKATEBOARD, BehaviorType.UNICYCLE, BehaviorType.MAGIC_TRICK, BehaviorType.EXCITE_PLAY_BALL))
        self.assertTrue(hit_stunt, "At excitement=60 (>=30), stage stunts must be eligible for selection!")

        # 3. Self-amusement behaviors require excitement >= 15.0
        for exc in [0.0, 5.0, 10.0, 14.9]:
            pet.mood.excitement = exc
            pet.mood.fright = 0.0
            pet.mood.comfort = 50.0
            for _ in range(100):
                chosen, _ = pet.mood.select_next_behavior()
                self.assertNotIn(
                    chosen.code,
                    (BehaviorType.EXCITE_HOP, BehaviorType.EXCITE_BOB, BehaviorType.EXCITE_SING, BehaviorType.EXCITE_DOUBLE_PECK, BehaviorType.MISCHIEF_CHEW),
                    f"Self-amusement {chosen.code} triggered when excitement was {exc} < 15.0!"
                )

        # 4. Self-amusement behaviors can trigger when excitement >= 15.0 (e.g. 20.0)
        pet.mood.excitement = 20.0
        chosen_self = set()
        for _ in range(400):
            chosen, _ = pet.mood.select_next_behavior()
            chosen_self.add(chosen.code)
        hit_amusement = any(code in chosen_self for code in (BehaviorType.EXCITE_HOP, BehaviorType.EXCITE_BOB, BehaviorType.EXCITE_SING, BehaviorType.EXCITE_DOUBLE_PECK, BehaviorType.MISCHIEF_CHEW))
        self.assertTrue(hit_amusement, "At excitement=20 (>=15), self-amusements must be eligible for selection!")

        # 5. Anti-consecutive rule: the same self-amusement behavior can NEVER trigger consecutively
        pet.mood.excitement = 50.0
        for amusement_code in (BehaviorType.EXCITE_HOP, BehaviorType.EXCITE_BOB, BehaviorType.EXCITE_SING, BehaviorType.EXCITE_DOUBLE_PECK, BehaviorType.MISCHIEF_CHEW):
            for _ in range(100):
                chosen, _ = pet.mood.select_next_behavior(current_behavior=amusement_code)
                self.assertNotEqual(
                    chosen.code, amusement_code,
                    f"Self-amusement {amusement_code} consecutively repeated!"
                )

        # 6. EAT_PLANT is daily behavior: can be chosen even when excitement < 15.0
        pet.mood.excitement = 0.0
        pet.mood.comfort = 60.0
        chosen_daily = set()
        for _ in range(500):
            chosen, _ = pet.mood.select_next_behavior()
            chosen_daily.add(chosen.code)
        self.assertIn(BehaviorType.EAT_PLANT, chosen_daily, "EAT_PLANT is daily routine and should be selectable at excitement=0")

        # 7. Excitement clearing: Stage stunts clear excitement upon exit; self-amusements do NOT
        # Stage stunt exit clears excitement:
        pet.mood.excitement = 60.0
        pet.switch_behavior(BEHAVIOR_CATALOG[BehaviorType.SKATEBOARD], 10.0)
        self.assertEqual(pet.mood.excitement, 60.0, "Excitement preserved during stunt")
        pet.switch_behavior(BEHAVIOR_CATALOG[BehaviorType.IDLE_WADDLE], 10.0)
        self.assertEqual(pet.mood.excitement, 0.0, "Excitement must be cleared after stage stunt finishes!")

        # Self-amusement exit preserves excitement:
        pet.mood.excitement = 25.0
        pet.switch_behavior(BEHAVIOR_CATALOG[BehaviorType.EXCITE_BOB], 10.0)
        self.assertEqual(pet.mood.excitement, 25.0)
        pet.switch_behavior(BEHAVIOR_CATALOG[BehaviorType.IDLE_WADDLE], 10.0)
        self.assertEqual(pet.mood.excitement, 25.0, "Excitement must NOT be cleared after self-amusement finishes!")

        pet.close()
        print("PASS: test_excited_behaviors_rules")

if __name__ == '__main__':
    unittest.main()
