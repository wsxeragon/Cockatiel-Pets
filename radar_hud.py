import math
import time
from functools import partial
from PySide6.QtCore import Qt, QPointF
from PySide6.QtGui import QPainter, QColor, QPen, QBrush, QPolygonF, QFont
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QHBoxLayout, QPushButton, QProgressBar,
                               QScrollArea, QGridLayout)
from config import is_dev_mode
from models import BehaviorType, BEHAVIOR_CATALOG

class RadarHUD(QWidget):
    """四维心态雷达图与心理监视器 HUD 窗口"""

    # 调试面板行为注入表：(动作 key, 按钮文案)
    # 与右键菜单里"仅开发调试模式显示"的那批动作保持一一对应（桌霸恶作剧在菜单里也被隐藏，故不列）。
    DEBUG_ACTIONS = [
        ("sing", "🎵 吹口哨"),
        ("hop", "🦘 雀跃小跳"),
        ("bonk", "🥁 敲击屏幕"),
        ("double_peck", "⚡ 连环双击"),
        ("play_ball", "🔴 杂技踩球"),
        ("eat_plant", "🌿 啃咬植物"),
        ("magic", "🎩 变魔术"),
        ("skateboard", "🛹 极限滑板"),
        ("unicycle", "🎪 独轮杂技"),
        ("poop", "💩 触发拉屎"),
        ("peck", "🌾 闲置啄食"),
        ("waddle", "🚶 摇晃溜达"),
        ("preen", "🪶 整理羽毛"),
        ("fluff", "🐡 蓬成毛球"),
        ("yawn", "🥱 打大哈欠"),
        ("fly", "🕊️ 舒展飞翔"),
        ("fright", "⚡ 戳身反咬"),
        ("clean_poop", "🧹 一键铲屎"),
        ("toggle_poop", "🚯 禁止随地大小便"),
        ("reset_mood", "🔄 重置心态"),
    ]

    def __init__(self, pet_window):
        super().__init__()
        self.pet = pet_window
        self.setWindowTitle("🐤 玄凤鹦鹉心理雷达监视器")
        self.dev_mode = is_dev_mode()
        if not self.dev_mode:
            # 发布版的仪表盘尺寸保持不变
            self.setFixedSize(320, 390)
        self.setWindowFlags(Qt.Window | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_ShowWithoutActivating)
        # 上一次重绘雷达用的四维取值，用来避免数值没变时的空重绘
        self._radar_key = None

        self.setStyleSheet("""
            QWidget {
                background-color: #1e1e24;
                color: #e0e0e0;
                font-family: 'Segoe UI', 'Microsoft YaHei', sans-serif;
            }
            QLabel {
                font-size: 13px;
            }
            QPushButton {
                background-color: #2e303e;
                border: 1px solid #45475a;
                border-radius: 6px;
                padding: 6px 12px;
                font-size: 12px;
                color: #cdd6f4;
            }
            QPushButton:hover {
                background-color: #3b3e52;
                border-color: #89b4fa;
            }
            QPushButton:pressed {
                background-color: #181825;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(10)

        # 标题与当前状态
        self.title_label = QLabel("<b>🐤 玄凤心态实时监视</b>")
        self.title_label.setStyleSheet("font-size: 15px; color: #f9e2af;")
        layout.addWidget(self.title_label)

        self.state_label = QLabel("当前行为: 发呆眨眼 (剩余 3.0s)")
        self.state_label.setStyleSheet("color: #89b4fa; font-size: 13px;")
        layout.addWidget(self.state_label)

        self.last_event_label = QLabel("最新事件: 初始就绪")
        self.last_event_label.setStyleSheet("color: #a6adc8; font-size: 12px;")
        layout.addWidget(self.last_event_label)

        # 雷达图渲染画布区域
        self.radar_canvas = RadarCanvas(self.pet.mood)
        layout.addWidget(self.radar_canvas)

        self.fatigue_label = QLabel("疲劳 0 / 100")
        self.fatigue_label.setStyleSheet("color: #f5c2e7; font-size: 12px;")
        layout.addWidget(self.fatigue_label)
        self.fatigue_bar = QProgressBar()
        self.fatigue_bar.setRange(0, 100)
        self.fatigue_bar.setTextVisible(False)
        self.fatigue_bar.setStyleSheet(
            "QProgressBar { background: #313244; border: 0; height: 8px; }"
            "QProgressBar::chunk { background: #f5c2e7; }")
        layout.addWidget(self.fatigue_bar)

        # 调试测试控制按钮 (仅开发调试模式显示)
        if self.dev_mode:
            ctrl_title = QLabel("<b>调试行为注入测试:</b>")
            ctrl_title.setStyleSheet("font-size: 12px; color: #bac2de;")
            layout.addWidget(ctrl_title)

            btn_row1 = QHBoxLayout()
            self.btn_pet = QPushButton("摸头 (+舒适)")
            self.btn_pet.clicked.connect(self.on_pet_clicked)
            self.btn_poke = QPushButton("戳身子 (+惊吓)")
            self.btn_poke.clicked.connect(self.on_poke_clicked)
            btn_row1.addWidget(self.btn_pet)
            btn_row1.addWidget(self.btn_poke)
            layout.addLayout(btn_row1)

            btn_row2 = QHBoxLayout()
            self.btn_idle_charge = QPushButton("模拟长时闲置 (+精力)")
            self.btn_idle_charge.clicked.connect(self.on_idle_charge_clicked)
            self.btn_force_dance = QPushButton("强制兴奋自嗨")
            self.btn_force_dance.clicked.connect(self.on_force_dance_clicked)
            btn_row2.addWidget(self.btn_idle_charge)
            btn_row2.addWidget(self.btn_force_dance)
            layout.addLayout(btn_row2)

            btn_row3 = QHBoxLayout()
            self.btn_force_sleep = QPushButton("💤 强制睡眠")
            self.btn_force_sleep.setStyleSheet("""
                QPushButton {
                    background-color: #3b2d42;
                    border: 1px solid #f5c2e7;
                    color: #f5c2e7;
                    font-weight: bold;
                    padding: 6px 10px;
                }
                QPushButton:hover {
                    background-color: #4e3857;
                    border-color: #cba6f7;
                }
                QPushButton:pressed {
                    background-color: #241a29;
                }
            """)
            self.btn_force_sleep.clicked.connect(self.on_force_sleep_clicked)

            self.btn_clear_fatigue = QPushButton("⚡ 清空疲劳")
            self.btn_clear_fatigue.setStyleSheet("""
                QPushButton {
                    background-color: #263832;
                    border: 1px solid #a6e3a1;
                    color: #a6e3a1;
                    font-weight: bold;
                    padding: 6px 10px;
                }
                QPushButton:hover {
                    background-color: #334d44;
                    border-color: #94e2d5;
                }
                QPushButton:pressed {
                    background-color: #172420;
                }
            """)
            self.btn_clear_fatigue.clicked.connect(self.on_clear_fatigue_clicked)

            btn_row3.addWidget(self.btn_force_sleep)
            btn_row3.addWidget(self.btn_clear_fatigue)
            layout.addLayout(btn_row3)

            # 行为动作注入面板：与右键菜单（开发调试模式）里的动作一一对应
            action_title = QLabel("<b>🧪 行为动作注入（同右键菜单）:</b>")
            action_title.setStyleSheet("font-size: 12px; color: #bac2de;")
            layout.addWidget(action_title)

            scroll = QScrollArea()
            scroll.setWidgetResizable(True)
            scroll.setFixedHeight(246)
            scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
            scroll.setStyleSheet(
                "QScrollArea { border: 1px solid #313244; border-radius: 6px; background: #1e1e24; }"
                "QScrollArea > QWidget > QWidget { background: #1e1e24; }")
            panel = QWidget()
            grid = QGridLayout(panel)
            grid.setContentsMargins(6, 6, 6, 6)
            grid.setSpacing(5)
            self.btn_toggle_poop = None
            for idx, (key, label) in enumerate(self.DEBUG_ACTIONS):
                btn = QPushButton(label)
                btn.setCursor(Qt.PointingHandCursor)
                btn.setStyleSheet("QPushButton { padding: 5px 4px; font-size: 12px; }")
                if key == "toggle_poop":
                    btn.setCheckable(True)
                    btn.setChecked(self.pet.is_poop_disabled)
                    btn.setText(self._poop_toggle_text())
                    self.btn_toggle_poop = btn
                btn.clicked.connect(partial(self.on_debug_action, key))
                grid.addWidget(btn, idx // 2, idx % 2)
            scroll.setWidget(panel)
            layout.addWidget(scroll)

            # 内容收口：宽度固定 320，高度按实际内容撑开（发布版不走这里，仍是 320x390）
            self.adjustSize()
            self.setFixedSize(320, max(560, self.sizeHint().height()))

    def on_pet_clicked(self):
        self.pet.handle_pet_head()

    def on_poke_clicked(self):
        self.pet.handle_touch_body()

    def on_idle_charge_clicked(self):
        self.pet.mood.excitement = min(100.0, self.pet.mood.excitement + 35.0)
        self.pet.mood.comfort = max(10.0, self.pet.mood.comfort - 15.0)
        self.last_event_label.setText("最新事件: 注入长时闲置冲动 (+精力)")

    def on_force_dance_clicked(self):
        self.pet.mood.excitement = 95.0
        self.pet.mood.comfort = 40.0
        self.pet.mood.fright = 0.0
        self.last_event_label.setText("最新事件: 兴奋值拉满至 95")

    def _poop_toggle_text(self) -> str:
        if self.pet.is_poop_disabled:
            return "🚯 禁止随地大小便：开"
        return "💩 禁止随地大小便：关"

    def _refresh_poop_toggle(self):
        btn = getattr(self, "btn_toggle_poop", None)
        if btn is not None:
            btn.setChecked(self.pet.is_poop_disabled)
            btn.setText(self._poop_toggle_text())

    def _wake_if_sleeping(self, reason: str):
        if self.pet.current_behavior.code in (BehaviorType.REST_SLEEP, BehaviorType.REST_FALL_ASLEEP):
            self.pet.wake_up(reason)

    def on_debug_action(self, key: str):
        """行为动作注入：逐条对齐右键菜单（开发调试模式）里的动作语义。"""
        pet = self.pet

        if key == "sing":
            self._wake_if_sleeping("被歌声唤醒了")
            pet.mood.excitement = 90.0
            pet.switch_behavior(BEHAVIOR_CATALOG[BehaviorType.EXCITE_SING], None,
                                "控制面板注入：被主人逗乐，开心大声独唱！")
        elif key == "hop":
            pet.trigger_hop("控制面板注入：欢快移动连环小跳！")
        elif key == "bonk":
            pet.trigger_bonk("控制面板注入：靠边敲击屏幕！")
        elif key == "double_peck":
            self._wake_if_sleeping("被叫醒起来连环啄米")
            pet.mood.excitement = max(pet.mood.excitement, 70.0)
            pet.switch_behavior(BEHAVIOR_CATALOG[BehaviorType.EXCITE_DOUBLE_PECK], None,
                                "控制面板注入：兴奋连环双击啄桌！")
        elif key == "play_ball":
            self._wake_if_sleeping("被红球吸引醒来！")
            pet.mood.excitement = max(pet.mood.excitement, 75.0)
            pet.switch_behavior(BEHAVIOR_CATALOG[BehaviorType.EXCITE_PLAY_BALL], None,
                                "控制面板注入：兴奋杂技踩球！")
        elif key == "eat_plant":
            self._wake_if_sleeping("被植物吸引醒来！")
            pet.trigger_eat_plant("控制面板注入：趣味啃咬植物！")
        elif key == "magic":
            self._wake_if_sleeping("被魔术表演唤醒！")
            pet.trigger_magic_trick("控制面板注入：红色幕布变魔术！")
        elif key == "skateboard":
            self._wake_if_sleeping("被滑板吸引醒来！")
            pet.trigger_skateboard("控制面板注入：极限滑板炫技！")
        elif key == "unicycle":
            self._wake_if_sleeping("被独轮杂技吸引醒来！")
            pet.trigger_unicycle("控制面板注入：独轮杂技特技！")
        elif key == "poop":
            pet.trigger_poop("控制面板注入：后退深蹲排便！")
        elif key == "peck":
            self._wake_if_sleeping("被叫醒起来啄米")
            pet.switch_behavior(BEHAVIOR_CATALOG[BehaviorType.IDLE_PECK], None,
                                "控制面板注入：闲置自然啄食！")
        elif key == "waddle":
            self._wake_if_sleeping("被叫醒起来溜达")
            pet.switch_behavior(BEHAVIOR_CATALOG[BehaviorType.IDLE_WADDLE], None,
                                "控制面板注入：摇晃溜达漫步！")
        elif key == "preen":
            self._wake_if_sleeping("被叫醒起来整理羽毛")
            pet.switch_behavior(BEHAVIOR_CATALOG[BehaviorType.COMFORT_PREEN], None,
                                "控制面板注入：转头埋背整理羽毛！")
        elif key == "fluff":
            self._wake_if_sleeping("被叫醒起来蓬成毛球")
            pet.switch_behavior(BEHAVIOR_CATALOG[BehaviorType.COMFORT_FLUFF], None,
                                "控制面板注入：舒适蓬成毛球！")
        elif key == "yawn":
            pet.trigger_yawn("控制面板注入：伸脖打大哈欠！")
        elif key == "fly":
            pet.start_flight(panic=False, roam=True)
        elif key == "fright":
            pet.handle_touch_body()
        elif key == "clean_poop":
            pet.clean_all_poop("控制面板注入：一键铲屎！")
        elif key == "toggle_poop":
            pet.toggle_disable_poop()
            self._refresh_poop_toggle()
        elif key == "reset_mood":
            pet.mood.fright = 0.0
            pet.last_feedback = "控制面板注入：惊吓值已重置为平静"
            if pet.hud_window:
                pet.hud_window.update_view()

        self.update_view()

    def on_force_sleep_clicked(self):
        self.pet.force_sleep("控制面板注入：疲劳度拉满至 100，直接进入睡眠")
        self.last_event_label.setText("最新事件: 强制睡眠 (疲劳拉满至 100)")

    def on_clear_fatigue_clicked(self):
        self.pet.clear_fatigue("控制面板注入：疲劳度已直接清空！")
        self.last_event_label.setText("最新事件: 清空疲劳 (疲劳归零)")

    @staticmethod
    def _set_label(label, text: str):
        """内容没变就不 setText，省掉一次无谓的布局与重绘。"""
        if label.text() != text:
            label.setText(text)

    def update_view(self):
        """只在显示内容真的变化时才更新控件 / 重绘雷达。

        这个函数被主循环每 100ms 调一次；以前每次都无条件重绘 320x390 的雷达画布，
        等于每秒 10 次空重绘——桌宠压在游戏画面上时这些合成都会拖帧。
        """
        m = self.pet.mood
        curr_b = self.pet.current_behavior
        rem_t = max(0.0, self.pet.action_end_time - self.pet.get_now())
        # 10 秒内才显示一位小数；否则整数秒（否则这个标签每秒要重绘 10 次）
        rem_txt = f"{rem_t:.1f}" if rem_t < 10.0 else f"{rem_t:.0f}"
        self._set_label(self.state_label, f"当前行为: <b>{curr_b.name_cn}</b> (剩余 {rem_txt}s)")
        self._set_label(self.last_event_label, f"最新事件: {self.pet.last_feedback}")
        self._set_label(self.fatigue_label, f"疲劳 {m.fatigue:.1f} / 100")

        bar_val = round(m.fatigue)
        if bar_val != self.fatigue_bar.value():
            self.fatigue_bar.setValue(bar_val)

        # 雷达按"取整后的四维值"判断是否需要重绘，视觉上看不出差别
        key = (int(m.fright), int(m.excitement), int(m.comfort), int(m.calm))
        if key != self._radar_key:
            self._radar_key = key
            self.radar_canvas.update()

class RadarCanvas(QWidget):
    """绘制四维心态雷达图的绘图组件"""
    def __init__(self, mood):
        super().__init__()
        self.mood = mood
        self.setMinimumHeight(210)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        w = self.width()
        h = self.height()
        cx, cy = w / 2, h / 2
        radius = min(cx, cy) - 34

        # 四个维度的轴定义:
        # 上: 惊吓(Fright)
        # 右: 兴奋(Excitement)
        # 下: 舒适(Comfort)
        # 左: 平静(Calm)
        axes = [
            ("惊吓 (F)", self.mood.fright, 0, -1, QColor(243, 139, 168)),     # 樱花粉红
            ("兴奋 (E)", self.mood.excitement, 1, 0, QColor(249, 226, 175)), # 亮金黄
            ("舒适 (Co)", self.mood.comfort, 0, 1, QColor(166, 227, 161)),   # 嫩绿
            ("平静 (Ca)", self.mood.calm, -1, 0, QColor(137, 180, 250)),     # 浅天蓝
        ]

        # 1. 绘制同心多边形背景网格 (25%, 50%, 75%, 100%)
        painter.setPen(QPen(QColor(69, 71, 90, 180), 1, Qt.DashLine))
        painter.setBrush(Qt.NoBrush)
        for step in [0.25, 0.5, 0.75, 1.0]:
            r = radius * step
            pts = [
                QPointF(cx, cy - r),
                QPointF(cx + r, cy),
                QPointF(cx, cy + r),
                QPointF(cx - r, cy),
            ]
            painter.drawPolygon(QPolygonF(pts))

        # 2. 绘制轴线与文字标签
        font = QFont("Microsoft YaHei", 9)
        painter.setFont(font)
        for label, val, dx, dy, color in axes:
            end_x = cx + dx * radius
            end_y = cy + dy * radius
            painter.setPen(QPen(QColor(88, 91, 112), 1))
            painter.drawLine(QPointF(cx, cy), QPointF(end_x, end_y))

            # 绘制标签文字
            painter.setPen(QPen(color))
            val_str = f"{label} {int(val)}"
            if dx == 0 and dy == -1:
                painter.drawText(cx - 36, cy - radius - 8, val_str)
            elif dx == 1 and dy == 0:
                painter.drawText(cx + radius + 8, cy + 4, val_str)
            elif dx == 0 and dy == 1:
                painter.drawText(cx - 36, cy + radius + 18, val_str)
            elif dx == -1 and dy == 0:
                painter.drawText(cx - radius - 75, cy + 4, val_str)

        # 3. 绘制当前心态多边形填充
        poly_points = []
        for _, val, dx, dy, _ in axes:
            r_val = radius * (max(2.0, min(100.0, val)) / 100.0)
            poly_points.append(QPointF(cx + dx * r_val, cy + dy * r_val))

        mood_poly = QPolygonF(poly_points)
        fill_color = QColor(249, 226, 175, 90)  # 半透明玄凤黄色填充
        painter.setBrush(QBrush(fill_color))
        painter.setPen(QPen(QColor(249, 226, 175, 220), 2))
        painter.drawPolygon(mood_poly)

        # 顶点圆点
        for pt in poly_points:
            painter.setBrush(QBrush(QColor(255, 255, 255)))
            painter.setPen(QPen(QColor(249, 226, 175), 2))
            painter.drawEllipse(pt, 3, 3)
