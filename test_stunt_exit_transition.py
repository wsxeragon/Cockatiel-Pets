"""滑板/独轮大舞台收尾：200x110 -> 100x80 缩窗口这一帧不能闪残图。

历史问题：收尾时在 setUpdatesEnabled(False) 区间里直接 setGeometry，系统拿旧的
大画布按新窗口裁一刀，桌面上偶尔闪过一帧被裁歪的鸟（多轮回数越容易撞上）。

现在的约定：
1. 缩窗口推迟到画面刷新恢复之后；
2. 先把"缩回后的画面"按最终屏幕坐标预合成进旧尺寸画布并同步 repaint；
3. 过渡期间任何一次 paintEvent 的窗口尺寸与贴图尺寸都必须一致（不允许整帧丢弃）。
"""
import os
import sys
import unittest

# 离屏跑，避免测试时在桌面上闪窗口；repaint() 在离屏平台同样会走 paintEvent
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtGui import QImage
from PySide6.QtWidgets import QApplication

from models import BehaviorType
from cockatiel_window import CockatielWindow


class RecordingWindow(CockatielWindow):
    def __init__(self):
        super().__init__()
        self.paint_log = []          # (behavior, win_w, win_h, pix_w, pix_h, used_transition)
        self.transition_canvases = []  # (canvas, offset_x, offset_y, old_x, old_y, target_x, target_y)

    def _compose_transition(self, target_x, target_y):
        old_x, old_y = self.x(), self.y()
        canvas = super()._compose_transition(target_x, target_y)
        if canvas is not None and not canvas.isNull():
            self.transition_canvases.append(
                (canvas.copy(), target_x - old_x, target_y - old_y, old_x, old_y, target_x, target_y))
        return canvas

    def paintEvent(self, event):
        used_transition = (
            self._transition_pixmap is not None
            and self._transition_pixmap.width() == self.width()
            and self._transition_pixmap.height() == self.height()
        )
        pix = self.get_current_pixmap()
        if used_transition:
            drawn_w, drawn_h = self._transition_pixmap.width(), self._transition_pixmap.height()
        else:
            drawn_w, drawn_h = pix.width(), pix.height()
        # (行为, 窗口宽, 窗口高, 实际贴出的贴图宽, 实际贴出的贴图高, 是否用了过渡帧, 是否整帧空绘)
        self.paint_log.append((self.current_behavior.code.name, self.width(), self.height(),
                               drawn_w, drawn_h, used_transition,
                               not used_transition and pix.isNull()))
        super().paintEvent(event)


class TestStuntExitTransition(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance()
        if cls.app is None:
            cls.app = QApplication(sys.argv)

    def _finish_stunt(self, trigger, last_frame, final_round=False):
        pet = RecordingWindow()
        pet.show()                     # repaint() 只对可见窗口生效
        pet.safe_move(400, 400, margin=10)
        trigger(pet)
        if final_round:
            pet.skateboard_remaining_repeats = 1   # 已是最后一轮，下一帧就谢幕
        pet.current_frame_index = last_frame
        self.app.processEvents()
        pet.paint_log.clear()
        pet.transition_canvases.clear()
        pet.on_anim_frame_step()
        self.app.processEvents()
        return pet

    def _check_transition(self, pet, stage_size, stage_name):
        self.assertEqual(pet.current_behavior.code, BehaviorType.IDLE_BLINK)
        self.assertEqual((pet.width(), pet.height()), (100, 80),
                         f"{stage_name}收尾后窗口必须回到标准 100x80 画布")

        self.assertTrue(pet.transition_canvases, f"{stage_name}收尾必须先合成过渡帧")
        canvas, off_x, off_y, old_x, old_y, target_x, target_y = pet.transition_canvases[-1]
        self.assertEqual((canvas.width(), canvas.height()), stage_size,
                         "过渡帧必须是缩小前的旧画布尺寸")
        self.assertTrue(any(row[5] for row in pet.paint_log),
                        "缩窗口前必须用过渡帧 repaint 过一次")

        for beh, ww, wh, pw, ph, _used, blank in pet.paint_log:
            self.assertFalse(blank, f"{beh} 出现整帧空绘（窗口尺寸与贴图尺寸对不上被丢弃），会闪空")
            self.assertEqual((ww, wh), (pw, ph),
                             f"{beh} 贴出的画面 {pw}x{ph} 与窗口 {ww}x{wh} 不一致，会闪残图")

        # 过渡帧里"将来会被新窗口露出来"的那块，必须和收尾后真正画出来的 idle 帧逐像素一致
        composed = canvas.toImage().convertToFormat(QImage.Format_ARGB32)
        idle = pet.get_current_pixmap().toImage().convertToFormat(QImage.Format_ARGB32)
        self.assertEqual((idle.width(), idle.height()), (100, 80))
        diff = 0
        for y in range(idle.height()):
            for x in range(idle.width()):
                if composed.pixel(x + off_x, y + off_y) != idle.pixel(x, y):
                    diff += 1
        self.assertEqual(diff, 0, f"过渡帧与收尾后的显示不一致（{diff} 个像素不同），会看到跳帧")

    def test_skateboard_exit_uses_composed_transition_frame(self):
        pet = self._finish_stunt(lambda p: p.trigger_skateboard("测试收尾", repeats=1), 199)
        self._check_transition(pet, (200, 110), "滑板")
        pet.close()

    def test_skateboard_multiround_exit_uses_composed_transition_frame(self):
        pet = self._finish_stunt(lambda p: p.trigger_skateboard("测试多轮收尾", repeats=3), 199,
                                 final_round=True)
        self.assertEqual(pet.skateboard_total_repeats, 3)
        self._check_transition(pet, (200, 110), "多轮滑板")
        pet.close()

    def test_unicycle_exit_uses_composed_transition_frame(self):
        pet = self._finish_stunt(lambda p: p.trigger_unicycle("测试收尾"), 499)
        self._check_transition(pet, (240, 160), "独轮")
        pet.close()


if __name__ == '__main__':
    unittest.main()
