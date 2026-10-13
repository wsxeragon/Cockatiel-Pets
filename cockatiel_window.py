import os
import time
import math
import random
from typing import Dict, Optional

from PySide6.QtCore import Qt, QTimer, QPoint, QPointF
from PySide6.QtGui import QPixmap, QPainter, QCursor, QAction, QTransform
from PySide6.QtWidgets import QWidget, QMenu, QApplication

from models import MoodDynamics, BehaviorType, BEHAVIOR_CATALOG, BehaviorDef, EXCITED_BEHAVIORS

class CockatielWindow(QWidget):
    """原始灰玄凤鹦鹉主桌宠窗口 (透明通道、无边框、置顶)"""
    def __init__(self):
        super().__init__()
        # 窗口属性: 无边框、置顶、桌面工具窗口 (不占用任务栏大窗口)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.SubWindow)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setMouseTracking(True)
        self.setFixedSize(100, 80)

        # 心态动力学与状态机
        self.mood = MoodDynamics()
        self.current_behavior: BehaviorDef = BEHAVIOR_CATALOG[BehaviorType.IDLE_BLINK]
        self.action_end_time: float = time.time() + 3.0
        self.last_feedback: str = "刚刚来到你的桌面~"

        # 动画帧控制
        self.current_frame_index: int = 0
        self.sprites: Dict[str, QPixmap] = {}
        self.load_all_sprites()

        # 鼠标拖拽状态
        self.is_dragging: bool = False
        self.drag_start_pos: QPoint = QPoint()
        self.hover_head_start_time: Optional[float] = None

        # 飞行平滑位移引擎
        self.is_flying: bool = False
        self.fly_start_pos: QPointF = QPointF()
        self.fly_target_pos: QPointF = QPointF()
        self.fly_control_pos: QPointF = QPointF()
        self.fly_progress: float = 0.0
        self.fly_duration: float = 2.0
        self.flight_purpose: str = "panic"
        self.fly_timer: QTimer = QTimer(self)
        self.fly_timer.timeout.connect(self.on_fly_step)

        # 移动 (Waddle 走来走去) 与朝向控制
        self.waddle_direction: int = -1 # 参考图面向左
        self.facing_direction: int = -1 # 1: 右, -1: 左
        self.waddle_step_count: int = 0
        self.hop_direction: int = -1    # 移动小跳方向

        # 雷达 HUD 监视器引用
        self.hud_window = None

        # 主定时器: 100ms 刷新一次心态与帧调度
        self.main_timer = QTimer(self)
        self.main_timer.timeout.connect(self.on_main_tick)
        self.main_timer.start(100)

        # 动画帧切换定时器
        self.anim_timer = QTimer(self)
        self.anim_timer.timeout.connect(self.on_anim_frame_step)
        self.anim_timer.start(self.current_behavior.frame_interval_ms)

        # 初始化位置 (屏幕右下角靠近任务栏)
        screen = QApplication.primaryScreen().geometry()
        self.move(screen.width() - self.width() - 30,
                  screen.height() - self.height() - 60)

    def get_now(self) -> float:
        return time.time()

    def set_hud(self, hud):
        self.hud_window = hud

    def load_all_sprites(self):
        assets_dir = os.path.join(os.path.dirname(__file__), "assets", "sprites")
        if not os.path.exists(assets_dir):
            return
        for file in os.listdir(assets_dir):
            if file.endswith(".png"):
                name = os.path.splitext(file)[0]
                pix = QPixmap(os.path.join(assets_dir, file))
                self.sprites[name] = pix

        # 动态自适应精灵画布尺寸
        if "idle_0" in self.sprites and not self.sprites["idle_0"].isNull():
            sw = self.sprites["idle_0"].width()
            sh = self.sprites["idle_0"].height()
            self.setFixedSize(sw, sh)

    def get_current_pixmap(self) -> QPixmap:
        frames = self.current_behavior.frames
        if not frames:
            pix = self.sprites.get("idle_0", QPixmap())
        else:
            frame_name = frames[self.current_frame_index % len(frames)]
            pix = self.sprites.get(frame_name, self.sprites.get("idle_0", QPixmap()))

        # 所有原始帧面向左，只有朝右时镜像。
        if self.facing_direction == 1 and not pix.isNull():
            return pix.transformed(QTransform().scale(-1, 1))
        return pix

    def switch_behavior(self, new_b_def: BehaviorDef, duration: float, feedback: str = None):
        # 从兴奋类行为切出时 (打断或结束)，自动清空兴奋值
        if self.current_behavior and self.current_behavior.code in EXCITED_BEHAVIORS and new_b_def.code not in EXCITED_BEHAVIORS:
            self.mood.clear_excitement()

        self.current_behavior = new_b_def
        self.current_frame_index = 0
        self.action_end_time = time.time() + duration
        if feedback:
            self.last_feedback = feedback

        # 移动雀跃小跳：根据屏幕边缘自适应随机选择起跳方向
        if new_b_def.code == BehaviorType.EXCITE_HOP:
            screen = QApplication.primaryScreen().geometry()
            cur_x = self.x()
            if cur_x < 90:
                self.hop_direction = 1
            elif cur_x > screen.width() - self.width() - 90:
                self.hop_direction = -1
            else:
                self.hop_direction = random.choice([-1, 1])
            self.facing_direction = self.hop_direction

        # 调整帧播放速率
        self.anim_timer.setInterval(new_b_def.frame_interval_ms)
        self.update()

    def wake_up(self, reason: str):
        """End sleep once, then prevent an immediate return to sleep."""
        if self.current_behavior.code != BehaviorType.REST_SLEEP:
            return
        self.mood.sleep_cooldown_until = time.time() + 90.0
        self.mood.last_interaction_time = time.time()
        self.switch_behavior(BEHAVIOR_CATALOG[BehaviorType.REST_WAKE], 0.6, reason)

    def force_sleep(self, reason: str = "强制睡眠：疲劳拉满，进入熟睡"):
        """直接将疲劳度拉满(100)，清空惊吓与兴奋，并立即进入睡眠状态"""
        self.is_flying = False
        self.is_dragging = False
        self.mood.fright = 0.0
        self.mood.excitement = 0.0
        self.mood.fatigue = 100.0
        self.mood.sleep_cooldown_until = 0.0
        self.switch_behavior(BEHAVIOR_CATALOG[BehaviorType.REST_SLEEP], 30.0, reason)
        if self.hud_window:
            self.hud_window.update_view()

    def clear_fatigue(self, reason: str = "疲劳度已直接清空！"):
        """直接清空疲劳度(归零)，如果正在睡觉则神清气爽醒来"""
        self.mood.fatigue = 0.0
        if self.current_behavior.code == BehaviorType.REST_SLEEP:
            self.wake_up(reason)
        else:
            self.last_feedback = reason
        if self.hud_window:
            self.hud_window.update_view()

    def trigger_bonk(self, reason: str = "兴奋自嗨：用嘴壳敲击屏幕！"):
        """靠拢最近的屏幕边缘并进入嘴壳敲击状态"""
        if self.current_behavior.code == BehaviorType.REST_SLEEP:
            self.wake_up("被敲屏冲动唤醒！")
        screen = QApplication.primaryScreen().geometry()
        cur_pos = self.pos()
        dist_to_left = cur_pos.x()
        dist_to_right = screen.width() - self.width() - cur_pos.x()
        if dist_to_left < dist_to_right:
            new_x = 25
            self.facing_direction = -1
            self.waddle_direction = 1
        else:
            new_x = screen.width() - self.width() - 25
            self.facing_direction = 1
            self.waddle_direction = -1
        self.move(new_x, cur_pos.y())
        self.mood.excitement = max(self.mood.excitement, 55.0)
        self.switch_behavior(BEHAVIOR_CATALOG[BehaviorType.EXCITE_BONK], 3.2, reason)
    def trigger_hop(self, reason: str = "兴奋雀跃：移动连环小跳！"):
        """触发移动雀跃小跳"""
        if self.current_behavior.code == BehaviorType.REST_SLEEP:
            self.wake_up("被欢快的跳跃冲动唤醒！")
        self.mood.excitement = max(self.mood.excitement, 65.0)
        self.switch_behavior(BEHAVIOR_CATALOG[BehaviorType.EXCITE_HOP], 3.2, reason)
        if self.hud_window:
            self.hud_window.update_view()

    def on_anim_frame_step(self):
        """动画帧步进"""
        frames = self.current_behavior.frames
        if len(frames) > 1:
            self.current_frame_index = (self.current_frame_index + 1) % len(frames)
            # 嘴壳敲击屏幕边缘时：在撞击帧给窗口轻微 1px 物理微震
            if self.current_behavior.code == BehaviorType.EXCITE_BONK:
                frame_name = frames[self.current_frame_index]
                if frame_name == "bonk_2":
                    shake_offset = -1 if self.facing_direction == -1 else 1
                    self.move(self.x() + shake_offset, self.y())
                elif frame_name == "bonk_3":
                    shake_back = 1 if self.facing_direction == -1 else -1
                    self.move(self.x() + shake_back, self.y())
            # 移动雀跃小跳：在各动作帧带动窗口产生连环跳跃位移
            elif self.current_behavior.code == BehaviorType.EXCITE_HOP:
                frame_name = frames[self.current_frame_index]
                hop_dx = 0
                if frame_name == "hop_1":
                    hop_dx = 8  # 腾空前跃冲刺
                elif frame_name == "hop_2":
                    hop_dx = 4  # 落地触地缓冲滑移
                elif frame_name == "hop_3":
                    hop_dx = 2  # 顺势回弹推进

                if hop_dx > 0:
                    screen = QApplication.primaryScreen().geometry()
                    cur_x = self.x()
                    new_x = cur_x + self.hop_direction * hop_dx
                    # 屏幕边缘反弹转向
                    if new_x < 25:
                        new_x = 25
                        self.hop_direction = 1
                        self.facing_direction = 1
                    elif new_x > screen.width() - self.width() - 25:
                        new_x = screen.width() - self.width() - 25
                        self.hop_direction = -1
                        self.facing_direction = -1
                    self.move(new_x, self.y())
            self.update()

    def on_main_tick(self):
        """主业务循环 (100ms)"""
        now = time.time()
        # 1. 心态动力学更新与衰减
        self.mood.update_tick(0.1, self.current_behavior.code)

        # 2. 如果正在被拖拽或飞行，暂停自主状态切换
        if self.is_dragging or self.is_flying:
            if self.hud_window:
                self.hud_window.update_view()
            return

        # 2.1 惊吓值 > 80% 触发应激防御: 鼠标靠近就会惊慌飞走
        if self.mood.fright > 80.0 and not self.is_flying:
            cursor_pos = QCursor.pos()
            pet_center = self.geometry().center()
            dist = math.hypot(cursor_pos.x() - pet_center.x(), cursor_pos.y() - pet_center.y())
            if dist < 120.0:
                if self.current_behavior.code == BehaviorType.REST_SLEEP:
                    self.wake_up("被逼近的鼠标惊醒！")
                self.start_flight(panic=True)
                self.last_feedback = "惊吓值超过80%，察觉到鼠标靠近，惊恐扇翅逃跑！"
                if self.hud_window:
                    self.hud_window.update_view()
                return

        # 2.2 疲劳度 > 90% 且惊吓值 < 50%: 强制终止其他行为，立刻进入睡眠
        if (self.mood.must_sleep()
                and self.current_behavior.code not in (BehaviorType.REST_SLEEP, BehaviorType.REST_WAKE)):
            self.switch_behavior(BEHAVIOR_CATALOG[BehaviorType.REST_SLEEP], 30.0,
                                 "疲劳度超过90%，困倦难耐，强制终止当前行为秒睡！")
            if self.hud_window:
                self.hud_window.update_view()
            return

        if self.current_behavior.code == BehaviorType.REST_SLEEP:
            if self.mood.fatigue <= 25.0 or self.mood.fright >= 50.0:
                self.wake_up("睡饱了，醒来伸展" if self.mood.fatigue <= 25.0 else "惊吓值>=50%，惊醒警惕！")
            elif now >= self.action_end_time:
                self.action_end_time = now + 30.0
            if self.hud_window:
                self.hud_window.update_view()
            return

        # 3. 漫步走来走去 (Waddle)
        if self.current_behavior.code == BehaviorType.IDLE_WADDLE:
            cur_pos = self.pos()
            screen = QApplication.primaryScreen().geometry()
            self.waddle_step_count += 1
            # 窗口缩小后同步缩短每步的屏幕位移。
            new_x = cur_pos.x() + self.waddle_direction * 2

            # 屏幕边缘折返与嘴壳敲击判定
            if new_x <= 25:
                new_x = 25
                self.move(new_x, cur_pos.y())
                self.facing_direction = -1
                self.waddle_step_count = 0
                # 触及屏幕左边缘：若处于兴奋或较活跃状态，高概率停下敲击屏幕边缘！
                if (self.mood.excitement >= 30.0 or random.random() < 0.5) and self.mood.fright < 40.0:
                    self.waddle_direction = 1  # 敲击结束后调头折返
                    self.switch_behavior(BEHAVIOR_CATALOG[BehaviorType.EXCITE_BONK], 3.2,
                                         "溜达撞到屏幕左边缘，兴奋用嘴壳敲击屏幕！")
                    if self.hud_window:
                        self.hud_window.update_view()
                    return
                else:
                    self.waddle_direction = 1
                    self.facing_direction = 1
            elif new_x >= screen.width() - self.width() - 25:
                new_x = screen.width() - self.width() - 25
                self.move(new_x, cur_pos.y())
                self.facing_direction = 1
                self.waddle_step_count = 0
                # 触及屏幕右边缘：同样判定嘴壳敲击
                if (self.mood.excitement >= 30.0 or random.random() < 0.5) and self.mood.fright < 40.0:
                    self.waddle_direction = -1  # 敲击结束后调头折返
                    self.switch_behavior(BEHAVIOR_CATALOG[BehaviorType.EXCITE_BONK], 3.2,
                                         "溜达撞到屏幕右边缘，兴奋用嘴壳敲击屏幕！")
                    if self.hud_window:
                        self.hud_window.update_view()
                    return
                else:
                    self.waddle_direction = -1
                    self.facing_direction = -1
            else:
                # 走了一段距离后 (约 20~35 步，即 2~3.5 秒)，有概率随机调头踱步
                if self.waddle_step_count > 20 and random.random() < 0.08:
                    self.waddle_direction *= -1
                    self.facing_direction = self.waddle_direction
                    self.waddle_step_count = 0

            self.move(new_x, cur_pos.y())

        # 4. 检查动作是否自然到期，抽取下一个动作
        if now >= self.action_end_time:
            # 兴奋类动作 (如唱歌、心形翅膀、打节拍、小跳、拆家等) 结束后，自动清空兴奋值
            if self.current_behavior.code in EXCITED_BEHAVIORS:
                self.mood.clear_excitement()
                self.last_feedback = f"{self.current_behavior.name_cn}结束，兴奋值自动清空！"

            if self.mood.should_sleep(now):
                self.switch_behavior(BEHAVIOR_CATALOG[BehaviorType.REST_SLEEP], 30.0,
                                     "困了，找个安静角落睡觉")
                return
            next_b_def, duration = self.mood.select_next_behavior(self.current_behavior.code)
            # 特殊情况: 如果抽取到飞行
            if next_b_def.code == BehaviorType.FRIGHT_PANIC_FLY:
                self.start_flight(panic=True)
            elif next_b_def.code == BehaviorType.COMFORT_APPROACH:
                self.start_flight(panic=False)
            elif next_b_def.code == BehaviorType.IDLE_FLY:
                self.start_flight(panic=False, roam=True)
            else:
                self.switch_behavior(next_b_def, duration, f"自发切换到: {next_b_def.name_cn}")

        # 6. 同步更新雷达监视器
        if self.hud_window:
            self.hud_window.update_view()

    # --- 空间交互与局部感应 ---
    def is_head_neck_zone(self, local_pos: QPoint) -> bool:
        """判定点击/悬停位置是否在头颈部安全区 (黄脸/冠羽/脖子)"""
        if local_pos.y() > self.height() * 0.55:
            return False
        # 根据当前左右朝向适配头颈 X 坐标
        if self.facing_direction == -1:
            return local_pos.x() < self.width() * 0.55
        else:
            return local_pos.x() > self.width() * 0.45

    def mouseMoveEvent(self, event):
        pos = event.position().toPoint()
        now = time.time()

        # 拖拽移动
        if self.is_dragging:
            self.move(event.globalPosition().toPoint() - self.drag_start_pos)
            return

        if self.current_behavior.code == BehaviorType.REST_SLEEP:
            if self.mood.fright > 80.0 and not self.is_flying:
                self.wake_up("鼠标靠近受惊！")
                self.start_flight(panic=True)
            return

        # 惊吓值 > 80% 触发应激防御: 鼠标靠近窗口，立即惊慌飞逃
        if self.mood.fright > 80.0 and not self.is_flying:
            self.start_flight(panic=True)
            self.last_feedback = "惊吓值超过80%，察觉到鼠标靠近，惊恐扇翅逃跑！"
            return

        # 悬停在头颈部检测
        if self.is_head_neck_zone(pos):
            if self.hover_head_start_time is None:
                self.hover_head_start_time = now
            else:
                hover_dur = now - self.hover_head_start_time
                # 悬停超过 0.6 秒且心态平和舒适 -> 主动低头求撸
                if hover_dur >= 0.6 and self.mood.fright < 25.0:
                    self.mood.hover_head_tick(0.05)
                    if self.current_behavior.code not in [BehaviorType.COMFORT_BOW, BehaviorType.COMFORT_FLUFF]:
                        self.switch_behavior(BEHAVIOR_CATALOG[BehaviorType.COMFORT_BOW], 3.0, "察觉到手停在头顶，主动低头求撸")
        else:
            self.hover_head_start_time = None

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            pos = event.position().toPoint()
            # Any click on the pet window is enough to wake a sleeping bird,
            # including a click on its transparent padding.
            if self.current_behavior.code == BehaviorType.REST_SLEEP:
                self.wake_up("被鼠标点击吵醒了")
                return
            # 检查点击点是否命中非透明羽毛
            pix = self.get_current_pixmap()
            if not pix.isNull() and 0 <= pos.x() < pix.width() and 0 <= pos.y() < pix.height():
                alpha = pix.toImage().pixelColor(pos.x(), pos.y()).alpha()
                if alpha < 30:
                    # 透明处既不触发交互，也不开始拖拽。
                    return

            self.is_dragging = True
            self.drag_start_pos = pos

            # 局部感应判定
            if self.is_head_neck_zone(pos):
                self.handle_pet_head()
            else:
                self.handle_touch_body()
        elif event.button() == Qt.RightButton:
            self.show_context_menu(event.globalPosition().toPoint())

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.is_dragging = False

    def handle_pet_head(self):
        """摸头交互"""
        if self.current_behavior.code == BehaviorType.REST_SLEEP:
            self.wake_up("被轻轻摸醒了")
        d_co, _, msg = self.mood.pet_head()
        # 优先切换到低头享受或蓬毛
        chosen = BehaviorType.COMFORT_BOW if random.random() < 0.6 else BehaviorType.COMFORT_FLUFF
        self.switch_behavior(BEHAVIOR_CATALOG[chosen], 3.5, msg)

    def handle_touch_body(self):
        """戳身体禁区"""
        if self.current_behavior.code == BehaviorType.REST_SLEEP:
            self.wake_up("被戳醒了！")
        panic, msg = self.mood.touch_body()
        if panic:
            # 强制应激惊飞逃跑
            self.start_flight(panic=True)
            self.last_feedback = msg
        else:
            # 咬人反击
            self.switch_behavior(BEHAVIOR_CATALOG[BehaviorType.FRIGHT_BITE], 1.0, msg)

    # --- 飞行引擎 (贝塞尔抛物线位移) ---
    def start_flight(self, panic: bool = True, roam: bool = False):
        if self.is_flying:
            return
        if self.current_behavior.code == BehaviorType.REST_SLEEP:
            self.wake_up("惊醒起飞")
        screen = QApplication.primaryScreen().geometry()
        cur_x = self.x()
        cur_y = self.y()

        self.fly_start_pos = QPointF(cur_x, cur_y)
        self.is_flying = True
        self.fly_progress = 0.0
        self.flight_purpose = "panic" if panic else ("roam" if roam else "approach")
        flight_cost = 5.0 if panic else (4.0 if roam else 3.0)
        self.mood.fatigue = min(100.0, self.mood.fatigue + flight_cost)

        if panic:
            # 惊吓飞往远端对角
            right_bound = max(25, screen.width() - self.width() - 25)
            target_x = random.randint(25, right_bound)
            target_y = random.randint(max(25, screen.height() - 230),
                                      max(25, screen.height() - 90))
            # 避开当前点
            if abs(target_x - cur_x) < 150:
                target_x = 25 if cur_x > screen.width() / 2 else right_bound
            self.fly_target_pos = QPointF(target_x, target_y)
            self.fly_duration = 1.2 # 逃跑飞得极快
            self.switch_behavior(BEHAVIOR_CATALOG[BehaviorType.FRIGHT_PANIC_FLY], 2.0, "受惊扑腾起飞逃跑！")
        elif roam:
            # Keep a clear horizontal displacement so a casual flight is visible.
            margin_x = max(30, screen.width() - self.width() - 30)
            margin_y = max(30, screen.height() - self.height() - 30)
            target_x = max(30, min(margin_x, cur_x + random.choice([-1, 1]) * random.randint(130, 260)))
            if abs(target_x - cur_x) < 75:
                target_x = max(30, min(margin_x, cur_x + (160 if cur_x < screen.width() / 2 else -160)))
            target_y = max(30, min(margin_y, cur_y + random.randint(-45, 45)))
            self.fly_target_pos = QPointF(target_x, target_y)
            self.fly_duration = max(1.4, min(2.8, abs(target_x - cur_x) / 130.0))
            self.switch_behavior(BEHAVIOR_CATALOG[BehaviorType.IDLE_FLY],
                                 self.fly_duration, "日常扑翅飞到附近")
        else:
            # 飞往光标附近 (撒娇)
            cursor_pos = QCursor.pos()
            target_x = max(25, min(screen.width() - self.width() - 25,
                                   cursor_pos.x() + random.choice([-40, 40])))
            target_y = max(25, min(screen.height() - self.height() - 25,
                                   cursor_pos.y() + 10))
            self.fly_target_pos = QPointF(target_x, target_y)
            self.fly_duration = 2.0
            self.switch_behavior(BEHAVIOR_CATALOG[BehaviorType.COMFORT_APPROACH], 2.5, "主动飞到主人光标边上~")

        # Reference frames face left. Mirror them when the flight heads right.
        dx = self.fly_target_pos.x() - cur_x
        if abs(dx) >= 1:
            self.facing_direction = 1 if dx > 0 else -1
            self.waddle_direction = self.facing_direction
            self.update()

        # 控制点（模拟高高掠起的弧度）
        mid_x = (self.fly_start_pos.x() + self.fly_target_pos.x()) / 2
        mid_y = min(self.fly_start_pos.y(), self.fly_target_pos.y()) - random.randint(60, 110)
        self.fly_control_pos = QPointF(mid_x, max(20.0, mid_y))

        self.fly_timer.start(25) # 40 FPS 平滑插值

    def on_fly_step(self):
        step = 0.025 / self.fly_duration
        self.fly_progress += step
        if self.fly_progress >= 1.0:
            self.fly_progress = 1.0
            self.move(int(self.fly_target_pos.x()), int(self.fly_target_pos.y()))
            self.fly_timer.stop()
            self.is_flying = False
            # 落地动作
            if self.flight_purpose == "panic" or self.mood.fright > 40.0:
                self.switch_behavior(BEHAVIOR_CATALOG[BehaviorType.FRIGHT_ALERT], 3.0, "惊险降落，警惕拉直身子")
            elif self.flight_purpose == "roam":
                self.switch_behavior(BEHAVIOR_CATALOG[BehaviorType.IDLE_BLINK], 2.0, "飞了一小段，落地休息")
            else:
                self.switch_behavior(BEHAVIOR_CATALOG[BehaviorType.COMFORT_BOW], 3.5, "亲切降落，在鼠标边低头求撸")
            return

        # 二阶贝塞尔曲线插值: B(t) = (1-t)^2 * P0 + 2t(1-t) * P1 + t^2 * P2
        t = self.fly_progress
        bx = (1 - t)**2 * self.fly_start_pos.x() + 2 * t * (1 - t) * self.fly_control_pos.x() + t**2 * self.fly_target_pos.x()
        by = (1 - t)**2 * self.fly_start_pos.y() + 2 * t * (1 - t) * self.fly_control_pos.y() + t**2 * self.fly_target_pos.y()
        self.move(int(bx), int(by))

    def show_context_menu(self, global_pos: QPoint):
        menu = QMenu(self)
        menu.setStyleSheet("""
            QMenu {
                background-color: #24273a;
                color: #cad3f5;
                border: 1px solid #494d64;
                padding: 4px;
            }
            QMenu::item:selected {
                background-color: #8aadf4;
                color: #181926;
            }
        """)
        act_hud = menu.addAction("📊 开启/关闭 心态雷达监视器")
        act_sing = menu.addAction("🎵 逗它开心吹口哨")
        act_hop = menu.addAction("🦘 移动雀跃小跳 (开心蹦跶)")
        act_bonk = menu.addAction("🥁 敲击屏幕边缘 (自嗨敲屏)")
        act_fly = menu.addAction("🕊️ 舒展振翅飞翔 (有机动力学)")
        act_fright = menu.addAction("⚡ 戳身反咬威慑 (嘴前辐射音波)")
        act_sleep = menu.addAction("💤 强制睡眠 (疲劳拉满)")
        act_clear_fatigue = menu.addAction("⚡ 清空疲劳 (瞬间回满)")
        act_reset = menu.addAction("🔄 重置心态为平静")
        menu.addSeparator()
        act_quit = menu.addAction("❌ 告别退出")

        res = menu.exec(global_pos)
        if res == act_hud:
            if self.hud_window:
                if self.hud_window.isVisible():
                    self.hud_window.hide()
                else:
                    self.hud_window.show()
        elif res == act_sing:
            if self.current_behavior.code == BehaviorType.REST_SLEEP:
                self.wake_up("被歌声唤醒了")
            self.mood.excitement = 90.0
            self.switch_behavior(BEHAVIOR_CATALOG[BehaviorType.EXCITE_SING], 6.0, "被主人逗乐，开心大声独唱！")
        elif res == act_hop:
            self.trigger_hop("右键菜单触发：欢快移动连环小跳！")
        elif res == act_bonk:
            self.trigger_bonk("右键菜单触发：靠边敲击屏幕！")
        elif res == act_fly:
            self.start_flight(panic=False, roam=True)
        elif res == act_fright:
            self.handle_touch_body()
        elif res == act_sleep:
            self.force_sleep("右键菜单触发：疲劳度拉满，进入熟睡")
        elif res == act_clear_fatigue:
            self.clear_fatigue("右键菜单触发：疲劳度已直接清空！")
        elif res == act_reset:
            self.mood.fright = 0.0
            self.mood.comfort = 25.0
            self.mood.excitement = 10.0
            self.mood.fatigue = 0.0
            self.mood.sleep_cooldown_until = 0.0
            self.mood.last_head_pet_time = float("-inf")
            self.switch_behavior(BEHAVIOR_CATALOG[BehaviorType.IDLE_BLINK], 3.0, "心态平复回原点")
        elif res == act_quit:
            QApplication.quit()

    def paintEvent(self, event):
        painter = QPainter(self)
        pix = self.get_current_pixmap()
        if not pix.isNull():
            painter.drawPixmap(0, 0, pix)
