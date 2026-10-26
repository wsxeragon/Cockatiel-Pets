import os
import sys
import time
import math
import random
import json
from typing import Dict, Optional

from PySide6.QtCore import Qt, QTimer, QPoint, QPointF, QRect
from PySide6.QtGui import QPixmap, QPainter, QCursor, QAction, QTransform, QIcon
from PySide6.QtWidgets import QWidget, QMenu, QApplication, QToolTip, QMessageBox, QProgressDialog

from models import MoodDynamics, BehaviorType, BEHAVIOR_CATALOG, BehaviorDef, EXCITED_BEHAVIORS
from config import get_base_dir, is_dev_mode, is_poop_disabled, set_poop_disabled
from autostart import is_auto_start_supported, is_auto_start_enabled, set_auto_start
from updater import CheckUpdateWorker, DownloadUpdateWorker, launch_updater_and_exit, APP_VERSION
from poop_item_window import PoopItemWindow

class CockatielWindow(QWidget):
    """原始灰玄凤鹦鹉主桌宠窗口 (透明通道、无边框、置顶)"""
    def __init__(self, start_with_fly_in: bool = False):
        super().__init__()
        self.is_exiting: bool = False # 退出离场飞行标记
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

        # 鼠标拖拽状态与预定待执行行为
        self.is_dragging: bool = False
        self.drag_start_pos: QPoint = QPoint()
        self.hover_head_start_time: Optional[float] = None
        self.pending_next_behavior: Optional[BehaviorType] = None
        self.yawn_remaining_repeats: int = 0

        # 在线自动更新控制器
        self._update_checker: Optional[CheckUpdateWorker] = None
        self._update_downloader: Optional[DownloadUpdateWorker] = None
        self._download_dialog: Optional[QProgressDialog] = None

        # 摸头互动与阶梯概率理毛引擎 (点1下20%, 点2下30%, 点3下40%...)
        self.head_pet_count: int = 0          # 摸头累计点击次数
        self.head_pet_active: bool = False    # 标记当前是否处于摸头等待后续动作状态
        self.last_head_pet_time: float = 0.0  # 上次摸头时间戳 (用于连击间隔判定与超时重置)

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

        # 动画帧切换定时器 (使用高精度定时器保证高帧率平滑稳定)
        self.anim_timer = QTimer(self)
        self.anim_timer.setTimerType(Qt.TimerType.PreciseTimer)
        self.anim_timer.timeout.connect(self.on_anim_frame_step)
        self.anim_timer.start(self.current_behavior.frame_interval_ms)

        # 待机微动画定时器 (60ms)：驱动呼吸 / 眨眼 / 冠羽的随机事件
        self.idle_timer = QTimer(self)
        self.idle_timer.timeout.connect(self.on_idle_tick)
        self.idle_timer.start(60)

        # 随地大小便动力学与实体管理 (前30分钟概率为0，30~60分钟概率从0线性增至100%)
        self.active_poops: List[PoopItemWindow] = []
        self.is_poop_disabled: bool = is_poop_disabled()
        self.last_poop_time: float = time.time()
        self.next_poop_target_time: float = self.last_poop_time + 3600.0
        self.poop_timer = QTimer(self)
        self.poop_timer.timeout.connect(self.on_poop_timer_tick)
        self._schedule_next_poop()

        # 啃咬植物动画镜像状态与原点坐标记录
        self.is_plant_chew_mirrored: bool = False
        self._plant_chew_orig_x: int = 0
        self._plant_chew_orig_y: int = 0

        # 变魔术动画镜像状态记录 (面向右时镜像向右展开，连续多次瞬移时镜像交替免转身)
        self.is_magic_mirrored: bool = False

        # 极限滑板动画状态记录 (真实桌面滑行、长边优先、短道提前跳下、往返镜像)
        self.is_skateboard_mirrored: bool = False
        self.skateboard_remaining_repeats: int = 0
        self.skateboard_total_repeats: int = 2
        self.skateboard_slide_dir: int = 1
        self.skateboard_cruise_speed: float = 8.0
        self.skateboard_dismount_frame: int = 69

        # 初始化位置 (屏幕右下角靠近任务栏，完全限制在可用可视区域内)
        rect = self.get_screen_rect(use_available=True)
        init_x = rect.right() - self.width() - 30
        init_y = rect.bottom() - self.height() - 20
        self.safe_move(init_x, init_y, margin=10)

        # 若开启开机飞入动画，立即执行屏幕外入场飞行动力学
        if start_with_fly_in:
            self.start_fly_in()

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

    def apply_window_geometry(self, x: int, y: int, w: int, h: int, margin: int = 10):
        """同时原子更新窗口大小与屏幕约束坐标，避免先缩放再位移产生的贴图撕裂与瞬间闪烁"""
        rect = self.get_screen_rect(use_available=True)
        min_x = rect.left() + margin
        max_x = max(min_x, rect.right() - w - margin + 1)
        min_y = rect.top() + margin
        max_y = max(min_y, rect.bottom() - h - margin + 1)
        clamped_x = max(min_x, min(max_x, x))
        clamped_y = max(min_y, min(max_y, y))

        if self.width() == w and self.height() == h:
            self.move(clamped_x, clamped_y)
        else:
            self.setMinimumSize(0, 0)
            self.setMaximumSize(16777215, 16777215)
            self.setGeometry(clamped_x, clamped_y, w, h)
            self.setFixedSize(w, h)


    def ensure_on_screen(self, margin: int = 10):
        """保底卫士：如果当前桌宠超出屏幕可视区域，立即平滑拉回屏幕内"""
        # 飞行中或退出离场中不强制纠偏，避免打断飞翔抛物线
        if self.is_flying or getattr(self, "is_exiting", False):
            return
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

    # -------------------------------------------------------------
    # 在线检查更新与全量升级核心逻辑
    # -------------------------------------------------------------
    def check_for_updates(self):
        """手动触发在线版本检查（右键菜单点击触发）"""
        if self._update_checker and self._update_checker.isRunning():
            return
        self.last_feedback = "正在连接 GitHub 检查最新版本..."
        self._update_checker = CheckUpdateWorker(self)
        self._update_checker.check_finished.connect(self.on_check_update_finished)
        self._update_checker.start()

    def on_check_update_finished(self, success: bool, info: dict, error_msg: str):
        self._update_checker = None
        if not success:
            self.last_feedback = "检查更新失败"
            QMessageBox.warning(self, "检查更新", f"检查更新遇到问题：\n{error_msg}\n\n请检查网络连接后重试。")
            return

        has_update = info.get("has_update", False)
        cloud_tag = info.get("tag_name", "")
        if not has_update:
            self.last_feedback = f"当前已是最新版 ({APP_VERSION})"
            QMessageBox.information(
                self,
                "检查更新",
                f"当前已是最新版本 ({APP_VERSION})！\n\n小玄凤状态绝佳，暂无可用新版本~"
            )
            return

        # 发现新版本，弹出更新询问对话框
        self.last_feedback = f"发现新版本: {cloud_tag}！"
        title = info.get("title", "") or cloud_tag
        body = info.get("body", "") or "优化了体验并修复已知问题。"
        size_mb = info.get("size_bytes", 0) / (1024 * 1024)
        pkg_desc = info.get("package_desc", "")
        pkg_display = f"{pkg_desc}" if pkg_desc else (f"安装包约 {size_mb:.1f} MB" if size_mb > 0 else "安装包")
        decision_reason = info.get("decision_reason", "")
        reason_html = f"<p style='color:#555;'><small>💡 <b>更新策略</b>：{decision_reason}</small></p>" if decision_reason else ""

        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("发现小玄凤新版本！")
        msg_box.setIcon(QMessageBox.Information)
        body_html = body.replace("\r\n", "\n").replace("\n", "<br>")
        msg_text = (
            f"<h3>🐤 发现新版本：{cloud_tag}</h3>"
            f"<p><b>当前版本</b>：{APP_VERSION}<br>"
            f"<b>最新版本</b>：{cloud_tag} ({pkg_display})</p>"
            f"{reason_html}"
            f"<p><b>【更新说明】</b><br>{body_html}</p>"
            f"<p>是否立即下载新版本并自动更新？</p>"
        )
        msg_box.setText(msg_text)
        btn_update = msg_box.addButton("立即更新", QMessageBox.AcceptRole)
        btn_cancel = msg_box.addButton("稍后再说", QMessageBox.RejectRole)
        msg_box.setDefaultButton(btn_update)
        msg_box.exec()

        if msg_box.clickedButton() == btn_update:
            self.start_download_update(info)

    def start_download_update(self, info: dict):
        download_url = info.get("download_url", "")
        if not download_url:
            QMessageBox.warning(self, "更新错误", "未能从最新发布包中找到可供下载的安装包附件，请稍后再试。")
            return

        expected_size = info.get("size_bytes", 0)
        cloud_tag = info.get("tag_name", "")

        # 初始化下载进度弹窗
        self._download_dialog = QProgressDialog(f"正在准备下载新版本 {cloud_tag}...", "取消", 0, 100, self)
        self._download_dialog.setWindowTitle(f"下载更新包 ({cloud_tag})")
        self._download_dialog.setWindowModality(Qt.WindowModal)
        self._download_dialog.setMinimumDuration(0)
        self._download_dialog.setValue(0)
        self._download_dialog.canceled.connect(self.cancel_download_update)
        self._download_dialog.show()

        self._update_downloader = DownloadUpdateWorker(download_url, expected_size)
        self._update_downloader.progress.connect(self.on_download_progress)
        self._update_downloader.finished.connect(self.on_download_finished)
        self._update_downloader.start()

    def on_download_progress(self, percent: int, downloaded: int, total: int):
        if self._download_dialog and self._download_dialog.isVisible():
            self._download_dialog.setValue(percent)
            d_mb = downloaded / (1024 * 1024)
            t_mb = total / (1024 * 1024)
            if total > 0:
                self._download_dialog.setLabelText(f"正在下载全量安装包... {percent}%\n({d_mb:.1f} MB / {t_mb:.1f} MB)")
            else:
                self._download_dialog.setLabelText(f"正在下载全量安装包... 已下载 {d_mb:.1f} MB")

    def cancel_download_update(self):
        if self._update_downloader:
            self._update_downloader.cancel()
        self.last_feedback = "已取消下载更新"

    def on_download_finished(self, success: bool, zip_path: str, error_msg: str):
        if self._download_dialog:
            self._download_dialog.close()
            self._download_dialog = None
        self._update_downloader = None

        if not success:
            if "取消" not in error_msg:
                QMessageBox.critical(self, "下载失败", f"更新包下载失败：\n{error_msg}\n\n请稍后重试。")
            return

        # 下载完成，询问用户是否立即重启更新
        reply = QMessageBox.question(
            self,
            "下载完成",
            "小玄凤新版本安装包已下载完成！\n\n需要重启桌宠以完成自动解压与覆盖更新。\n是否立即重启小玄凤？",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.Yes
        )
        if reply == QMessageBox.Yes:
            self.last_feedback = "正在启动独立更新器并重启..."
            try:
                launch_updater_and_exit(zip_path)
            except Exception as e:
                QMessageBox.critical(
                    self,
                    "启动更新器失败",
                    f"启动独立更新器遇到异常：\n{e}\n\n更新包已安全保存在：\n{zip_path}\n您可以手动解压其中的文件覆盖完成更新。"
                )
        else:
            self.last_feedback = "更新包已保存，下次启动前可随时更新"

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
            frame_name = "idle_0"
            pix = self.sprites.get("idle_0", QPixmap())
        else:
            frame_name = frames[self.current_frame_index % len(frames)]
            pix = self.sprites.get(frame_name, self.sprites.get("idle_0", QPixmap()))

        # 玩球动作自带完整左右舞台编排与朝向，不作全局镜像翻转
        if self.current_behavior.code == BehaviorType.EXCITE_PLAY_BALL:
            return pix

        # 变魔术动作：由 is_magic_mirrored 控制是否进行整体镜像翻转
        if self.current_behavior.code == BehaviorType.MAGIC_TRICK:
            if getattr(self, 'is_magic_mirrored', False) and not pix.isNull():
                return pix.transformed(QTransform().scale(-1, 1))
            return pix

        # 极限滑板动作：由 is_skateboard_mirrored 控制是否进行整体镜像翻转 (往返第二遍向左)
        if self.current_behavior.code == BehaviorType.SKATEBOARD:
            if getattr(self, 'is_skateboard_mirrored', False) and not pix.isNull():
                return pix.transformed(QTransform().scale(-1, 1))
            return pix

        # 啃咬植物动作：由 is_plant_chew_mirrored 控制是否进行整体镜像翻转
        if self.current_behavior.code == BehaviorType.EAT_PLANT:
            if getattr(self, 'is_plant_chew_mirrored', False) and not pix.isNull():
                return pix.transformed(QTransform().scale(-1, 1))
            return pix

        # 所有原始帧面向左，只有朝右时镜像。
        if self.facing_direction == 1 and not pix.isNull():
            # 睡觉状态朝右时：使用专用右朝向帧 (sleep_0_r, sleep_1_r)，
            # 保证鸟体镜像朝右的同时，呼噜 Z 字符始终保持正向，绝不反转为镜像字符
            if frame_name in ("sleep_0", "sleep_1"):
                r_name = f"{frame_name}_r"
                if r_name in self.sprites and not self.sprites[r_name].isNull():
                    return self.sprites[r_name]
            return pix.transformed(QTransform().scale(-1, 1))
        return pix

    def switch_behavior(self, new_b_def: BehaviorDef, duration: Optional[float] = None, feedback: str = None):
        self.setUpdatesEnabled(False)
        try:
            old_behavior_code = self.current_behavior.code if self.current_behavior else None
            if duration is None:
                duration = max(1.0, random.gauss(new_b_def.duration_mean, new_b_def.duration_std))

            # 从玩球切出时 (无论是正常结束还是被打断)，恢复标准 100x80 画布并平滑对齐地面与鸟体坐标
            # 鸟在最后一帧展翅飞下地面并站立于 bcx=84, ground y=98
            # 标准 100x80 中，鸟中心 x=53, ground y=72
            if self.current_behavior and self.current_behavior.code == BehaviorType.EXCITE_PLAY_BALL and new_b_def.code != BehaviorType.EXCITE_PLAY_BALL:
                restore_x = self.x() + 84 - 53
                restore_y = self.y() + 98 - 72
                self.apply_window_geometry(restore_x, restore_y, 100, 80, margin=10)

            # 从啃咬植物切出时：恢复标准 100x80 画布并无缝衔接鸟体当前屏幕坐标，绝不消失或瞬移
            if self.current_behavior and self.current_behavior.code == BehaviorType.EAT_PLANT and new_b_def.code != BehaviorType.EAT_PLANT:
                is_mirrored = getattr(self, 'is_plant_chew_mirrored', False)
                if new_b_def.code == BehaviorType.IDLE_WADDLE:
                    # 自然完成：鸟在最后一帧位于 bx=125, by=10，无缝顺承至当前位置继续漫步
                    bx_end = 125
                    by_end = 10
                    if is_mirrored:
                        target_x = self.x() + (140 - bx_end)
                        exit_dir = -1
                    else:
                        target_x = self.x() + bx_end
                        exit_dir = 1
                    target_y = self.y() + by_end
                    self.apply_window_geometry(target_x, target_y, 100, 80, margin=10)
                    self.facing_direction = exit_dir
                    self.waddle_direction = exit_dir
                    self.waddle_origin_x = target_x
                    self.waddle_step_count = 0
                    self.waddle_consecutive_steps = 0
                    self.waddle_mode = "straight_to_edge"
                else:
                    # 异常强行打断时：平稳恢复原站立坐标
                    orig_x = getattr(self, '_plant_chew_orig_x', self.x())
                    orig_y = getattr(self, '_plant_chew_orig_y', self.y())
                    self.apply_window_geometry(orig_x, orig_y, 100, 80, margin=10)

            # 从变魔术切出时 (无论是正常结束还是被打断)，恢复标准 100x80 画布并平滑对齐地面与鸟体坐标
            if self.current_behavior and self.current_behavior.code == BehaviorType.MAGIC_TRICK and new_b_def.code != BehaviorType.MAGIC_TRICK:
                self.magic_remaining_repeats = 0
                is_mirrored = getattr(self, 'is_magic_mirrored', False)
                if is_mirrored:
                    # 镜像模式结束：鸟在最后一帧位于 bx=5, by=26，面向左
                    restore_x = self.x() + 5
                    restore_y = self.y() + 26
                    exit_dir = -1
                else:
                    # 标准模式结束：鸟在最后一帧位于 bx=155, by=26，面向右
                    restore_x = self.x() + 155
                    restore_y = self.y() + 26
                    exit_dir = 1
                self.apply_window_geometry(restore_x, restore_y, 100, 80, margin=10)
                self.facing_direction = exit_dir
                if new_b_def.code == BehaviorType.IDLE_WADDLE:
                    self.waddle_direction = exit_dir
                    self.waddle_origin_x = restore_x
                    self.waddle_step_count = 0
                    self.waddle_consecutive_steps = 0
                    self.waddle_mode = "straight_to_edge"
                self.is_magic_mirrored = None

            # 从滑板切出时 (无论是正常结束还是被打断)，恢复标准 100x80 画布并平滑对齐地面与鸟体坐标
            if self.current_behavior and self.current_behavior.code == BehaviorType.SKATEBOARD and new_b_def.code != BehaviorType.SKATEBOARD:
                self.skateboard_remaining_repeats = 0
                is_mirrored = getattr(self, 'is_skateboard_mirrored', False)
                restore_x = self.x() + 50
                restore_y = self.y() + 14
                self.apply_window_geometry(restore_x, restore_y, 100, 80, margin=10)
                self.facing_direction = -1 if is_mirrored else 1
                self.is_skateboard_mirrored = False

            # 进入玩球时，临时扩容为 260x120 高清像素舞台，并无缝贴合原站立点
            if new_b_def.code == BehaviorType.EXCITE_PLAY_BALL:
                rect = self.get_screen_rect(use_available=True)
                target_x = self.x() + 53 - 175
                target_y = self.y() + 72 - 98
                target_x = max(rect.left() + 10, min(rect.right() - 260 - 10, target_x))
                target_y = max(rect.top() + 10, min(rect.bottom() - 120 - 10, target_y))
                self.apply_window_geometry(target_x, target_y, 260, 120, margin=10)
                self.facing_direction = -1
                duration = 60.0  # 提供充分的冗余时间，由最后一帧自然驱动谢幕切出，绝不被时钟截断

            # 进入啃咬植物时，临时扩容为 240x90 舞台，并无缝贴合原站立点
            if new_b_def.code == BehaviorType.EAT_PLANT:
                self._plant_chew_orig_x = self.x()
                self._plant_chew_orig_y = self.y()
                rect = self.get_screen_rect(use_available=True)

                if not hasattr(self, 'is_plant_chew_mirrored') or self.is_plant_chew_mirrored is None:
                    margin = 200
                    cur_x = self.x()
                    if cur_x < rect.left() + margin:
                        self.is_plant_chew_mirrored = True
                    elif cur_x > rect.right() - self.width() - margin:
                        self.is_plant_chew_mirrored = False
                    else:
                        self.is_plant_chew_mirrored = (self.facing_direction == 1)

                if self.is_plant_chew_mirrored:
                    target_x = self.x() + 36
                    self.facing_direction = 1
                else:
                    target_x = self.x() - 160
                    self.facing_direction = -1

                target_y = self.y() - 10
                self.apply_window_geometry(target_x, target_y, 240, 90, margin=10)
                duration = 60.0

            # 进入变魔术时，临时扩容为 260x120 舞台，并无缝贴合原站立点
            if new_b_def.code == BehaviorType.MAGIC_TRICK:
                if not getattr(self, 'magic_remaining_repeats', 0):
                    self.magic_remaining_repeats = random.randint(1, 4)
                    self.magic_total_repeats = self.magic_remaining_repeats

                rect = self.get_screen_rect(use_available=True)
                if getattr(self, 'is_magic_mirrored', None) is None:
                    margin = 170
                    cur_x = self.x()
                    if cur_x < rect.left() + margin:
                        self.is_magic_mirrored = True   # 靠左屏幕：向右镜像展开
                    elif cur_x > rect.right() - self.width() - margin:
                        self.is_magic_mirrored = False  # 靠右屏幕：向左标准展开
                    else:
                        self.is_magic_mirrored = (self.facing_direction == 1)

                self._magic_orig_x = self.x()
                self._magic_orig_y = self.y()
                if self.is_magic_mirrored:
                    # 镜像模式：鸟在 frame 0 位于 bx=5，面向右
                    target_x = self.x() - 5
                    self.facing_direction = 1
                else:
                    # 标准模式：鸟在 frame 0 位于 bx=155，面向左
                    target_x = self.x() - 155
                    self.facing_direction = -1

                target_y = self.y() - 26
                self.apply_window_geometry(target_x, target_y, 260, 120, margin=10)
                duration = 60.0

            # 进入滑板时，临时扩容为 200x110 舞台，并无缝贴合原站立点
            if new_b_def.code == BehaviorType.SKATEBOARD:
                if not getattr(self, 'skateboard_remaining_repeats', 0):
                    self.skateboard_remaining_repeats = 2
                    self.skateboard_total_repeats = self.skateboard_remaining_repeats
                    self.prepare_skateboard_round(is_first_round=True)
                target_x = self.x() - 50
                target_y = self.y() - 14
                self.apply_window_geometry(target_x, target_y, 200, 110, margin=10)
                self.skateboard_exact_x = float(self.x())
                duration = 60.0

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

            if new_b_def.code not in (BehaviorType.COMFORT_BOW, BehaviorType.COMFORT_PREEN):
                self.head_pet_active = False

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
                # 若是从啃咬植物或变魔术无缝衔接切入，保留已对齐的行走方向与模式，不作随机覆盖
                if old_behavior_code not in (BehaviorType.EAT_PLANT, BehaviorType.MAGIC_TRICK):
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
        finally:
            self.setUpdatesEnabled(True)
        self.update()

    def wake_up(self, reason: str):
        """End sleep once, then prevent an immediate return to sleep."""
        if self.current_behavior.code not in (BehaviorType.REST_SLEEP, BehaviorType.REST_FALL_ASLEEP):
            return
        now = time.time()
        self.pending_next_behavior = None
        self.head_pet_active = False
        self.head_pet_count = 0
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

    def get_poop_probability(self) -> float:
        """
        计算当前排便发生概率 (0.0 ~ 1.0):
        - 开启‘禁止随地大小便’时固定为 0.0
        - 每次排便完重置为 0.0
        - 前 30 分钟 (0 ~ 1800 秒) 概率严格保持为 0.0，不产生任何增长
        - 30 ~ 60 分钟 (1800 ~ 3600 秒) 随着时间流逝，概率从 0.0 线性增至 1.0 (0% ~ 100%)
        - 超过 60 分钟 (>= 3600 秒) 概率为 1.0 (100% 必然发生便意)
        """
        if self.is_poop_disabled:
            return 0.0
        elapsed = time.time() - self.last_poop_time
        if elapsed < 1800.0:
            return 0.0
        elif elapsed >= 3600.0:
            return 1.0
        else:
            return (elapsed - 1800.0) / 1800.0

    def _schedule_next_poop(self):
        """
        根据概率动力学模型抽取下一次排便的目标触发时刻：
        - 前 30 分钟概率为 0 (1800s 内绝不排便)
        - 30 ~ 60 分钟内累计概率从 0% 均匀增长至 100%
        - 逆变换抽样：next_time = last_poop_time + 1800 + random() * 1800
        - 巡检定时器每 5 秒检查一次生理状态与目标时间
        """
        roll = random.random()
        self.next_poop_target_time = self.last_poop_time + 1800.0 + roll * 1800.0
        self.poop_timer.start(5000)

    def on_poop_timer_tick(self):
        """定期巡检排便生理状态 (每 5 秒)"""
        if self.is_poop_disabled:
            return
        if self.is_dragging or self.is_flying:
            return
        if self.current_behavior.code in (BehaviorType.REST_SLEEP, BehaviorType.REST_FALL_ASLEEP):
            return
        if self.current_behavior.code in (BehaviorType.EXCITE_PLAY_BALL, BehaviorType.POOP, BehaviorType.EAT_PLANT, BehaviorType.MAGIC_TRICK, BehaviorType.SKATEBOARD):
            return

        now = time.time()
        elapsed = now - self.last_poop_time
        # 前 30 分钟概率严格为 0，不排便
        if elapsed < 1800.0:
            return

        # 达到目标排便时间点 (30~60分钟之间按概率到达)
        if now >= self.next_poop_target_time:
            self.trigger_poop("便意达到临界点，后退深蹲便便！")

    def trigger_poop(self, reason: str = "后退深蹲排便") -> bool:
        """触发后退深蹲排便行为 (非打断性动作)"""
        if self.is_poop_disabled:
            self.last_feedback = "当前已开启‘禁止随地大小便’，小玄凤忍住了便意~"
            if self.hud_window:
                self.hud_window.update_view()
            return False
        if self.is_dragging or self.is_flying:
            return False
        if self.current_behavior.code in (BehaviorType.REST_SLEEP, BehaviorType.REST_FALL_ASLEEP):
            self.wake_up("被便意唤醒了")
        self.switch_behavior(BEHAVIOR_CATALOG[BehaviorType.POOP], 4.5, reason)
        if self.hud_window:
            self.hud_window.update_view()
        return True

    def spawn_poop_at_tail(self):
        """在尾部排泄口位置生成大便实体悬浮窗并重置便意概率"""
        if self.is_poop_disabled:
            return

        # 鸟面向左 (-1) 时，泄殖腔在右侧；面向右 (1) 时在左侧 (适配 26x22 紧凑马赛克大便)
        if self.facing_direction == -1:
            spawn_x = self.x() + 53
        else:
            spawn_x = self.x() + 21

        spawn_y = self.y() + 50
        poop = PoopItemWindow(spawn_x, spawn_y)
        poop.cleaned.connect(self._on_poop_cleaned)
        self.active_poops.append(poop)

        # 排泄完成：便意概率立即重置为 0，开启下一轮生理周期
        self.last_poop_time = time.time()
        self._schedule_next_poop()

        self.last_feedback = "噗嗤~ 原地留下一坨热腾腾的马赛克大便！"
        if self.hud_window:
            self.hud_window.update_view()

    def _on_poop_cleaned(self, poop: PoopItemWindow):
        if poop in self.active_poops:
            self.active_poops.remove(poop)
        self.last_feedback = "✨ 大便已被主人清理干净啦，桌面干干净净！"
        if self.hud_window:
            self.hud_window.update_view()

    def toggle_disable_poop(self):
        """切换是否禁止随地大小便，并保存至配置"""
        self.is_poop_disabled = not self.is_poop_disabled
        set_poop_disabled(self.is_poop_disabled)
        if self.is_poop_disabled:
            self.poop_timer.stop()
            self.last_feedback = "🚯 已开启‘禁止随地大小便’"
        else:
            self._schedule_next_poop()
            self.last_feedback = "💩 已允许自然排泄 (前30分概率为0，30~60分渐增至100%)"
        if self.hud_window:
            self.hud_window.update_view()

    def trigger_eat_plant(self, reason: str = "趣味啃咬植物"):
        """触发啃咬植物行为，自动根据当前屏幕位置与朝向决策标准/镜像模式"""
        rect = self.get_screen_rect(use_available=True)
        margin = 200
        cur_x = self.x()

        if cur_x < rect.left() + margin:
            self.is_plant_chew_mirrored = True  # 靠左屏幕：向右镜像
        elif cur_x > rect.right() - self.width() - margin:
            self.is_plant_chew_mirrored = False # 靠右屏幕：向左标准
        else:
            self.is_plant_chew_mirrored = (self.facing_direction == 1)

        self.switch_behavior(BEHAVIOR_CATALOG[BehaviorType.EAT_PLANT], None, reason)

    def trigger_magic_trick(self, reason: str = "红色幕布变魔术", repeats: Optional[int] = None):
        """触发变魔术跨屏瞬移行为，每次触发随机重复 1-4 次"""
        if repeats is None:
            repeats = random.randint(1, 4)
        self.magic_remaining_repeats = repeats
        self.magic_total_repeats = repeats

        # 初始镜像判定：根据当前屏幕边缘与朝向决定初始演出方向
        rect = self.get_screen_rect(use_available=True)
        margin = 170
        cur_x = self.x()
        if cur_x < rect.left() + margin:
            self.is_magic_mirrored = True   # 靠左屏幕：向右镜像展开
        elif cur_x > rect.right() - self.width() - margin:
            self.is_magic_mirrored = False  # 靠右屏幕：向左标准展开
        else:
            self.is_magic_mirrored = (self.facing_direction == 1)

        self.switch_behavior(BEHAVIOR_CATALOG[BehaviorType.MAGIC_TRICK], None, f"{reason} (巡回魔术 {repeats} 场)")

    def teleport_magic_window(self):
        """变魔术瞬移：在全透明帧将窗口无感移至桌面全新随机坐标"""
        rect = self.get_screen_rect(use_available=True)
        # 为连续瞬移的镜像交替保留左右各 180px 安全缓冲区，确保下一场加减 150px 时永不撞墙出界
        margin_x = 180
        min_x = rect.left() + margin_x
        max_x = max(min_x, rect.right() - 260 - margin_x)
        min_y = rect.top() + 50
        max_y = max(min_y, rect.bottom() - 120 - 30)
        
        cur_x, cur_y = self.x(), self.y()
        rand_x, rand_y = cur_x, cur_y
        for _ in range(25):
            rx = random.randint(min_x, max_x)
            ry = random.randint(min_y, max_y)
            if math.hypot(rx - cur_x, ry - cur_y) >= 280:
                rand_x, rand_y = rx, ry
                break
        else:
            rand_x = random.randint(min_x, max_x)
            rand_y = random.randint(min_y, max_y)
            
        self.safe_move(rand_x, rand_y, margin=10)

    def prepare_skateboard_round(self, is_first_round: bool = False):
        """
        初始化/重置单趟滑板的滑动方向与巡航距离：
        1. 第一轮启动时：检测屏幕左右可用空间，智能选择‘长边’作为首次滑动的方向；
           第二轮启动时：反转方向，向对侧（此时对侧为长边）往返滑回。
        2. 根据可用滑动距离动态调整巡航时间：
           若空间充裕（> 半个屏幕，如 >= 0.55 * screen_w 且 >= 900px），执行 54 帧全速长程巡航；
           若空间有限（<= 半个屏幕），智能减少滑动时间，提前跳下滑板（在计算出的 dismount 帧直接切入第 69 帧，自然步入第 70 帧跃下展开）。
        """
        rect = self.get_screen_rect(use_available=True)
        margin = 25
        w = 200

        # 当前 200 宽窗口的左右侧屏幕安全距离
        cur_x = self.x() if self.width() == 200 else (self.x() - 50)
        cur_x = max(rect.left() + margin, min(rect.right() - margin - w, cur_x))
        dist_left = max(0, cur_x - (rect.left() + margin))
        dist_right = max(0, (rect.right() - margin - w) - cur_x)

        if is_first_round:
            # 选择长边滑动：如果右边可用空间大，向右滑；如果左边可用空间大，向左滑
            if dist_right >= dist_left:
                self.skateboard_slide_dir = 1
                self.is_skateboard_mirrored = False
                self.facing_direction = 1
                avail_dist = dist_right
            else:
                self.skateboard_slide_dir = -1
                self.is_skateboard_mirrored = True
                self.facing_direction = -1
                avail_dist = dist_left
        else:
            # 后续轮次（如第二轮往返）：反转方向
            self.skateboard_slide_dir = -getattr(self, 'skateboard_slide_dir', 1)
            self.is_skateboard_mirrored = (self.skateboard_slide_dir == -1)
            self.facing_direction = -1 if self.is_skateboard_mirrored else 1
            avail_dist = dist_right if self.skateboard_slide_dir == 1 else dist_left

        # 骑行距离估计为可以骑半个屏幕，不同屏幕尺寸动态计算 (25 FPS / 40ms 高帧率版)
        target_ride_dist = rect.width() * 0.5
        leap_dist = 35  # 飞离下板与减速刹车所需的位移 (frames 150..174 累计位移 35px)
        buffer_dist = 20
        target_cruise_dist = max(50.0, target_ride_dist - leap_dist)
        full_cruise_frames = 133  # frame 17 to frame 149 inclusive (上板后滑板立即前行，全程不停顿)

        # 动态计算巡航速度，使完整巡航刚好滑行半屏距离 (平缓舒适 4.0 ~ 14.0 px/帧)
        cruise_speed = max(4.0, min(14.0, target_cruise_dist / full_cruise_frames))
        self.skateboard_cruise_speed = cruise_speed
        self.skateboard_exact_x = float(self.x())

        usable_dist = max(0.0, avail_dist - leap_dist - buffer_dist)
        if usable_dist >= target_cruise_dist:
            # 空间充足（>= 半个屏幕）：完整滑行半屏距离
            self.skateboard_dismount_frame = 149
        else:
            # 可用空间不足半个屏幕：按可用距离自适应减少滑动时间，提前跳下滑板！
            actual_cruise_dist = max(30.0, usable_dist)
            cruise_frames = max(16, min(125, int(actual_cruise_dist / self.skateboard_cruise_speed)))
            self.skateboard_dismount_frame = min(149, 17 + cruise_frames)

        current_round = getattr(self, 'skateboard_total_repeats', 2) - getattr(self, 'skateboard_remaining_repeats', 1) + 1
        total_rounds = getattr(self, 'skateboard_total_repeats', 2)
        dir_text = "向右" if self.skateboard_slide_dir == 1 else "向左"
        if self.skateboard_dismount_frame < 149:
            mode_text = f"半屏短道版 (第{self.skateboard_dismount_frame}帧提前跳下)"
        else:
            mode_text = f"25FPS丝滑半屏巡航版 (预计滑行: {int(target_ride_dist)}px, 速度: {self.skateboard_cruise_speed:.1f}px/帧)"
        self.last_feedback = f"🛹 极限滑板第 {current_round}/{total_rounds} 轮！{dir_text}滑向长边 ({mode_text})"

    def trigger_skateboard(self, reason: str = "极限滑板炫技", repeats: int = 2):
        """触发极限滑板炫技，默认播放 2 遍往返（智能长边滑动与短道提前跳下）"""
        self.skateboard_remaining_repeats = max(1, repeats)
        self.skateboard_total_repeats = self.skateboard_remaining_repeats
        self.prepare_skateboard_round(is_first_round=True)
        self.switch_behavior(BEHAVIOR_CATALOG[BehaviorType.SKATEBOARD], None, f"{reason} (往返 {repeats} 趟)")

    def closeEvent(self, event):
        """主窗口关闭时清理所有活跃的大便实体"""
        for poop in list(self.active_poops):
            try:
                poop.close()
            except Exception:
                pass
        self.active_poops.clear()
        super().closeEvent(event)

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
                    elif self.current_behavior.code == BehaviorType.POOP:
                        self.switch_behavior(BEHAVIOR_CATALOG[BehaviorType.IDLE_BLINK], 3.0, "呼~ 轻松舒爽！")
                        if self.hud_window:
                            self.hud_window.update_view()
                        return
                    elif self.current_behavior.code == BehaviorType.EAT_PLANT:
                        self.switch_behavior(BEHAVIOR_CATALOG[BehaviorType.IDLE_WADDLE], 20.0, "植物啃完树枝咬断，步履轻快溜达20秒离开~")
                        if self.hud_window:
                            self.hud_window.update_view()
                        return
                    elif self.current_behavior.code == BehaviorType.MAGIC_TRICK:
                        if getattr(self, 'magic_remaining_repeats', 1) > 1:
                            self.magic_remaining_repeats -= 1
                            self.current_frame_index = 0
                            self.action_end_time = time.time() + 60.0
                            current_round = getattr(self, 'magic_total_repeats', 1) - self.magic_remaining_repeats + 1
                            self.last_feedback = f"🎩 魔术连续瞬移！第 {current_round}/{getattr(self, 'magic_total_repeats', 1)} 场表演..."

                            # 连续魔术镜像交替：鸟在上一场表演结束时的朝向直接作为下一场的初始朝向，无缝衔接绝不转身！
                            if getattr(self, 'is_magic_mirrored', False):
                                # 上一场是镜像模式：鸟在 frame 101 位于 bx=5，面向左
                                # 下一场切换为标准模式：鸟在 frame 0 位于 bx=155，面向左
                                # 为使鸟的全局屏幕坐标完全保持一致：(x + 5) == (new_x + 155) => new_x = x - 150
                                new_x = self.x() - 150
                                self.is_magic_mirrored = False
                                self.facing_direction = -1
                            else:
                                # 上一场是标准模式：鸟在 frame 101 位于 bx=155，面向右
                                # 下一场切换为镜像模式：鸟在 frame 0 位于 bx=5，面向右
                                # 为使鸟的全局屏幕坐标完全保持一致：(x + 155) == (new_x + 5) => new_x = x + 150
                                new_x = self.x() + 150
                                self.is_magic_mirrored = True
                                self.facing_direction = 1

                            self.safe_move(new_x, self.y(), margin=10)
                            self.update()
                            if self.hud_window:
                                self.hud_window.update_view()
                            return
                        else:
                            self.magic_remaining_repeats = 0
                            self.switch_behavior(BEHAVIOR_CATALOG[BehaviorType.IDLE_WADDLE], 10.0, "魔术大功告成！瞬间移动至全新坐标，开始漫步10秒~")
                            if self.hud_window:
                                self.hud_window.update_view()
                            return
                    elif self.current_behavior.code == BehaviorType.SKATEBOARD:
                        if getattr(self, 'skateboard_remaining_repeats', 1) > 1:
                            self.skateboard_remaining_repeats -= 1
                            self.current_frame_index = 0
                            self.action_end_time = time.time() + 60.0
                            # 初始化下一轮：反转方向，计算对侧可用距离，若只有半屏则减少滑动时间提前跳下
                            self.prepare_skateboard_round(is_first_round=False)
                            self.update()
                            if self.hud_window:
                                self.hud_window.update_view()
                            return
                        else:
                            self.skateboard_remaining_repeats = 0
                            self.switch_behavior(BEHAVIOR_CATALOG[BehaviorType.IDLE_BLINK], 4.0, "滑板炫技圆满谢幕！炫酷落地发呆~")
                            if self.hud_window:
                                self.hud_window.update_view()
                            return
            else:
                self.current_frame_index = (self.current_frame_index + 1) % len(frames)
                if intervals and self.current_frame_index < len(intervals):
                    self.anim_timer.setInterval(intervals[self.current_frame_index])

            # 变魔术：在第 51 帧幕布完全收起且全透明的瞬间，瞬间移动到桌面随机全新坐标
            if self.current_behavior.code == BehaviorType.MAGIC_TRICK and self.current_frame_index == 51:
                self.teleport_magic_window()

            # 后退深蹲排便：在第 9 帧泄殖腔释放瞬间，生成大便实体悬浮窗
            if self.current_behavior.code == BehaviorType.POOP and self.current_frame_index == 9:
                self.spawn_poop_at_tail()
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
            # 极限滑板：真实桌面高帧率丝滑滑动位移与智能提前跳下处理 (25 FPS / 40ms)
            elif self.current_behavior.code == BehaviorType.SKATEBOARD:
                f = self.current_frame_index
                slide_dir = getattr(self, 'skateboard_slide_dir', 1)
                cruise_speed = getattr(self, 'skateboard_cruise_speed', 7.0)
                dismount_frame = getattr(self, 'skateboard_dismount_frame', 149)

                # 1. 物理位移计算 (第17帧玄风踩上滑板后立即向前平滑位移，使用浮点亚像素累加器消除微停顿)
                dx_step = 0.0
                if 17 <= f <= dismount_frame:
                    dx_step = slide_dir * cruise_speed
                elif 150 <= f <= 174:
                    leap_speeds = {
                        150: 3, 151: 3, 152: 3, 153: 3, 154: 2, 155: 2, 156: 2, 157: 2,
                        158: 2, 159: 2, 160: 2, 161: 1, 162: 1, 163: 1, 164: 1, 165: 1,
                        166: 1, 167: 1, 168: 1, 169: 1, 170: 0, 171: 0, 172: 0, 173: 0, 174: 0
                    }
                    dx_step = slide_dir * leap_speeds.get(f, 0)

                if dx_step != 0.0:
                    if not hasattr(self, 'skateboard_exact_x') or self.skateboard_exact_x is None:
                        self.skateboard_exact_x = float(self.x())
                    self.skateboard_exact_x += dx_step
                    target_x = int(round(self.skateboard_exact_x))
                    if target_x != self.x():
                        self.safe_move(target_x, self.y(), margin=10)
                        if self.x() != target_x:
                            self.skateboard_exact_x = float(self.x())

                # 2. 提前跳下判定：若在滑行区间 (17..149) 达到提前跳下帧或临近屏幕边缘，直接跳下（切至第 149 帧，下一帧自然步入第 150 帧跃下展开）
                if 17 <= f < 150:
                    reached_dismount = (f >= dismount_frame)
                    rect = self.get_screen_rect(use_available=True)
                    edge_close = False
                    if slide_dir == 1:
                        edge_close = (self.x() + self.width() >= rect.right() - 35)
                    else:
                        edge_close = (self.x() <= rect.left() + 35)

                    if reached_dismount or edge_close:
                        self.current_frame_index = 149
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

        # 2.3 鼠标悬停头部静止检测 (停留超过2秒且心态平和舒适 -> 主动低头求撸)
        if self.update_head_hover(now=now):
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
        # 杂技踩球、后退深蹲排便、趣味啃咬植物、变魔术与极限滑板包含完整剧本序列，由 on_anim_frame_step 自然播放完毕后收尾切出，跳过主循环强制超时
        if self.current_behavior.code in (BehaviorType.EXCITE_PLAY_BALL, BehaviorType.POOP, BehaviorType.EAT_PLANT, BehaviorType.MAGIC_TRICK, BehaviorType.SKATEBOARD):
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

            # 1. 显式预设动作 (如有外部调用设置) 优先消费
            if self.pending_next_behavior:
                next_code = self.pending_next_behavior
                self.pending_next_behavior = None
                self.switch_behavior(BEHAVIOR_CATALOG[next_code], None, f"执行预设动作: {BEHAVIOR_CATALOG[next_code].name_cn}")
                if self.hud_window:
                    self.hud_window.update_view()
                return

            # 2. 摸头后衔接动作：概率性触发转头理毛 (COMFORT_PREEN)
            # 规则：点一下 20%，点两下 30%，点三下 40%... 该概率只影响摸头后的这一个动作
            if getattr(self, 'head_pet_active', False):
                self.head_pet_active = False
                prob = self.get_head_pet_preen_prob()
                if random.random() < prob:
                    # 概率命中理毛：理毛后清空摸头累计次数
                    self.head_pet_count = 0
                    self.switch_behavior(BEHAVIOR_CATALOG[BehaviorType.COMFORT_PREEN], None,
                                         "摸头享受完毕，开始整理凌乱羽毛~")
                    if self.hud_window:
                        self.hud_window.update_view()
                    return
                else:
                    # 未命中理毛：该概率只影响摸头后的这一个动作，后续动作恢复正常发呆
                    self.switch_behavior(BEHAVIOR_CATALOG[BehaviorType.IDLE_BLINK], 3.0,
                                         "摸头享受完毕，惬意站立发呆~")
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
            # 特殊情况: 如果抽取到飞行或大舞台特技
            if next_b_def.code == BehaviorType.FRIGHT_PANIC_FLY:
                self.start_flight(panic=True)
            elif next_b_def.code == BehaviorType.COMFORT_APPROACH:
                self.start_flight(panic=False)
            elif next_b_def.code == BehaviorType.IDLE_FLY:
                self.start_flight(panic=False, roam=True)
            elif next_b_def.code == BehaviorType.MAGIC_TRICK:
                self.trigger_magic_trick("自发变魔术！")
            elif next_b_def.code == BehaviorType.SKATEBOARD:
                self.trigger_skateboard("自发极限滑板炫技！")
            elif next_b_def.code == BehaviorType.EAT_PLANT:
                self.trigger_eat_plant("自发趣味啃咬植物！")
            else:
                self.switch_behavior(next_b_def, duration, f"自发切换到: {next_b_def.name_cn}")

        # 6. 同步更新雷达监视器
        if self.hud_window:
            self.hud_window.update_view()

    # --- 空间交互与局部感应 ---
    def is_head_neck_zone(self, local_pos: QPoint) -> bool:
        """判定点击/悬停位置是否在头颈部安全区 (黄脸/冠羽/嘴壳/下巴/咽喉/后颈)

        支持全角度头部抚摸互动，包含下巴与嘴下喉部，同时严格保留背部/翅膀/腹部/尾巴的躯干禁区。
        自动根据当前朝向进行左右镜像归一化，并动态适配低头(COMFORT_BOW)与啄地动作的头部位置偏移。
        """
        w = self.width()
        h = self.height()
        if local_pos.x() < 0 or local_pos.x() >= w or local_pos.y() < 0 or local_pos.y() >= h:
            return False

        # 针对大画布特技动作 (如玩球 260x120) 进行比例容错适配
        if w > 120 or h > 100:
            if local_pos.y() > h * 0.65:
                return False
            if self.facing_direction == -1:
                return local_pos.x() < w * 0.55
            else:
                return local_pos.x() > w * 0.45

        # 归一化为基准左朝向坐标 (面向左时 rx=x，面向右时镜像翻转 rx=w-1-x)
        rx = local_pos.x() if self.facing_direction == -1 else (w - 1 - local_pos.x())
        ry = local_pos.y()

        behavior_code = self.current_behavior.code if self.current_behavior else None

        # 1. 低头闭眼享受姿态 (COMFORT_BOW): 头部深低前探，头部、下巴与喉部判定区顺延向下
        if behavior_code == BehaviorType.COMFORT_BOW:
            if ry <= 36:
                return rx <= 54
            elif ry <= 58:
                return rx <= 48
            return False

        # 2. 啄地姿态 (IDLE_PECK / EXCITE_DOUBLE_PECK): 头部低头啄食
        if behavior_code in (BehaviorType.IDLE_PECK, BehaviorType.EXCITE_DOUBLE_PECK):
            if ry <= 65 and rx <= 45:
                return True
            if ry <= 42 and rx <= 55:
                return True
            return False

        # 3. 常规站立/行走/鸣叫/打哈欠等常态姿势 (标准 100x80 画布):
        # 3.1 头部上部 (冠羽、额头、眼睛、嘴壳上部、脸颊上侧、脑后上颈): y <= 42, rx <= 55
        if ry <= 42:
            return rx <= 55

        # 3.2 头部下部安全区 (嘴壳下部、下巴、咽喉前侧、下脸颊): y 在 43..53 之间
        # 下巴及喉部羽毛位于前方 (rx <= 45)，完全包含下巴下缘及喉咙部位
        if ry <= 53:
            if rx <= 45:
                return True
            # 后脑下缘与后颈连接处 (rx 在 46..52，且 y <= 47)
            if rx <= 52 and ry <= 47:
                return True
            return False

        # 其余区域 (背部、翅膀、腹部、尾巴、脚爪) 判定为躯干禁区
        return False

    def update_head_hover(self, local_pos: Optional[QPoint] = None, now: Optional[float] = None) -> bool:
        """检查鼠标悬停在头颈部的时间，停留超过 2 秒且心态平和舒适时才触发主动低头求撸"""
        if now is None:
            now = time.time()

        # 拖拽中、飞行中、睡眠中、排便中、玩球中、啃植物中、变魔术中、玩滑板中不触发悬停求撸
        if self.is_dragging or self.is_flying or self.current_behavior.code in (
            BehaviorType.REST_SLEEP, BehaviorType.REST_FALL_ASLEEP, BehaviorType.POOP, BehaviorType.EXCITE_PLAY_BALL, BehaviorType.EAT_PLANT, BehaviorType.MAGIC_TRICK, BehaviorType.SKATEBOARD
        ):
            self.hover_head_start_time = None
            return False

        if local_pos is None:
            local_pos = self.mapFromGlobal(QCursor.pos())

        if self.is_head_neck_zone(local_pos):
            if self.hover_head_start_time is None:
                self.hover_head_start_time = now
            else:
                hover_dur = now - self.hover_head_start_time
                # 鼠标靠近停留超过 2.0 秒，且心态平和舒适 (fright < 25.0) -> 主动低头求撸
                if hover_dur >= 2.0 and self.mood.fright < 25.0:
                    self.mood.hover_head_tick(0.05)
                    triggered = False
                    if self.current_behavior.code not in [BehaviorType.COMFORT_BOW, BehaviorType.COMFORT_FLUFF]:
                        self.switch_behavior(BEHAVIOR_CATALOG[BehaviorType.COMFORT_BOW], None,
                                             "察觉到手停在头顶超过2秒，主动低头求撸")
                        triggered = True
                    # 触发后重置悬停计时，避免同一停留持续重复触发
                    self.hover_head_start_time = None
                    return triggered
        else:
            self.hover_head_start_time = None

        return False

    def leaveEvent(self, event):
        """鼠标离开桌宠窗口时彻底重置头部悬停计时，防止移出后再移入时发生超时误触发"""
        self.hover_head_start_time = None
        super().leaveEvent(event)

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

        # 悬停在头颈部检测 (停留超过2秒才触发主动低头求撸)
        self.update_head_hover(local_pos=pos, now=now)

    def mousePressEvent(self, event):
        if self.is_flying or getattr(self, "is_exiting", False):
            return
        if event.button() == Qt.LeftButton:
            pos = event.position().toPoint()
            # Any click on the pet window is enough to wake a sleeping bird,
            # including a click on its transparent padding.
            if self.current_behavior.code in (BehaviorType.REST_SLEEP, BehaviorType.REST_FALL_ASLEEP):
                self.wake_up("被鼠标点击吵醒了")
                return

            # 玩球、啃咬植物、变魔术、极限滑板等大舞台动作播放期间，禁止鼠标拖拽与触摸打断
            if self.current_behavior.code in (BehaviorType.EXCITE_PLAY_BALL, BehaviorType.EAT_PLANT, BehaviorType.MAGIC_TRICK, BehaviorType.SKATEBOARD):
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
            self.hover_head_start_time = None

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
            self.hover_head_start_time = None
            self.ensure_on_screen(margin=10)
            # 如果处于敲屏状态但被拖拽移离了屏幕边缘，立即切出敲屏
            if self.current_behavior.code == BehaviorType.EXCITE_BONK and not self.is_at_screen_edge(margin=50):
                self.switch_behavior(BEHAVIOR_CATALOG[BehaviorType.IDLE_BLINK], 3.0, "被移离屏幕边缘，停止敲屏发呆~")

    def mouseDoubleClickEvent(self, event):
        self.mousePressEvent(event)

    def get_head_pet_preen_prob(self) -> float:
        """计算摸头后下个动作触发理毛的概率：点1下20%，点2下30%，点3下40%... 以此类推 (上限100%)"""
        if self.head_pet_count <= 0:
            return 0.0
        return min(1.0, 0.20 + (self.head_pet_count - 1) * 0.10)

    def handle_pet_head(self):
        """摸头交互：切入低头享受动作，结束后概率性衔接转头理毛 (点1下20%, 点2下30%, 点3下40%...)
        该概率只影响摸头后的下一个动作。
        """
        if self.current_behavior.code in (BehaviorType.REST_SLEEP, BehaviorType.REST_FALL_ASLEEP):
            self.wake_up("被轻轻摸醒了")

        now = time.time()
        # 如果先前正在理毛，或者距上次摸头超过 15 秒且非当前低头动作，重置累计次数
        if self.current_behavior.code == BehaviorType.COMFORT_PREEN or (
            self.current_behavior.code != BehaviorType.COMFORT_BOW and (now - self.last_head_pet_time > 15.0)
        ):
            self.head_pet_count = 0

        self.head_pet_count += 1
        self.head_pet_active = True
        self.last_head_pet_time = now
        self.pending_next_behavior = None  # 不再硬编码必触发理毛

        d_co, _, msg = self.mood.pet_head()
        feedback_msg = msg

        # 摸头动作切入低头闭眼享受 (COMFORT_BOW)，持续 4.0 秒
        self.switch_behavior(BEHAVIOR_CATALOG[BehaviorType.COMFORT_BOW], 4.0, feedback_msg)

    def handle_touch_body(self):
        """戳身体禁区"""
        self.pending_next_behavior = None
        self.head_pet_active = False
        self.head_pet_count = 0
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
        self.head_pet_active = False
        self.head_pet_count = 0
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

    def start_fly_in(self, target_pos: Optional[QPointF] = None, entry_side: Optional[str] = None):
        """
        开机启动入场动画：玄凤从屏幕外飞入桌面，随机寻找落脚点降落
        """
        if self.is_flying:
            return

        self.pending_next_behavior = None
        self.head_pet_active = False
        self.head_pet_count = 0

        rect = self.get_screen_rect(use_available=True)
        w, h = self.width(), self.height()

        # 1. 随机决定落脚点 (桌面舒适可视区域，靠中下部)
        if target_pos is not None:
            tx = float(target_pos.x())
            ty = float(target_pos.y())
        else:
            tx = float(random.randint(rect.left() + 60, max(rect.left() + 60, rect.right() - w - 60)))
            y_min = max(rect.top() + 60, rect.bottom() - 260)
            y_max = max(y_min, rect.bottom() - h - 25)
            ty = float(random.randint(y_min, y_max))

        self.fly_target_pos = QPointF(tx, ty)

        # 2. 随机决定屏幕外出发点 (从天际上方、左上或右上等屏幕外区域滑翔入场)
        side = entry_side if entry_side else random.choice(["top_sky", "top_left", "top_right", "left", "right"])
        if side == "top_sky":
            sx = tx + random.choice([-1, 1]) * random.randint(120, 260)
            sy = float(rect.top() - h - random.randint(40, 90))
        elif side == "top_left":
            sx = float(rect.left() - w - random.randint(30, 80))
            sy = float(rect.top() - h - random.randint(20, 50))
        elif side == "top_right":
            sx = float(rect.right() + random.randint(30, 80))
            sy = float(rect.top() - h - random.randint(20, 50))
        elif side == "left":
            sx = float(rect.left() - w - random.randint(30, 70))
            sy = float(random.randint(rect.top() + 40, max(rect.top() + 40, int(ty) - 60)))
        else: # "right"
            sx = float(rect.right() + random.randint(30, 70))
            sy = float(random.randint(rect.top() + 40, max(rect.top() + 40, int(ty) - 60)))

        self.fly_start_pos = QPointF(sx, sy)
        self.move(int(sx), int(sy))

        # 3. 飞行朝向面向目标落脚点
        dx = tx - sx
        self.facing_direction = 1 if dx > 0 else -1
        self.waddle_direction = self.facing_direction
        self.update()

        # 4. 二阶贝塞尔曲线控制点 (自然俯冲并优雅拉起降落)
        mid_x = (sx + tx) / 2.0
        mid_y = min(sy, ty) - random.randint(30, 80)
        self.fly_control_pos = QPointF(mid_x, mid_y)

        # 5. 启动入场飞行
        self.is_flying = True
        self.flight_purpose = "fly_in"
        dist = math.hypot(tx - sx, ty - sy)
        self.fly_duration = max(1.4, min(2.0, dist / 340.0))
        self.fly_progress = 0.0

        self.switch_behavior(BEHAVIOR_CATALOG[BehaviorType.IDLE_FLY], self.fly_duration + 0.5, "从屏幕外挥翅飞入，寻找落脚点~")
        self.fly_timer.start(25) # 40 FPS

    def start_fly_out_and_quit(self, exit_dir: Optional[int] = None):
        """
        关闭退出离场动画：点击告别退出时，玄凤直接向上掠起飞出屏幕外，然后退出程序
        """
        if getattr(self, "is_exiting", False):
            return
        self.is_exiting = True

        # 若在睡眠中则立刻唤醒
        if self.current_behavior.code in (BehaviorType.REST_SLEEP, BehaviorType.REST_FALL_ASLEEP):
            self.wake_up("跟主人告别，准备飞走~")

        # 隐藏 HUD 窗口与浮窗
        if self.hud_window:
            self.hud_window.hide()

        # 清除摸头/交互状态
        self.head_pet_active = False
        self.head_pet_count = 0
        self.is_dragging = False

        rect = self.get_screen_rect(use_available=True)
        w, h = self.width(), self.height()
        cur_x = float(self.x())
        cur_y = float(self.y())

        # 起点为当前位置
        self.fly_start_pos = QPointF(cur_x, cur_y)

        # 终点为屏幕外上方（向上方天空飞离屏幕）
        mid_screen_x = (rect.left() + rect.right()) / 2.0
        if exit_dir is not None:
            fly_dir = exit_dir
        else:
            fly_dir = 1 if cur_x < mid_screen_x else -1

        out_x = cur_x + fly_dir * random.randint(180, 360)
        out_y = float(rect.top() - h - random.randint(40, 80))
        self.fly_target_pos = QPointF(out_x, out_y)

        # 朝向飞行方向
        dx = out_x - cur_x
        self.facing_direction = 1 if dx > 0 else -1
        self.waddle_direction = self.facing_direction
        self.update()

        # 贝塞尔控制点：向上弧度掠起起飞
        c_x = (cur_x + out_x) / 2.0
        c_y = min(cur_y, out_y) - random.randint(40, 80)
        self.fly_control_pos = QPointF(c_x, c_y)

        self.is_flying = True
        self.flight_purpose = "fly_out"
        self.fly_duration = 1.3
        self.fly_progress = 0.0

        self.switch_behavior(BEHAVIOR_CATALOG[BehaviorType.IDLE_FLY], 3.0, "告别主人，挥翅飞向远方~")
        self.fly_timer.start(25)

    def on_fly_step(self):
        step = 0.025 / self.fly_duration
        self.fly_progress += step
        if self.fly_progress >= 1.0:
            self.fly_progress = 1.0
            self.fly_timer.stop()
            self.is_flying = False

            if self.flight_purpose == "fly_out":
                # 告别飞出屏幕完全离开，立即安全退出程序
                self.hide()
                if hasattr(self, "_on_fly_out_finished"):
                    self._on_fly_out_finished()
                else:
                    QApplication.quit()
                return

            if self.flight_purpose == "fly_in":
                # 飞入屏幕安全降落
                self.safe_move(int(self.fly_target_pos.x()), int(self.fly_target_pos.y()), margin=10)
                landing_action = random.choice([BehaviorType.COMFORT_BOW, BehaviorType.COMFORT_FLUFF, BehaviorType.IDLE_BLINK])
                self.switch_behavior(BEHAVIOR_CATALOG[landing_action], 2.0, "顺利飞到桌面，开心降落找你玩~")
                if self.hud_window:
                    self.hud_window.update_view()
                return

            self.safe_move(int(self.fly_target_pos.x()), int(self.fly_target_pos.y()), margin=10)
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

        if self.flight_purpose in ("fly_in", "fly_out"):
            # 屏幕内外飞入/飞出：允许越过屏幕边缘进行真·屏幕外出入
            self.move(int(bx), int(by))
        else:
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

        # 4. 禁止随地大小便 (保存至配置)
        act_disable_poop = menu.addAction("🚯 禁止随地大小便")
        act_disable_poop.setCheckable(True)
        act_disable_poop.setChecked(self.is_poop_disabled)

        menu.addSeparator()

        # 5. 清空疲劳与 6. 强制睡眠 (发布版与开发版均保留的核心控制)
        act_clear_fatigue = menu.addAction("⚡ 清空疲劳 (瞬间回满)")
        act_sleep = menu.addAction("💤 强制睡眠 (疲劳拉满)")

        # 仅开发调试模式显示的注入选项
        if dev_mode:
            menu.addSeparator()
            prob_pct = int(self.get_poop_probability() * 100)
            elapsed_min = int((time.time() - self.last_poop_time) / 60)
            act_sing = menu.addAction("🎵 逗它开心吹口哨")
            act_hop = menu.addAction("🦘 移动雀跃小跳 (开心蹦跶)")
            act_bonk = menu.addAction("🥁 敲击屏幕边缘 (自嗨敲屏)")
            act_double_peck = menu.addAction("⚡ 连环双击啄桌 (兴奋连啄)")
            act_play_ball = menu.addAction("🔴 兴奋杂技踩球 (30秒巡游)")
            act_eat_plant = menu.addAction("🌿 趣味啃咬植物 (自适应嚼叶啃树枝)")
            act_magic = menu.addAction("🎩 变魔术大巡游 (红幕跨屏瞬移)")
            act_skateboard = menu.addAction("🛹 极限滑板炫技 (两遍镜像往返)")
            act_poop = menu.addAction(f"💩 触发拉屎行为 (便意概率: {prob_pct}%, 已过{elapsed_min}分)")
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
            act_eat_plant = None
            act_magic = None
            act_skateboard = None
            act_poop = None
            act_peck = None
            act_waddle = None
            act_preen = None
            act_fluff = None
            act_yawn = None
            act_fly = None
            act_fright = None
            act_reset = None

        menu.addSeparator()
        # 5. 检查更新
        act_check_update = menu.addAction(f"🚀 检查更新 (当前 {APP_VERSION})...")
        # 6. 退出
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
        elif res == act_disable_poop:
            self.toggle_disable_poop()
            tip_msg = "🚯 已开启‘禁止随地大小便’" if self.is_poop_disabled else "💩 已允许自然排泄"
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
        elif act_eat_plant and res == act_eat_plant:
            if self.current_behavior.code in (BehaviorType.REST_SLEEP, BehaviorType.REST_FALL_ASLEEP):
                self.wake_up("被植物吸引醒来！")
            self.trigger_eat_plant("右键菜单触发：趣味啃咬植物！")
        elif act_magic and res == act_magic:
            if self.current_behavior.code in (BehaviorType.REST_SLEEP, BehaviorType.REST_FALL_ASLEEP):
                self.wake_up("被魔术表演唤醒！")
            self.trigger_magic_trick("右键菜单触发：红色幕布变魔术！")
        elif act_skateboard and res == act_skateboard:
            if self.current_behavior.code in (BehaviorType.REST_SLEEP, BehaviorType.REST_FALL_ASLEEP):
                self.wake_up("被滑板吸引醒来！")
            self.trigger_skateboard("右键菜单触发：极限滑板炫技！")
        elif act_poop and res == act_poop:
            self.trigger_poop("右键菜单触发：后退深蹲排便！")
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
        elif res == act_check_update:
            self.check_for_updates()
        elif res == act_quit:
            self.start_fly_out_and_quit()

    def paintEvent(self, event):
        painter = QPainter(self)
        pix = self.get_current_pixmap()
        if not pix.isNull():
            # 防撕裂与跨画布切换闪烁卫士：若窗口尺寸与贴图尺寸在过渡瞬态未对齐，跳过绘制避免贴图乱闪
            if pix.width() != self.width() or pix.height() != self.height():
                return
            painter.drawPixmap(0, 0, pix)
