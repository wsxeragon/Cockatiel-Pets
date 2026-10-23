import os
import random
from typing import Optional, List
from pathlib import Path

from PySide6.QtCore import Qt, QTimer, QPoint, QRect, Signal
from PySide6.QtGui import QPixmap, QPainter, QCursor, QMouseEvent
from PySide6.QtWidgets import QWidget, QApplication
from config import get_base_dir

class PoopItemWindow(QWidget):
    """
    独立大便实体悬浮窗 (无边框、置顶、透明通道)。
    支持：
    1. 自由落体物理 (从高处坠落至地面/指定深度并弹性压扁着地)
    2. 点击清理动画 (鼠标左键轻点，播放金色星芒爆裂烟雾消散)
    3. 保持在屏幕工作区范围内，不越界
    """
    cleaned = Signal(object) # emit self when cleaned up

    def __init__(self, start_x: int, start_y: int, target_y: Optional[int] = None, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.SubWindow)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setAttribute(Qt.WA_DeleteOnClose, True)
        self.setFixedSize(26, 22)
        self.setCursor(Qt.PointingHandCursor)
        self.setToolTip("💩 湿漉漉的马赛克大便\n点击即可清理干净~")

        # 载入大便状态精灵
        self.sprites = self._load_poop_sprites()

        # 状态机: "fall" -> "land" -> "idle" -> "clean"
        self.state: str = "idle"
        self.clean_frame_idx: int = 0

        # 计算屏幕有效工作区 (避开任务栏)
        screen = QApplication.screenAt(QPoint(start_x, start_y)) or QApplication.primaryScreen()
        screen_geo = screen.availableGeometry() if screen else QRect(0, 0, 1920, 1080)
        max_y = screen_geo.bottom() - 20

        # 计算目标落点 (如果小鸟停留在高处，随机下落一段距离或直达底部；若已在地面则微距落地)
        self.pos_x = float(start_x)
        self.curr_y = float(start_y)

        if target_y is None:
            dist_to_bottom = max_y - start_y
            if dist_to_bottom <= 12:
                # 鸟基本就在地面上，直接原地生成
                self.target_y = float(min(max_y, start_y + 4))
            else:
                # 鸟在较高位置，随机下落 60 ~ 380px (或直达屏幕底端)
                random_drop = random.randint(60, 380)
                self.target_y = float(min(max_y, start_y + random_drop))
        else:
            self.target_y = float(min(max_y, target_y))

        # 定位初始位置
        self.move(int(self.pos_x), int(self.curr_y))

        # 是否需要下落动画
        if self.target_y > self.curr_y + 4:
            self.state = "fall"
            self.vy = 0.0
            self.gravity = 1.6
            self.fall_timer = QTimer(self)
            self.fall_timer.timeout.connect(self._on_fall_tick)
            self.fall_timer.start(25) # 40 FPS
        else:
            self.curr_y = self.target_y
            self.move(int(self.pos_x), int(self.curr_y))
            self.state = "idle"

        # 清理动画定时器
        self.clean_timer = QTimer(self)
        self.clean_timer.timeout.connect(self._on_clean_tick)

        self.show()

    def _load_poop_sprites(self) -> dict:
        poop_dir = Path(get_base_dir()) / "assets" / "poop"
        sprites = {}
        for name in ["poop_idle", "poop_fall", "poop_land", "poop_clean_0", "poop_clean_1", "poop_clean_2", "poop_clean_3"]:
            path = poop_dir / f"{name}.png"
            if path.exists():
                sprites[name] = QPixmap(str(path))
            else:
                sprites[name] = QPixmap()
        return sprites

    def _on_fall_tick(self):
        """下落物理动力学"""
        if self.state != "fall":
            return
        self.vy += self.gravity
        self.curr_y += self.vy

        if self.curr_y >= self.target_y:
            # 触地冲击瞬间 (触发 1 帧 squashed land 态)
            self.curr_y = self.target_y
            self.state = "land"
            self.fall_timer.stop()
            self.move(int(self.pos_x), int(self.curr_y))
            self.update()
            # 90ms 缓冲后恢复自然静止形态
            QTimer.singleShot(90, self._on_land_settled)
            return

        self.move(int(self.pos_x), int(self.curr_y))
        self.update()

    def _on_land_settled(self):
        if self.state == "land":
            self.state = "idle"
            self.update()

    def mousePressEvent(self, event: QMouseEvent):
        """点击大便触发清理消散动效"""
        if event.button() == Qt.LeftButton:
            if self.state != "clean":
                self.start_cleanup()
            event.accept()
        else:
            super().mousePressEvent(event)

    def start_cleanup(self):
        """启动金色星芒闪烁与消散动画"""
        if hasattr(self, "fall_timer") and self.fall_timer.isActive():
            self.fall_timer.stop()
        self.state = "clean"
        self.clean_frame_idx = 0
        self.clean_timer.start(100) # 100ms per sparkle frame
        self.update()

    def _on_clean_tick(self):
        self.clean_frame_idx += 1
        if self.clean_frame_idx >= 4:
            self.clean_timer.stop()
            self.cleaned.emit(self)
            self.close()
        else:
            self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing, False)

        pix: Optional[QPixmap] = None
        if self.state == "fall":
            pix = self.sprites.get("poop_fall")
        elif self.state == "land":
            pix = self.sprites.get("poop_land")
        elif self.state == "clean":
            frame_name = f"poop_clean_{self.clean_frame_idx}"
            pix = self.sprites.get(frame_name)
        else:
            pix = self.sprites.get("poop_idle")

        if pix and not pix.isNull():
            # 居中贴合在窗口底部
            draw_x = (self.width() - pix.width()) // 2
            draw_y = self.height() - pix.height()
            painter.drawPixmap(draw_x, draw_y, pix)
