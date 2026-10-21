import os
import sys
import time
import math
import random
import json
from typing import Dict, Optional

from PySide6.QtCore import Qt, QTimer, QPoint, QPointF, QRect
from PySide6.QtGui import QPixmap, QPainter, QCursor, QAction, QTransform, QIcon
from PySide6.QtWidgets import QWidget, QMenu, QApplication, QToolTip

from models import MoodDynamics, BehaviorType, BEHAVIOR_CATALOG, BehaviorDef, EXCITED_BEHAVIORS
from config import get_base_dir, is_dev_mode
from autostart import is_auto_start_supported, is_auto_start_enabled, set_auto_start

class CockatielWindow(QWidget):
    """原始灰玄凤鹦鹉主桌宠窗口 (透明通道、无边框、置顶)"""
    def __init__(self):
        super().__init__()
        # 窗口属性: 无边框、置顶、桌面工具窗口 (不占用任务栏大窗口)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.SubWindow)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setMouseTracking(True)
        self.setFixedSize(100, 80)

        # 窗口与托盘图标
        icon_path = os.path.join(get_base_dir(), "assets", "cockatiel.ico")
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))

        # 心态动力学与状态机
        self.mood = MoodDynamics()
        self.current_behavior: BehaviorDef = BEHAVIOR_CATALOG[BehaviorType.IDLE_BLINK]
        self.action_end_time: float = time.time() + 3.0
        self.last_feedback: str = "刚刚来到你的桌面~"

        # 羽冠造型与动画帧控制
        self.crest_style: str = self.load_saved_crest_style()
        self.current_frame_index: int = 0
        self.sprites: Dict[str, QPixmap] = {}
        self.load_all_sprites(self.crest_style)

        # 待机微动画 (呼吸 / 眨眼 / 冠羽) 的状态。只在 IDLE_BLINK 时启用。
        # 时间基准用 monotonic 毫秒，避免系统时钟跳变。
        self._idle_t0: float = time.monotonic()
        self._idle_relaxed: bool = False      # False=idle_0(冠羽竖起) True=idle_2(冠羽放松)
        self._breath_until: float = -1.0      # 身体下沉结束时刻
        self._blink_until: float = -1.0       # 闭眼结束时刻
        self._twitch_until: float = -1.0      # 冠羽轻抖结束时刻
        self._next_breath: float = 0.0
        self._next_blink: float = 0.0
        self._next_twitch: float = 0.0
        self._next_crest: float = 0.0

        # 鼠标拖拽状态与预定待执行行为 (例如摸头后固定衔接理毛)
        self.is_dragging: bool = False
        self.drag_start_pos: QPoint = QPoint()
        self.hover_head_start_time: Optional[float] = None
        self.pending_next_behavior: Optional[BehaviorType] = None
        self.yawn_remaining_repeats: int = 0

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
        self.waddle_mode: str = "origin_pacing" # "origin_pacing" (起点左右来回) 或 "straight_to_edge" (径直走向屏幕边缘)
        self.waddle_origin_x: int = 0           # 模式一起点 X 坐标
        self.waddle_consecutive_steps: int = 0  # 同一方向连续行走的步数 (走的越远回头概率越高)
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

        # 待机微动画定时器 (60ms)：驱动呼吸 / 眨眼 / 冠羽的随机事件
        self.idle_timer = QTimer(self)
        self.idle_timer.timeout.connect(self.on_idle_tick)
        self.idle_timer.start(60)

        # 初始化位置 (屏幕右下角靠近任务栏，完全限制在可用可视区域内)
        rect = self.get_screen_rect(use_available=True)
        init_x = rect.right() - self.width() - 30
        init_y = rect.bottom() - self.height() - 20
        self.safe_move(init_x, init_y, margin=10)

    def get_screen_rect(self, use_available: bool = True) -> QRect:
        """获取桌宠当前所在屏幕的可视安全矩形 (适配多显示器与Windows任务栏)"""
        pet_center = self.geometry().center()
        screen = QApplication.screenAt(pet_center)
        if not screen:
            screen = QApplication.screenAt(self.pos())
        if not screen:
            screen = QApplication.primaryScreen()
        if not screen:
            return QRect(0, 0, 1920, 1080)
        return screen.availableGeometry() if use_available else screen.geometry()

    def clamp_pos_to_screen(self, x: int, y: int, margin: int = 10) -> QPoint:
        """严格限制坐标在当前屏幕的可视区域内，杜绝出屏"""
        rect = self.get_screen_rect(use_available=True)
        w = self.width()
        h = self.height()

        min_x = rect.left() + margin
        max_x = rect.right() - w - margin + 1
        min_y = rect.top() + margin
        max_y = rect.bottom() - h - margin + 1

        if max_x < min_x:
            max_x = min_x
        if max_y < min_y:
            max_y = min_y

        clamped_x = max(min_x, min(max_x, x))
        clamped_y = max(min_y, min(max_y, y))
        return QPoint(clamped_x, clamped_y)

    def safe_move(self, x: int, y: int, margin: int = 10):
        """安全移动：限制在屏幕可见区域内"""
        clamped = self.clamp_pos_to_screen(x, y, margin=margin)
        self.move(clamped)

    def ensure_on_screen(self, margin: int = 10):
        """保底卫士：如果当前桌宠超出屏幕可视区域，立即平滑拉回屏幕内"""
        rect = self.get_screen_rect(use_available=True)
        cur_geom = self.geometry()
        safe_rect = QRect(rect.left() + margin, rect.top() + margin,
                          max(1, rect.width() - 2 * margin), max(1, rect.height() - 2 * margin))
        if not safe_rect.contains(cur_geom):
            self.safe_move(self.x(), self.y(), margin=margin)

    def get_now(self) -> float:
        return time.time()

    def set_hud(self, hud):
        self.hud_window = hud


    def get_config_path(self) -> str:
        return os.path.join(get_base_dir(), "assets", "crest_config.json")

    def load_saved_crest_style(self) -> str:
        cfg_path = self.get_config_path()
        if os.path.exists(cfg_path):
            try:
                with open(cfg_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    return data.get("crest_style", "classic")
            except Exception:
                pass
        return "classic"

    def save_crest_style(self, style: str):
        cfg_path = self.get_config_path()
        try:
            with open(cfg_path, "w", encoding="utf-8") as f:
                json.dump({"crest_style": style}, f, ensure_ascii=False, indent=2)
        except Exception:
            pass

    def load_all_sprites(self, crest_style: Optional[str] = None):
        if crest_style:
            self.crest_style = crest_style

        # 根据当前羽冠造型选择素材目录
        base_dir = get_base_dir()
        if self.crest_style == "classic":
            target_dir = os.path.join(base_dir, "assets", "sprites_classic")
        else:
            target_dir = os.path.join(base_dir, "assets", "sprites_triple")

        if not os.path.exists(target_dir):
            target_dir = os.path.join(base_dir, "assets", "sprites")

        if not os.path.exists(target_dir):
            return

        self.sprites.clear()
        for file in os.listdir(target_dir):
            if file.endswith(".png"):
                name = os.path.splitext(file)[0]
                pix = QPixmap(os.path.join(target_dir, file))
                self.sprites[name] = pix

        # 动态自适应精灵画布尺寸
        if "idle_0" in self.sprites and not self.sprites["idle_0"].isNull():
            sw = self.sprites["idle_0"].width()
            sh = self.sprites["idle_0"].height()
            self.setFixedSize(sw, sh)

        self.save_crest_style(self.crest_style)

    def switch_crest_style(self, new_style: str):
        if self.crest_style == new_style:
            return
        self.load_all_sprites(new_style)
        label = "🐰 经典兔耳羽冠" if new_style == "classic" else "✨ 灵动三毛羽冠"
        self.last_feedback = f"已换上【{label}】装扮！"
        self.update()
        if self.hud_window:
            self.hud_window.update()

    def _idle_elapsed_ms(self) -> float:
        return (time.monotonic() - self._idle_t0) * 1000.0

    def _idle_frame_name(self) -> str:
        """待机造型 = 基础姿势 + 呼吸下沉；眨眼优先级最高。"""
        t = self._idle_elapsed_ms()
        pose = "idle_2" if self._idle_relaxed else "idle_0"
        if t < self._twitch_until:
            pose = "idle_2"          # 冠羽轻抖
        if t < self._blink_until:
            pose = "idle_1"          # 眨眼
        down = t < self._breath_until
        return pose + ("_dn" if down else "")

    def _idle_pixmap(self) -> QPixmap:
        name = self._idle_frame_name()
        pix = self.sprites.get(name)
        if pix is not None and not pix.isNull():
            return pix
        if name.endswith("_dn"):                 # 缺下沉帧时退回普通帧
            pix = self.sprites.get(name[:-3])
            if pix is not None and not pix.isNull():
                return pix
        return self.sprites.get("idle_0", QPixmap())

    def on_idle_tick(self):
        """待机微动画：呼吸 / 眨眼 / 冠羽，事件驱动、间隔随机。"""
        if self.current_behavior.code != BehaviorType.IDLE_BLINK:
            return
        t = self._idle_elapsed_ms()
        if t >= self._next_crest:
            self._idle_relaxed = not self._idle_relaxed
            self._next_crest = t + random.uniform(8000, 18000)
        if t >= self._next_blink:
            self._blink_until = t + 120
            self._next_blink = t + random.uniform(2000, 5000)
        if t >= self._next_twitch:
            self._twitch_until = t + 100
            self._next_twitch = t + random.uniform(6000, 12000)
        if t >= self._next_breath:
            self._breath_until = t + 600
            self._next_breath = t + random.uniform(4000, 9000)
        self.update()

    def get_current_pixmap(self) -> QPixmap:
        # 待机状态走微动画（呼吸下沉 / 随机眨眼 / 冠羽切换）
        if self.current_behavior.code == BehaviorType.IDLE_BLINK:
            pix = self._idle_pixmap()
            if not pix.isNull():
                if self.facing_direction == 1:
                    return pix.transformed(QTransform().scale(-1, 1))
                return pix

        frames = self.current_behavior.frames
        if not frames:
            pix = self.sprites.get("idle_0", QPixmap())
        else:
            frame_name = frames[self.current_frame_index % len(frames)]
            pix = self.sprites.get(frame_name, self.sprites.get("idle_0", QPixmap()))

        # 玩球动作自带完整左右舞台编排与朝向，不作全局镜像翻转
        if self.current_behavior.code == BehaviorType.EXCITE_PLAY_BALL:
            return pix

        # 所有原始帧面向左，只有朝右时镜像。
        if self.facing_direction == 1 and not pix.isNull():
            return pix.transformed(QTransform().scale(-1, 1))
        return pix

    def switch_behavior(self, new_b_def: BehaviorDef, duration: Optional[float] = None, feedback: str = None):
        if duration is None:
            duration = max(1.0, random.gauss(new_b_def.duration_mean, new_b_def.duration_std))

        # 从玩球切出时 (无论是正常结束还是被打断)，恢复标准 100x80 画布并平滑对齐地面与鸟体坐标
        # 鸟在最后一帧展翅飞下地面并站立于 bcx=84, ground y=98
        # 标准 100x80 中，鸟中心 x=53, ground y=72
        if self.current_behavior and self.current_behavior.code == BehaviorType.EXCITE_PLAY_BALL and new_b_def.code != BehaviorType.EXCITE_PLAY_BALL:
            self.setFixedSize(100, 80)
            restore_x = self.x() + 84 - 53
            restore_y = self.y() + 98 - 72
            self.safe_move(restore_x, restore_y, margin=10)

        # 进入玩球时，临时扩容为 260x120 高清像素舞台，并无缝贴合原站立点
        if new_b_def.code == BehaviorType.EXCITE_PLAY_BALL:
            rect = self.get_screen_rect(use_available=True)
            target_x = self.x() + 53 - 175
            target_y = self.y() + 72 - 98
            target_x = max(rect.left() + 10, min(rect.right() - 260 - 10, target_x))
            target_y = max(rect.top() + 10, min(rect.bottom() - 120 - 10, target_y))
            self.setFixedSize(260, 120)
            self.safe_move(target_x, target_y, margin=10)
            self.facing_direction = -1
            duration = 60.0  # 提供充分的冗余时间，由最后一帧自然驱动谢幕切出，绝不被时钟截断

        # 从兴奋类行为切出时 (打断或结束)，自动清空兴奋值
        if self.current_behavior and self.current_behavior.code in EXCITED_BEHAVIORS and new_b_def.code not in EXCITED_BEHAVIORS:
            self.mood.clear_excitement()

        self.current_behavior = new_b_def
        self.current_frame_index = 0
        self.action_end_time = time.time() + duration

        # 进入待机时重置微动画的随机时间表（每次待机的节奏都不同）
        if new_b_def.code == BehaviorType.IDLE_BLINK:
            self._idle_t0 = time.monotonic()
            self._idle_relaxed = False
            self._breath_until = self._blink_until = self._twitch_until = -1.0
            self._next_blink = random.uniform(2000, 5000)
            self._next_twitch = random.uniform(6000, 12000)
            self._next_breath = random.uniform(1500, 3000)
            self._next_crest = random.uniform(8000, 18000)
        if feedback:
            self.last_feedback = feedback

        # 待执行动作消费与重置
        if getattr(self, 'pending_next_behavior', None) == new_b_def.code:
            self.pending_next_behavior = None
        elif new_b_def.code != BehaviorType.COMFORT_BOW:
            self.pending_next_behavior = None

        # 打哈欠连击计数清理 (切入非打哈欠动作时归零)
        if new_b_def.code != BehaviorType.COMFORT_YAWN:
            self.yawn_remaining_repeats = 0

        # 移动雀跃小跳：根据屏幕边缘自适应随机选择起跳方向
        if new_b_def.code == BehaviorType.EXCITE_HOP:
            rect = self.get_screen_rect(use_available=True)
            cur_x = self.x()
            if cur_x < rect.left() + 90:
                self.hop_direction = 1
            elif cur_x > rect.right() - self.width() - 90:
                self.hop_direction = -1
            else:
                self.hop_direction = random.choice([-1, 1])
            self.facing_direction = self.hop_direction

        # 摇晃溜达：初始化模式(起点来回踱步 vs 径直走碰屏幕)与初始方向
        if new_b_def.code == BehaviorType.IDLE_WADDLE:
            self.waddle_origin_x = self.x()
            self.waddle_consecutive_steps = 0
            self.waddle_step_count = 0
            self.waddle_mode = random.choice(["origin_pacing", "straight_to_edge"])
            rect = self.get_screen_rect(use_available=True)
            cur_x = self.x()
            min_x = rect.left() + 35
            max_x = rect.right() - self.width() - 35
            if cur_x <= min_x:
                self.waddle_direction = 1
            elif cur_x >= max_x:
                self.waddle_direction = -1
            else:
                self.waddle_direction = random.choice([-1, 1])
            self.facing_direction = self.waddle_direction

        # 调整帧播放速率
        intervals = getattr(new_b_def, 'frame_intervals_ms', None)
        if intervals and len(intervals) > 0:
            self.anim_timer.setInterval(intervals[0])
        else:
            self.anim_timer.setInterval(new_b_def.frame_interval_ms)
        self.update()

    def wake_up(self, reason: str):
        """End sleep once, then prevent an immediate return to sleep."""
        if self.current_behavior.code not in (BehaviorType.REST_SLEEP, BehaviorType.REST_FALL_ASLEEP):
            return
        now = time.time()
        self.mood.sleep_cooldown_until = now + 90.0
        self.mood.last_interaction_time = now
        # 用户手动唤醒或交互吵醒时：适度调降疲劳度 (降至 75.0)，避免依然卡在 >=90% 临界高位导致刚醒来就秒睡
        if self.mood.fatigue >= 80.0:
            self.mood.fatigue = 75.0
        # 50% 概率触发方案一 (利落机敏版)，50% 概率触发方案二 (细致观察版)
        chosen_wake = random.choice([BehaviorType.REST_WAKE, BehaviorType.REST_WAKE_CURIOUS])
        duration = 2.3 if chosen_wake == BehaviorType.REST_WAKE else 2.5
        self.switch_behavior(BEHAVIOR_CATALOG[chosen_wake], duration, reason)
        if self.hud_window:
            self.hud_window.update_view()

    def force_sleep(self, reason: str = "强制睡眠：疲劳拉满，打瞌睡卧下入睡"):
        """直接将疲劳度拉满(100)，清空惊吓与兴奋，并播放卧倒动画进入睡眠状态"""
        self.is_flying = False
        self.is_dragging = False
        self.mood.fright = 0.0
        self.mood.excitement = 0.0
        self.mood.fatigue = 100.0
        self.mood.sleep_cooldown_until = 0.0
        self.switch_behavior(BEHAVIOR_CATALOG[BehaviorType.REST_FALL_ASLEEP], 1.35, reason)
        if self.hud_window:
            self.hud_window.update_view()

    def clear_fatigue(self, reason: str = "疲劳度已直接清空！"):
        """直接清空疲劳度(归零)，如果正在睡觉则神清气爽醒来"""
        self.mood.fatigue = 0.0
        if self.current_behavior.code in (BehaviorType.REST_SLEEP, BehaviorType.REST_FALL_ASLEEP):
            self.wake_up(reason)
        else:
            self.last_feedback = reason
        if self.hud_window:
            self.hud_window.update_view()

    def is_at_screen_edge(self, margin: int = 50) -> bool:
        """判定当前桌宠是否处于屏幕左右边缘（margin 为边缘距离阈值，适配多显示器）"""
        rect = self.get_screen_rect(use_available=True)
        cur_x = self.x()
        at_left = cur_x <= (rect.left() + margin)
        at_right = cur_x >= (rect.right() - self.width() - margin)
        return at_left or at_right

    def trigger_bonk(self, reason: str = "兴奋自嗨：用嘴壳敲击屏幕！") -> bool:
        """在屏幕边缘进入嘴壳敲击状态（只在电脑屏幕边缘才触发）"""
        if not self.is_at_screen_edge(margin=60):
            msg = "敲屏只在电脑屏幕边缘才触发！请把小玄凤拖到屏幕边缘，或等它自己溜达过去~"
            self.last_feedback = msg
            if self.hud_window:
                self.hud_window.update_view()
            return False

        if self.current_behavior.code == BehaviorType.REST_SLEEP:
            self.wake_up("被敲屏冲动唤醒！")
        rect = self.get_screen_rect(use_available=True)
        cur_pos = self.pos()
        dist_to_left = cur_pos.x() - rect.left()
        dist_to_right = rect.right() - self.width() - cur_pos.x()
        if dist_to_left < dist_to_right:
            new_x = rect.left() + 25
            self.facing_direction = -1
            self.waddle_direction = 1
        else:
            new_x = rect.right() - self.width() - 25
            self.facing_direction = 1
            self.waddle_direction = -1
        self.safe_move(new_x, cur_pos.y(), margin=10)
        self.mood.excitement = max(self.mood.excitement, 55.0)
        self.switch_behavior(BEHAVIOR_CATALOG[BehaviorType.EXCITE_BONK], None, reason)
        return True
    def trigger_hop(self, reason: str = "兴奋雀跃：移动连环小跳！"):
        """触发移动雀跃小跳"""
        if self.current_behavior.code == BehaviorType.REST_SLEEP:
            self.wake_up("被欢快的跳跃冲动唤醒！")
        self.mood.excitement = max(self.mood.excitement, 65.0)
        self.switch_behavior(BEHAVIOR_CATALOG[BehaviorType.EXCITE_HOP], None, reason)
        if self.hud_window:
            self.hud_window.update_view()

    def trigger_yawn(self, reason: str = "伸脖打大哈欠！", repeats: Optional[int] = None):
        """触发伸脖打哈欠，支持指定或随机 3~5 次连续打哈欠"""
        if self.current_behavior.code == BehaviorType.REST_SLEEP:
            self.wake_up("醒来伸长脖子打大哈欠")
        self.yawn_remaining_repeats = repeats if repeats is not None else random.randint(3, 5)
        self.switch_behavior(BEHAVIOR_CATALOG[BehaviorType.COMFORT_YAWN], 2.35 * self.yawn_remaining_repeats, reason)
        if self.hud_window:
            self.hud_window.update_view()

    def on_anim_frame_step(self):
        """动画帧步进"""
        frames = self.current_behavior.frames
        intervals = getattr(self.current_behavior, 'frame_intervals_ms', None)
        if len(frames) > 1:
            if not getattr(self.current_behavior, 'is_looping', True):
                if self.current_frame_index < len(frames) - 1:
                    self.current_frame_index += 1
                    if intervals and self.current_frame_index < len(intervals):
                        self.anim_timer.setInterval(intervals[self.current_frame_index])
                else:
                    # 非循环长动作播放完毕最后一帧 (如杂技踩球 300 帧完整演完大谢幕，或打哈欠 8 帧自然收尾)
                    if self.current_behavior.code == BehaviorType.EXCITE_PLAY_BALL:
                        self.switch_behavior(BEHAVIOR_CATALOG[BehaviorType.IDLE_BLINK], 3.0, "精彩杂技玩球谢幕完毕，平稳落地发呆~")
                        if self.hud_window:
                            self.hud_window.update_view()
                        return
                    elif self.current_behavior.code == BehaviorType.COMFORT_YAWN:
                        if getattr(self, 'yawn_remaining_repeats', 0) > 1:
                            self.yawn_remaining_repeats -= 1
                            self.current_frame_index = 0
                            if intervals and len(intervals) > 0:
                                self.anim_timer.setInterval(intervals[0])
                            self.action_end_time = time.time() + 2.5 * self.yawn_remaining_repeats
                            self.last_feedback = f"惬意连续打哈欠 (剩余{self.yawn_remaining_repeats}次)..."
                            self.update()
                            return
                        else:
                            self.yawn_remaining_repeats = 0
                            self.switch_behavior(BEHAVIOR_CATALOG[BehaviorType.IDLE_BLINK], 3.0, "连续打完哈欠，神清气爽发呆~")
                            if self.hud_window:
                                self.hud_window.update_view()
                            return
                    elif self.current_behavior.code == BehaviorType.REST_FALL_ASLEEP:
                        self.switch_behavior(BEHAVIOR_CATALOG[BehaviorType.REST_SLEEP], 30.0, "安然进入熟睡梦乡~")
                        if self.hud_window:
                            self.hud_window.update_view()
                        return
                    elif self.current_behavior.code in (BehaviorType.REST_WAKE, BehaviorType.REST_WAKE_CURIOUS):
                        self.switch_behavior(BEHAVIOR_CATALOG[BehaviorType.IDLE_BLINK], 3.0, "睡醒伸展完毕，站立发呆~")
                        if self.hud_window:
                            self.hud_window.update_view()
                        return
            else:
                self.current_frame_index = (self.current_frame_index + 1) % len(frames)
                if intervals and self.current_frame_index < len(intervals):
                    self.anim_timer.setInterval(intervals[self.current_frame_index])
            # 嘴壳敲击屏幕边缘时：在撞击帧给窗口轻微 1px 物理微震
            if self.current_behavior.code == BehaviorType.EXCITE_BONK:
                frame_name = frames[self.current_frame_index]
                if frame_name == "bonk_2":
                    shake_offset = -1 if self.facing_direction == -1 else 1
                    self.safe_move(self.x() + shake_offset, self.y(), margin=10)
                elif frame_name == "bonk_3":
                    shake_back = 1 if self.facing_direction == -1 else -1
                    self.safe_move(self.x() + shake_back, self.y(), margin=10)
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
                    rect = self.get_screen_rect(use_available=True)
                    cur_x = self.x()
                    new_x = cur_x + self.hop_direction * hop_dx
                    min_hop_x = rect.left() + 25
                    max_hop_x = rect.right() - self.width() - 25
                    # 屏幕边缘反弹转向
                    if new_x <= min_hop_x:
                        new_x = min_hop_x
                        self.hop_direction = 1
                        self.facing_direction = 1
                    elif new_x >= max_hop_x:
                        new_x = max_hop_x
                        self.hop_direction = -1
                        self.facing_direction = -1
                    self.safe_move(new_x, self.y(), margin=10)
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

        # 巡检保底：在自主活动时，确保始终位于可用屏幕内 (防多屏热插拔、分辨率变化等)
        self.ensure_on_screen(margin=10)

        # 2.1 惊吓值 > 80% 触发应激防御: 鼠标靠近就会惊慌飞走
        if self.mood.fright > 80.0 and not self.is_flying:
            cursor_pos = QCursor.pos()
            pet_center = self.geometry().center()
            dist = math.hypot(cursor_pos.x() - pet_center.x(), cursor_pos.y() - pet_center.y())
            if dist < 120.0:
                if self.current_behavior.code in (BehaviorType.REST_SLEEP, BehaviorType.REST_FALL_ASLEEP):
                    self.wake_up("被逼近的鼠标惊醒！")
                self.start_flight(panic=True)
                self.last_feedback = "惊吓值超过80%，察觉到鼠标靠近，惊恐扇翅逃跑！"
                if self.hud_window:
                    self.hud_window.update_view()
                return

        # 2.2 疲劳度 > 90% 且惊吓值 < 50%: 强制终止其他行为，立刻进入入睡过渡 (受唤醒冷却保护)
        if (self.mood.must_sleep(now)
                and self.current_behavior.code not in (BehaviorType.REST_SLEEP, BehaviorType.REST_FALL_ASLEEP, BehaviorType.REST_WAKE, BehaviorType.REST_WAKE_CURIOUS)):
            self.switch_behavior(BEHAVIOR_CATALOG[BehaviorType.REST_FALL_ASLEEP], 1.35,
                                 "疲劳度超过90%，困倦难耐，打瞌睡卧下入睡！")
            if self.hud_window:
                self.hud_window.update_view()
            return

        if self.current_behavior.code == BehaviorType.REST_FALL_ASLEEP:
            if self.mood.fright >= 50.0:
                self.wake_up("惊吓值>=50%，惊醒警惕！")
            elif now >= self.action_end_time:
                self.switch_behavior(BEHAVIOR_CATALOG[BehaviorType.REST_SLEEP], 30.0, "安然进入熟睡梦乡~")
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
            rect = self.get_screen_rect(use_available=True)
            self.waddle_step_count += 1
            self.waddle_consecutive_steps += 1
            new_x = cur_pos.x() + self.waddle_direction * 2
            min_waddle_x = rect.left() + 25
            max_waddle_x = rect.right() - self.width() - 25

            # 判定是否触及屏幕边缘 (两种模式到达屏幕边缘时走统一边界逻辑)
            if new_x <= min_waddle_x or new_x >= max_waddle_x:
                hit_left = (new_x <= min_waddle_x)
                clamped_x = min_waddle_x if hit_left else max_waddle_x
                self.safe_move(clamped_x, cur_pos.y(), margin=10)
                self.facing_direction = -1 if hit_left else 1
                self.waddle_step_count = 0
                self.waddle_consecutive_steps = 0

                # 触及屏幕边缘判定：兴奋值越高，触发敲边缘的概率越大
                # 惊吓戒备状态下 (fright >= 40) 不会自嗨敲屏
                if self.mood.fright < 40.0:
                    # 兴奋度在 [0, 100]：兴奋度越高，敲屏概率平滑增长 (15% ~ 95%)
                    bonk_prob = min(0.95, max(0.10, 0.15 + (self.mood.excitement / 100.0) * 0.80))
                    if random.random() < bonk_prob:
                        self.waddle_direction = 1 if hit_left else -1  # 敲击结束后调头折返
                        self.switch_behavior(BEHAVIOR_CATALOG[BehaviorType.EXCITE_BONK], None,
                                             f"溜达触及屏幕边缘，兴奋度({int(self.mood.excitement)}%)触发敲屏！")
                        if self.hud_window:
                            self.hud_window.update_view()
                        return

                # 若未触发敲屏幕，转身往回走
                self.waddle_direction = 1 if hit_left else -1
                self.facing_direction = self.waddle_direction
                self.waddle_origin_x = clamped_x
                # 碰到边缘掉头后，随机选择下一段的漫步模式
                self.waddle_mode = random.choice(["origin_pacing", "straight_to_edge"])
                self.last_feedback = "触及屏幕边缘，转身往回走~"
            else:
                # 在屏幕可用范围内行走
                if self.waddle_mode == "origin_pacing":
                    # 模式一：以起点为基准，左右来回走。同一个方向走的越远，回头的概率越大
                    # 加大来回溜达的移动距离：
                    # 前 35 步 (约 3.5 秒 / 70px) 保持前行以展开较大尺度的漫步；
                    # 超过 35 步后，回头概率随连续步数平滑指数增长 (50步/100px~1%，80步/160px~7%，110步/220px~20%，140步/280px~45%)
                    if self.waddle_consecutive_steps > 35:
                        excess = self.waddle_consecutive_steps - 35
                        turn_prob = min(0.60, 0.005 + ((excess / 70.0) ** 2.2) * 0.18)
                        if random.random() < turn_prob:
                            self.waddle_direction *= -1
                            self.facing_direction = self.waddle_direction
                            self.waddle_consecutive_steps = 0
                            self.last_feedback = "漫步了一段距离，悠然转身往反方向溜达~"
                # 模式二 (straight_to_edge): 径直走直到碰到屏幕，中途不随意掉头

                self.safe_move(new_x, cur_pos.y(), margin=10)

        # 4. 检查动作是否自然到期，抽取下一个动作
        # 杂技踩球包含 300 帧完整舞台剧情 (含大谢幕与落地)，由 on_anim_frame_step 自然播放完毕后收尾切出，跳过主循环强制超时
        if self.current_behavior.code == BehaviorType.EXCITE_PLAY_BALL:
            if self.hud_window:
                self.hud_window.update_view()
            return

        if now >= self.action_end_time:
            # 兴奋类动作 (如唱歌、心形翅膀、打节拍、小跳、拆家等) 结束后，自动清空兴奋值
            if self.current_behavior.code in EXCITED_BEHAVIORS:
                self.mood.clear_excitement()
                self.last_feedback = f"{self.current_behavior.name_cn}结束，兴奋值自动清空！"

            # 刚睡醒伸展完毕：平稳切入平静发呆站立
            if self.current_behavior.code in (BehaviorType.REST_WAKE, BehaviorType.REST_WAKE_CURIOUS):
                self.switch_behavior(BEHAVIOR_CATALOG[BehaviorType.IDLE_BLINK], 3.0, "伸展完毕，清醒站立发呆~")
                if self.hud_window:
                    self.hud_window.update_view()
                return

            # 入睡过渡播放完毕：正式进入沉睡
            if self.current_behavior.code == BehaviorType.REST_FALL_ASLEEP:
                self.switch_behavior(BEHAVIOR_CATALOG[BehaviorType.REST_SLEEP], 30.0, "安然进入熟睡梦乡~")
                if self.hud_window:
                    self.hud_window.update_view()
                return

            # 仅当存在预设动作 (即鼠标点击了摸头后) 才固定衔接理毛
            if self.pending_next_behavior:
                next_code = self.pending_next_behavior
                self.pending_next_behavior = None
                self.switch_behavior(BEHAVIOR_CATALOG[next_code], None, "摸头享受完毕，开始整理凌乱羽毛~")
                if self.hud_window:
                    self.hud_window.update_view()
                return

            # 理毛 (COMFORT_PREEN) 结束后：30% 概率触发伸脖打哈欠，连打 3~5 次
            if self.current_behavior.code == BehaviorType.COMFORT_PREEN:
                if random.random() < 0.30:
                    repeats = random.randint(3, 5)
                    self.trigger_yawn(f"理毛完毕惬意放松，连打 {repeats} 个大哈欠~", repeats=repeats)
                    return

            if self.mood.should_sleep(now):
                self.switch_behavior(BEHAVIOR_CATALOG[BehaviorType.REST_FALL_ASLEEP], 1.35,
                                     "太困了，打着瞌睡慢慢卧下入睡~")
                return
            is_edge = self.is_at_screen_edge(margin=50)
            next_b_def, duration = self.mood.select_next_behavior(self.current_behavior.code, is_at_edge=is_edge)
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

        # 拖拽移动：硬限制在可用屏幕区域内，绝不脱离屏幕
        if self.is_dragging:
            target_pos = event.globalPosition().toPoint() - self.drag_start_pos
            self.safe_move(target_pos.x(), target_pos.y(), margin=5)
            return

        if self.current_behavior.code in (BehaviorType.REST_SLEEP, BehaviorType.REST_FALL_ASLEEP):
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
                        self.switch_behavior(BEHAVIOR_CATALOG[BehaviorType.COMFORT_BOW], None, "察觉到手停在头顶，主动低头求撸")
        else:
            self.hover_head_start_time = None

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            pos = event.position().toPoint()
            # Any click on the pet window is enough to wake a sleeping bird,
            # including a click on its transparent padding.
            if self.current_behavior.code in (BehaviorType.REST_SLEEP, BehaviorType.REST_FALL_ASLEEP):
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
            self.ensure_on_screen(margin=10)
            # 如果处于敲屏状态但被拖拽移离了屏幕边缘，立即切出敲屏
            if self.current_behavior.code == BehaviorType.EXCITE_BONK and not self.is_at_screen_edge(margin=50):
                self.switch_behavior(BEHAVIOR_CATALOG[BehaviorType.IDLE_BLINK], 3.0, "被移离屏幕边缘，停止敲屏发呆~")

    def mouseDoubleClickEvent(self, event):
        self.mousePressEvent(event)

    def handle_pet_head(self):
        """摸头交互：固定切入低头享受动作，结束后固定衔接转头理毛"""
        if self.current_behavior.code in (BehaviorType.REST_SLEEP, BehaviorType.REST_FALL_ASLEEP):
            self.wake_up("被轻轻摸醒了")
        d_co, _, msg = self.mood.pet_head()
        # 预设摸头结束后固定衔接转头理毛 (COMFORT_PREEN)
        self.pending_next_behavior = BehaviorType.COMFORT_PREEN
        # 摸头动作固定切入低头闭眼享受 (COMFORT_BOW)，持续 4.0 秒
        self.switch_behavior(BEHAVIOR_CATALOG[BehaviorType.COMFORT_BOW], 4.0, msg)

    def handle_touch_body(self):
        """戳身体禁区"""
        self.pending_next_behavior = None
        if self.current_behavior.code in (BehaviorType.REST_SLEEP, BehaviorType.REST_FALL_ASLEEP):
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
        self.pending_next_behavior = None
        if self.current_behavior.code in (BehaviorType.REST_SLEEP, BehaviorType.REST_FALL_ASLEEP):
            self.wake_up("惊醒起飞")
        rect = self.get_screen_rect(use_available=True)
        cur_x = self.x()
        cur_y = self.y()

        self.fly_start_pos = QPointF(cur_x, cur_y)
        self.is_flying = True
        self.fly_progress = 0.0
        self.flight_purpose = "panic" if panic else ("roam" if roam else "approach")
        flight_cost = 5.0 if panic else (4.0 if roam else 3.0)
        self.mood.fatigue = min(100.0, self.mood.fatigue + flight_cost)

        min_target_x = rect.left() + 25
        max_target_x = max(min_target_x, rect.right() - self.width() - 25)
        min_target_y = rect.top() + 25
        max_target_y = max(min_target_y, rect.bottom() - self.height() - 25)

        if panic:
            # 惊吓飞往远端对角
            target_x = random.randint(min_target_x, max_target_x)
            y_low = max(min_target_y, rect.bottom() - 230)
            y_high = max(min_target_y, rect.bottom() - 90)
            if y_low > y_high:
                y_low, y_high = y_high, y_low
            target_y = random.randint(y_low, min(max_target_y, y_high))
            # 避开当前点
            if abs(target_x - cur_x) < 150:
                mid_screen_x = (rect.left() + rect.right()) / 2
                target_x = min_target_x if cur_x > mid_screen_x else max_target_x
            self.fly_target_pos = QPointF(target_x, target_y)
            self.fly_duration = 1.2 # 逃跑飞得极快
            self.switch_behavior(BEHAVIOR_CATALOG[BehaviorType.FRIGHT_PANIC_FLY], 2.0, "受惊扑腾起飞逃跑！")
        elif roam:
            # Keep a clear horizontal displacement so a casual flight is visible.
            target_x = max(min_target_x, min(max_target_x, cur_x + random.choice([-1, 1]) * random.randint(130, 260)))
            if abs(target_x - cur_x) < 75:
                mid_screen_x = (rect.left() + rect.right()) / 2
                target_x = max(min_target_x, min(max_target_x, cur_x + (160 if cur_x < mid_screen_x else -160)))
            target_y = max(min_target_y, min(max_target_y, cur_y + random.randint(-45, 45)))
            self.fly_target_pos = QPointF(target_x, target_y)
            self.fly_duration = max(1.4, min(2.8, abs(target_x - cur_x) / 130.0))
            self.switch_behavior(BEHAVIOR_CATALOG[BehaviorType.IDLE_FLY],
                                 self.fly_duration, "日常扑翅飞到附近")
        else:
            # 飞往光标附近 (撒娇)
            cursor_pos = QCursor.pos()
            target_x = max(min_target_x, min(max_target_x, cursor_pos.x() + random.choice([-40, 40])))
            target_y = max(min_target_y, min(max_target_y, cursor_pos.y() + 10))
            self.fly_target_pos = QPointF(target_x, target_y)
            self.fly_duration = 2.0
            self.switch_behavior(BEHAVIOR_CATALOG[BehaviorType.COMFORT_APPROACH], 2.5, "主动飞到主人光标边上~")

        # Reference frames face left. Mirror them when the flight heads right.
        dx = self.fly_target_pos.x() - cur_x
        if abs(dx) >= 1:
            self.facing_direction = 1 if dx > 0 else -1
            self.waddle_direction = self.facing_direction
            self.update()

        # 控制点（模拟高高掠起的弧度），必须确保不冲出屏幕顶部
        mid_x = (self.fly_start_pos.x() + self.fly_target_pos.x()) / 2
        mid_y = min(self.fly_start_pos.y(), self.fly_target_pos.y()) - random.randint(60, 110)
        safe_mid_y = max(float(rect.top() + 10), mid_y)
        self.fly_control_pos = QPointF(mid_x, safe_mid_y)

        self.fly_timer.start(25) # 40 FPS 平滑插值

    def on_fly_step(self):
        step = 0.025 / self.fly_duration
        self.fly_progress += step
        if self.fly_progress >= 1.0:
            self.fly_progress = 1.0
            self.safe_move(int(self.fly_target_pos.x()), int(self.fly_target_pos.y()), margin=10)
            self.fly_timer.stop()
            self.is_flying = False
            # 落地动作
            if self.flight_purpose == "panic" or self.mood.fright > 40.0:
                self.switch_behavior(BEHAVIOR_CATALOG[BehaviorType.FRIGHT_ALERT], 3.0, "惊险降落，警惕拉直身子")
            elif self.flight_purpose == "roam":
                self.switch_behavior(BEHAVIOR_CATALOG[BehaviorType.IDLE_BLINK], 2.0, "飞了一小段，落地休息")
            else:
                self.switch_behavior(BEHAVIOR_CATALOG[BehaviorType.COMFORT_BOW], None, "亲切降落，在鼠标边低头求撸")
            return

        # 二阶贝塞尔曲线插值: B(t) = (1-t)^2 * P0 + 2t(1-t) * P1 + t^2 * P2
        t = self.fly_progress
        bx = (1 - t)**2 * self.fly_start_pos.x() + 2 * t * (1 - t) * self.fly_control_pos.x() + t**2 * self.fly_target_pos.x()
        by = (1 - t)**2 * self.fly_start_pos.y() + 2 * t * (1 - t) * self.fly_control_pos.y() + t**2 * self.fly_target_pos.y()
        self.safe_move(int(bx), int(by), margin=5)

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
        dev_mode = is_dev_mode()

        # 1. 仪表盘开关
        act_hud = menu.addAction("📊 开启/关闭 心态雷达监视器")

        # 2. 羽冠造型切换
        crest_menu = menu.addMenu("👑 羽冠造型切换")
        act_crest_classic = crest_menu.addAction("🐰 经典兔耳羽冠 (原始双叉)")
        act_crest_triple = crest_menu.addAction("✨ 灵动三毛羽冠 (反曲重叠)")
        act_crest_classic.setCheckable(True)
        act_crest_triple.setCheckable(True)
        if self.crest_style == "classic":
            act_crest_classic.setChecked(True)
        else:
            act_crest_triple.setChecked(True)

        # 3. 开机自启 (仅支持 Windows)
        act_autostart = menu.addAction("🚀 开机自启")
        if is_auto_start_supported():
            act_autostart.setCheckable(True)
            act_autostart.setChecked(is_auto_start_enabled())
        else:
            act_autostart.setEnabled(False)
            act_autostart.setText("🚀 开机自启 (仅支持Windows)")

        menu.addSeparator()

        # 4. 清空疲劳与 5. 强制睡眠 (发布版与开发版均保留的核心控制)
        act_clear_fatigue = menu.addAction("⚡ 清空疲劳 (瞬间回满)")
        act_sleep = menu.addAction("💤 强制睡眠 (疲劳拉满)")

        # 仅开发调试模式显示的注入选项
        if dev_mode:
            menu.addSeparator()
            act_sing = menu.addAction("🎵 逗它开心吹口哨")
            act_hop = menu.addAction("🦘 移动雀跃小跳 (开心蹦跶)")
            act_bonk = menu.addAction("🥁 敲击屏幕边缘 (自嗨敲屏)")
            act_double_peck = menu.addAction("⚡ 连环双击啄桌 (兴奋连啄)")
            act_play_ball = menu.addAction("🔴 兴奋杂技踩球 (30秒巡游)")
            act_peck = menu.addAction("🌾 闲置自然啄食 (单啄嚼米)")
            act_waddle = menu.addAction("🚶 摇晃溜达 (双模式漫步)")
            act_preen = menu.addAction("🪶 整理羽毛 (埋背理毛)")
            act_fluff = menu.addAction("🐡 蓬成毛球 (平缓起伏)")
            act_yawn = menu.addAction("🥱 伸脖打大哈欠 (仰头3px)")
            act_fly = menu.addAction("🕊️ 舒展振翅飞翔 (有机动力学)")
            act_fright = menu.addAction("⚡ 戳身反咬威慑 (嘴前辐射音波)")
            act_reset = menu.addAction("🔄 重置心态为平静")
        else:
            act_sing = None
            act_hop = None
            act_bonk = None
            act_double_peck = None
            act_play_ball = None
            act_peck = None
            act_waddle = None
            act_preen = None
            act_fluff = None
            act_yawn = None
            act_fly = None
            act_fright = None
            act_reset = None

        menu.addSeparator()
        # 5. 退出
        act_quit = menu.addAction("❌ 告别退出")

        res = menu.exec(global_pos)
        if res == act_hud:
            if self.hud_window:
                if self.hud_window.isVisible():
                    self.hud_window.hide()
                else:
                    self.hud_window.show()
        elif res == act_crest_classic:
            self.switch_crest_style("classic")
        elif res == act_crest_triple:
            self.switch_crest_style("triple")
        elif act_autostart and res == act_autostart:
            target_state = not is_auto_start_enabled()
            ok, msg = set_auto_start(target_state)
            if ok:
                status_txt = "已开启" if target_state else "已关闭"
                self.last_feedback = f"开机自启{status_txt}"
                tip_msg = f"🚀 开机自启{status_txt}"
            else:
                self.last_feedback = f"自启设置失败: {msg}"
                tip_msg = f"❌ {self.last_feedback}"
            if self.hud_window:
                self.hud_window.update_view()
            QToolTip.showText(global_pos, tip_msg, self)
        elif res == act_clear_fatigue:
            self.clear_fatigue("右键菜单触发：疲劳度已直接清空！")
        elif res == act_sleep:
            self.force_sleep("右键菜单触发：疲劳度拉满，打瞌睡卧下入睡")
        elif act_sing and res == act_sing:
            if self.current_behavior.code in (BehaviorType.REST_SLEEP, BehaviorType.REST_FALL_ASLEEP):
                self.wake_up("被歌声唤醒了")
            self.mood.excitement = 90.0
            self.switch_behavior(BEHAVIOR_CATALOG[BehaviorType.EXCITE_SING], None, "被主人逗乐，开心大声独唱！")
        elif act_hop and res == act_hop:
            self.trigger_hop("右键菜单触发：欢快移动连环小跳！")
        elif act_bonk and res == act_bonk:
            self.trigger_bonk("右键菜单触发：靠边敲击屏幕！")
        elif act_double_peck and res == act_double_peck:
            if self.current_behavior.code in (BehaviorType.REST_SLEEP, BehaviorType.REST_FALL_ASLEEP):
                self.wake_up("被叫醒起来连环啄米")
            self.mood.excitement = max(self.mood.excitement, 70.0)
            self.switch_behavior(BEHAVIOR_CATALOG[BehaviorType.EXCITE_DOUBLE_PECK], None, "右键菜单触发：兴奋连环双击啄桌！")
        elif act_play_ball and res == act_play_ball:
            if self.current_behavior.code in (BehaviorType.REST_SLEEP, BehaviorType.REST_FALL_ASLEEP):
                self.wake_up("被红球吸引醒来！")
            self.mood.excitement = max(self.mood.excitement, 75.0)
            self.switch_behavior(BEHAVIOR_CATALOG[BehaviorType.EXCITE_PLAY_BALL], None, "右键菜单触发：兴奋杂技踩球！")
        elif act_peck and res == act_peck:
            if self.current_behavior.code in (BehaviorType.REST_SLEEP, BehaviorType.REST_FALL_ASLEEP):
                self.wake_up("被叫醒起来啄米")
            self.switch_behavior(BEHAVIOR_CATALOG[BehaviorType.IDLE_PECK], None, "右键菜单触发：闲置自然啄食！")
        elif act_waddle and res == act_waddle:
            if self.current_behavior.code in (BehaviorType.REST_SLEEP, BehaviorType.REST_FALL_ASLEEP):
                self.wake_up("被叫醒起来溜达")
            self.switch_behavior(BEHAVIOR_CATALOG[BehaviorType.IDLE_WADDLE], None, "右键菜单触发：摇晃溜达漫步！")
        elif act_preen and res == act_preen:
            if self.current_behavior.code in (BehaviorType.REST_SLEEP, BehaviorType.REST_FALL_ASLEEP):
                self.wake_up("被叫醒起来整理羽毛")
            self.switch_behavior(BEHAVIOR_CATALOG[BehaviorType.COMFORT_PREEN], None, "右键菜单触发：转头埋背整理羽毛！")
        elif act_fluff and res == act_fluff:
            if self.current_behavior.code in (BehaviorType.REST_SLEEP, BehaviorType.REST_FALL_ASLEEP):
                self.wake_up("被叫醒起来蓬成毛球")
            self.switch_behavior(BEHAVIOR_CATALOG[BehaviorType.COMFORT_FLUFF], None, "右键菜单触发：舒适蓬成毛球！")
        elif act_yawn and res == act_yawn:
            self.trigger_yawn("右键菜单触发：伸脖打大哈欠！")
        elif act_fly and res == act_fly:
            self.start_flight(panic=False, roam=True)
        elif act_fright and res == act_fright:
            self.handle_touch_body()
        elif act_reset and res == act_reset:
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
