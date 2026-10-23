import math
import time
from PySide6.QtCore import Qt, QPointF
from PySide6.QtGui import QPainter, QColor, QPen, QBrush, QPolygonF, QFont
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QHBoxLayout, QPushButton, QProgressBar
from config import is_dev_mode

class RadarHUD(QWidget):
    """四维心态雷达图与心理监视器 HUD 窗口"""
    def __init__(self, pet_window):
        super().__init__()
        self.pet = pet_window
        self.setWindowTitle("🐤 玄凤鹦鹉心理雷达监视器")
        self.dev_mode = is_dev_mode()
        if self.dev_mode:
            self.setFixedSize(320, 560)
        else:
            self.setFixedSize(320, 390)
        self.setWindowFlags(Qt.Window | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_ShowWithoutActivating)

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
            self.btn_bonk = QPushButton("🥁 敲击屏幕")
            self.btn_bonk.setStyleSheet("""
                QPushButton {
                    background-color: #3e3828;
                    border: 1px solid #f9e2af;
                    color: #f9e2af;
                    font-weight: bold;
                    padding: 6px 8px;
                }
                QPushButton:hover {
                    background-color: #554b32;
                    border-color: #fab387;
                }
                QPushButton:pressed {
                    background-color: #2b2518;
                }
            """)
            self.btn_bonk.clicked.connect(self.on_bonk_clicked)
            btn_row2.addWidget(self.btn_idle_charge)
            btn_row2.addWidget(self.btn_force_dance)
            btn_row2.addWidget(self.btn_bonk)
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

            btn_row4 = QHBoxLayout()
            self.btn_hop = QPushButton("🦘 雀跃小跳")
            self.btn_hop.setStyleSheet("""
                QPushButton {
                    background-color: #263842;
                    border: 1px solid #89dceb;
                    color: #89dceb;
                    font-weight: bold;
                    padding: 6px 8px;
                }
                QPushButton:hover {
                    background-color: #334c59;
                    border-color: #a6e3a1;
                }
                QPushButton:pressed {
                    background-color: #17242a;
                }
            """)
            self.btn_hop.clicked.connect(self.on_hop_clicked)

            self.btn_fly = QPushButton("🕊️ 舒展飞翔")
            self.btn_fly.setStyleSheet("""
                QPushButton {
                    background-color: #2a3447;
                    border: 1px solid #b4befe;
                    color: #b4befe;
                    font-weight: bold;
                    padding: 6px 8px;
                }
                QPushButton:hover {
                    background-color: #374259;
                    border-color: #cdd6f4;
                }
                QPushButton:pressed {
                    background-color: #1a2233;
                }
            """)
            self.btn_fly.clicked.connect(self.on_fly_clicked)

            btn_row4.addWidget(self.btn_hop)
            btn_row4.addWidget(self.btn_fly)
            layout.addLayout(btn_row4)

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

    def on_bonk_clicked(self):
        ok = self.pet.trigger_bonk("控制面板注入：靠近屏幕边缘敲嘴壳！")
        if ok:
            self.last_event_label.setText("最新事件: 敲击屏幕边缘 (Beak Bonking)")
        else:
            self.last_event_label.setText("最新事件: 敲屏失败 (只在电脑屏幕边缘才触发)")

    def on_hop_clicked(self):
        self.pet.trigger_hop("控制面板注入：欢快移动连环小跳！")
        self.last_event_label.setText("最新事件: 移动雀跃小跳 (Hop Move)")

    def on_fly_clicked(self):
        self.pet.start_flight(panic=False, roam=True)
        self.last_event_label.setText("最新事件: 触发舒展飞翔 (Flight)")

    def on_force_sleep_clicked(self):
        self.pet.force_sleep("控制面板注入：疲劳度拉满至 100，直接进入睡眠")
        self.last_event_label.setText("最新事件: 强制睡眠 (疲劳拉满至 100)")

    def on_clear_fatigue_clicked(self):
        self.pet.clear_fatigue("控制面板注入：疲劳度已直接清空！")
        self.last_event_label.setText("最新事件: 清空疲劳 (疲劳归零)")

    def update_view(self):
        m = self.pet.mood
        curr_b = self.pet.current_behavior
        rem_t = max(0.0, self.pet.action_end_time - self.pet.get_now())
        self.state_label.setText(f"当前行为: <b>{curr_b.name_cn}</b> (剩余 {rem_t:.1f}s)")
        self.last_event_label.setText(f"最新事件: {self.pet.last_feedback}")
        self.fatigue_label.setText(f"疲劳 {m.fatigue:.1f} / 100")
        self.fatigue_bar.setValue(round(m.fatigue))

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
