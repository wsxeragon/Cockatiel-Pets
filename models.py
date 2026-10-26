import time
import random
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Tuple, Optional

class BehaviorType(str, Enum):
    # 平静日常
    IDLE_BLINK = "IDLE_BLINK"
    IDLE_WADDLE = "IDLE_WADDLE"
    IDLE_PECK = "IDLE_PECK"
    IDLE_FLY = "IDLE_FLY"
    # 闲置搞事 / 拆家
    MISCHIEF_CHEW = "MISCHIEF_CHEW"
    # 舒适享受
    COMFORT_FLUFF = "COMFORT_FLUFF"
    COMFORT_PREEN = "COMFORT_PREEN"
    COMFORT_BOW = "COMFORT_BOW"
    COMFORT_APPROACH = "COMFORT_APPROACH"
    COMFORT_YAWN = "COMFORT_YAWN"
    REST_FALL_ASLEEP = "REST_FALL_ASLEEP"
    REST_SLEEP = "REST_SLEEP"
    REST_WAKE = "REST_WAKE"
    REST_WAKE_CURIOUS = "REST_WAKE_CURIOUS"
    # 兴奋自嗨
    EXCITE_HOP = "EXCITE_HOP"
    EXCITE_BOB = "EXCITE_BOB"
    EXCITE_HEART_WINGS = "EXCITE_HEART_WINGS"
    EXCITE_SING = "EXCITE_SING"
    EXCITE_BONK = "EXCITE_BONK"
    EXCITE_DOUBLE_PECK = "EXCITE_DOUBLE_PECK"
    EXCITE_PLAY_BALL = "EXCITE_PLAY_BALL"
    POOP = "POOP"
    EAT_PLANT = "EAT_PLANT"
    MAGIC_TRICK = "MAGIC_TRICK"
    SKATEBOARD = "SKATEBOARD"
    # 应激防御
    FRIGHT_ALERT = "FRIGHT_ALERT"
    FRIGHT_BITE = "FRIGHT_BITE"
    FRIGHT_HISS = "FRIGHT_HISS"
    FRIGHT_PANIC_FLY = "FRIGHT_PANIC_FLY"

@dataclass
class BehaviorDef:
    code: BehaviorType
    name_cn: str
    base_weight: float
    w_fright: float
    w_comfort: float
    w_excite: float
    duration_mean: float  # seconds
    duration_std: float   # seconds
    frames: List[str]
    frame_interval_ms: int = 250
    frame_intervals_ms: Optional[List[int]] = None
    is_interruptible: bool = True
    is_looping: bool = True

BEHAVIOR_CATALOG: Dict[BehaviorType, BehaviorDef] = {
    # 日常
    BehaviorType.IDLE_BLINK: BehaviorDef(
        BehaviorType.IDLE_BLINK, "闭眼发呆", 30.0, -0.3, 0.1, -0.3, 300.0, 20.0,
        ["idle_0"], frame_interval_ms=1000
    ),
    BehaviorType.IDLE_WADDLE: BehaviorDef(
        BehaviorType.IDLE_WADDLE, "摇晃溜达(走来走去)", 55.0, -0.2, 0.2, 0.1, 300.0, 20.0,
        ["waddle_0", "waddle_1", "waddle_2", "waddle_3", "waddle_4",
         "waddle_5", "waddle_6", "waddle_7"], frame_interval_ms=120
    ),
    BehaviorType.IDLE_PECK: BehaviorDef(
        BehaviorType.IDLE_PECK, "闲置自然啄食", 15.0, -0.3, 0.0, 0.1, 30.0, 3.0,
        ["peck_0", "peck_1", "peck_2", "peck_3"], frame_interval_ms=180
    ),
    BehaviorType.IDLE_FLY: BehaviorDef(
        BehaviorType.IDLE_FLY, "日常短途飞行", 7.0, -0.4, 0.1, 0.0, 2.0, 0.4,
        ["fly_0", "fly_1", "fly_2", "fly_3"], frame_interval_ms=120,
        is_interruptible=False
    ),
    # 闲置搞事
    BehaviorType.MISCHIEF_CHEW: BehaviorDef(
        BehaviorType.MISCHIEF_CHEW, "啃咬屏幕(拆家)", 3.0, -0.5, -0.1, 0.9, 30.0, 3.0,
        ["chew_0", "chew_1", "chew_0", "chew_1"], frame_interval_ms=160
    ),
    # 舒适
    BehaviorType.COMFORT_FLUFF: BehaviorDef(
        BehaviorType.COMFORT_FLUFF, "蓬成毛球", 5.0, -0.5, 0.8, -0.2, 180.0, 15.0,
        ["fluff_0", "fluff_1"], frame_interval_ms=900
    ),
    BehaviorType.COMFORT_PREEN: BehaviorDef(
        BehaviorType.COMFORT_PREEN, "整理羽毛(埋背理毛)", 8.0, -0.4, 0.6, -0.1, 120.0, 12.0,
        ["preen_0", "preen_1", "preen_2", "preen_3"], frame_interval_ms=280
    ),
    BehaviorType.COMFORT_BOW: BehaviorDef(
        BehaviorType.COMFORT_BOW, "低头求撸毛", 2.0, -0.6, 1.2, 0.0, 10.0, 1.0,
        ["bow_0", "bow_1", "bow_0"]
    ),
    BehaviorType.COMFORT_APPROACH: BehaviorDef(
        BehaviorType.COMFORT_APPROACH, "飞向光标求陪伴", 1.0, -1.0, 1.1, 0.2, 3.0, 0.5,
        ["fly_0", "fly_1", "fly_2", "fly_3"], frame_interval_ms=120, is_interruptible=False
    ),
    BehaviorType.COMFORT_YAWN: BehaviorDef(
        BehaviorType.COMFORT_YAWN, "伸脖打哈欠", 0.0, 0.0, 0.0, 0.0, 2.35, 0.0,
        ["yawn_0", "yawn_1", "yawn_2", "yawn_3", "yawn_4", "yawn_5", "yawn_6", "yawn_7"],
        frame_interval_ms=280,
        frame_intervals_ms=[280, 220, 260, 450, 340, 240, 260, 300],
        is_interruptible=True,
        is_looping=False
    ),
    BehaviorType.REST_FALL_ASLEEP: BehaviorDef(
        BehaviorType.REST_FALL_ASLEEP, "困倦入睡", 0.0, 0.0, 0.0, 0.0, 1.35, 0.0,
        ["fall_asleep_0", "fall_asleep_1", "fall_asleep_2", "fall_asleep_3"],
        frame_interval_ms=320,
        frame_intervals_ms=[350, 320, 320, 360],
        is_looping=False
    ),
    BehaviorType.REST_SLEEP: BehaviorDef(
        BehaviorType.REST_SLEEP, "安静睡觉", 0.0, 0.0, 0.0, 0.0, 30.0, 0.0,
        ["sleep_0", "sleep_1", "sleep_0", "sleep_1"], frame_interval_ms=850
    ),
    BehaviorType.REST_WAKE: BehaviorDef(
        BehaviorType.REST_WAKE, "醒来机敏转头", 0.0, 0.0, 0.0, 0.0, 2.2, 0.0,
        ["wake_0", "wake_1", "wake_2", "wake_3", "wake_4", "wake_5"],
        frame_interval_ms=300,
        frame_intervals_ms=[350, 300, 450, 350, 280, 450],
        is_looping=False
    ),
    BehaviorType.REST_WAKE_CURIOUS: BehaviorDef(
        BehaviorType.REST_WAKE_CURIOUS, "醒来细致探头", 0.0, 0.0, 0.0, 0.0, 2.4, 0.0,
        ["wake_0", "wake_1", "wake_c_2", "wake_c_3", "wake_3", "wake_4", "wake_5"],
        frame_interval_ms=300,
        frame_intervals_ms=[350, 260, 280, 380, 320, 260, 450],
        is_looping=False
    ),
    # 兴奋
    BehaviorType.EXCITE_HOP: BehaviorDef(
        BehaviorType.EXCITE_HOP, "移动雀跃小跳", 8.0, -0.2, 0.1, 0.8, 30.0, 3.0,
        ["hop_0", "hop_1", "hop_2", "hop_3"], frame_interval_ms=130
    ),
    BehaviorType.EXCITE_BOB: BehaviorDef(
        BehaviorType.EXCITE_BOB, "点头打节拍狂魔", 10.0, -0.3, 0.2, 0.9, 60.0, 8.0,
        ["bob_0", "bob_1", "bob_0", "bob_1"], frame_interval_ms=160
    ),
    BehaviorType.EXCITE_HEART_WINGS: BehaviorDef(
        BehaviorType.EXCITE_HEART_WINGS, "心形翅膀(已隐藏)", 0.0, 0.0, 0.0, 0.0, 30.0, 3.0,
        ["heart_wings_0", "heart_wings_1", "heart_wings_0"], frame_interval_ms=240
    ),
    BehaviorType.EXCITE_SING: BehaviorDef(
        BehaviorType.EXCITE_SING, "吹口哨唱歌独奏", 1.0, -0.6, 0.2, 1.4, 180.0, 15.0,
        ["sing_0", "sing_1", "sing_2", "sing_1"], frame_interval_ms=200
    ),
    BehaviorType.EXCITE_BONK: BehaviorDef(
        BehaviorType.EXCITE_BONK, "嘴壳敲屏(自嗨敲打)", 2.5, -0.4, 0.3, 1.2, 60.0, 5.0,
        ["bonk_0", "bonk_1", "bonk_2", "bonk_3", "bonk_4", "bonk_0"], frame_interval_ms=160
    ),
    BehaviorType.EXCITE_DOUBLE_PECK: BehaviorDef(
        BehaviorType.EXCITE_DOUBLE_PECK, "连环双击啄桌面", 3.0, -0.4, 0.2, 1.2, 60.0, 5.0,
        ["double_peck_0", "double_peck_1", "double_peck_2", "double_peck_1", "double_peck_2", "double_peck_3"], frame_interval_ms=140
    ),
    BehaviorType.EXCITE_PLAY_BALL: BehaviorDef(
        BehaviorType.EXCITE_PLAY_BALL, "兴奋杂技踩球", 5.0, -0.4, 0.2, 1.3, 30.0, 0.0,
        [f"play_ball_{i}" for i in range(300)], frame_interval_ms=100,
        is_interruptible=True, is_looping=False
    ),
    BehaviorType.POOP: BehaviorDef(
        BehaviorType.POOP, "后退深蹲排便", 0.0, 0.0, 0.0, 0.0, 5.0, 0.0,
        [f"poop_{i}" for i in range(14)],
        frame_interval_ms=250,
        frame_intervals_ms=[300, 220, 220, 220, 260, 240, 450, 600, 600, 350, 240, 180, 180, 500],
        is_interruptible=False,
        is_looping=False
    ),
    BehaviorType.EAT_PLANT: BehaviorDef(
        BehaviorType.EAT_PLANT, "趣味啃咬植物", 3.0, -0.4, 0.3, 1.0, 22.0, 0.0,
        [f"eat_plant_{i}" for i in range(138)],
        frame_interval_ms=120,
        frame_intervals_ms=[105, 105, 105, 105, 105, 105, 105, 105, 105, 105, 105, 105, 105, 105, 105, 105, 105, 105, 105, 105, 105, 105, 105, 105, 105, 105, 105, 105, 105, 105, 105, 105, 105, 105, 105, 105, 140, 140, 140, 140, 140, 140, 140, 140, 140, 140, 140, 140, 150, 110, 140, 140, 140, 140, 140, 140, 140, 140, 140, 140, 150, 110, 110, 110, 110, 140, 140, 140, 140, 140, 140, 140, 140, 140, 140, 160, 130, 130, 130, 120, 120, 140, 140, 140, 130, 130, 140, 120, 140, 120, 140, 120, 140, 120, 150, 120, 120, 120, 120, 120, 120, 140, 140, 130, 130, 120, 105, 105, 105, 105, 105, 105, 105, 105, 105, 105, 105, 105, 105, 105, 105, 105, 105, 105, 105, 105, 105, 105, 105, 105, 105, 105, 105, 105, 105, 105, 105, 105],
        is_interruptible=True,
        is_looping=False
    ),
    BehaviorType.MAGIC_TRICK: BehaviorDef(
        BehaviorType.MAGIC_TRICK, "红幕变魔术(瞬移)", 2.5, -0.4, 0.2, 1.2, 11.0, 0.0,
        [f"magic_trick_{i}" for i in range(110)],
        frame_interval_ms=100,
        is_interruptible=False,
        is_looping=False
    ),
    BehaviorType.SKATEBOARD: BehaviorDef(
        BehaviorType.SKATEBOARD, "极限滑板炫技", 2.0, -0.4, 0.2, 1.2, 8.0, 0.0,
        [f"skateboard_{i}" for i in range(200)],
        frame_interval_ms=40,
        is_interruptible=False,
        is_looping=False
    ),
    # 应激
    BehaviorType.FRIGHT_ALERT: BehaviorDef(
        BehaviorType.FRIGHT_ALERT, "警惕拉长身体", 2.0, 0.8, -0.4, 0.0, 2.5, 0.8,
        ["alert_0"]
    ),
    BehaviorType.FRIGHT_BITE: BehaviorDef(
        BehaviorType.FRIGHT_BITE, "咬鼠标反击", 0.0, 1.0, -0.5, 0.0, 1.0, 0.2,
        ["bite_0", "bite_1", "bite_2", "bite_3"], frame_interval_ms=180, is_interruptible=False, is_looping=False
    ),
    BehaviorType.FRIGHT_HISS: BehaviorDef(
        BehaviorType.FRIGHT_HISS, "炸毛哈气威慑", 1.0, 1.0, -0.5, 0.0, 2.0, 0.5,
        ["hiss_0", "hiss_1"], frame_interval_ms=200
    ),
    BehaviorType.FRIGHT_PANIC_FLY: BehaviorDef(
        BehaviorType.FRIGHT_PANIC_FLY, "惊吓扇翅逃跑", 0.5, 1.5, -0.8, 0.0, 3.0, 0.5,
        ["fly_0", "fly_1", "fly_2", "fly_3"], frame_interval_ms=95, is_interruptible=False
    ),
}

# 兴奋类行为集 (仅在兴奋时才触发的行为；结束后自动清空兴奋值)
EXCITED_BEHAVIORS = {
    BehaviorType.EXCITE_HOP,
    BehaviorType.EXCITE_BOB,
    BehaviorType.EXCITE_HEART_WINGS,
    BehaviorType.EXCITE_SING,
    BehaviorType.EXCITE_BONK,
    BehaviorType.EXCITE_DOUBLE_PECK,
    BehaviorType.EXCITE_PLAY_BALL,
    BehaviorType.EAT_PLANT,
    BehaviorType.MAGIC_TRICK,
    BehaviorType.SKATEBOARD,
    BehaviorType.MISCHIEF_CHEW,
}

class MoodDynamics:
    """四维心态动力学引擎"""
    def __init__(self):
        self.fright: float = 0.0       # 惊吓 [0, 100]
        self.comfort: float = 25.0     # 舒适 [0, 100]
        self.excitement: float = 10.0  # 兴奋 [0, 100]
        self.calm: float = 65.0        # 平静 [0, 100] (基准平衡态)
        self.fatigue: float = 0.0      # 身体疲劳 [0, 100]，独立于四维心态
        self.sleep_cooldown_until: float = 0.0
        self.last_head_pet_time: float = float("-inf")

        self.last_interaction_time: float = time.time()
        self.body_click_timestamps: List[float] = []

    @property
    def is_excited(self) -> bool:
        """是否处于高兴奋状态 (>=40%)"""
        return self.excitement >= 40.0

    def clear_excitement(self):
        """兴奋行为结束后自动清空兴奋值 (归零)"""
        self.excitement = 0.0

    def update_tick(self, dt: float = 0.1, behavior: BehaviorType = BehaviorType.IDLE_BLINK):
        """每 100ms 调用一次的心态动力学更新与衰减"""
        now = time.time()
        idle_duration = now - self.last_interaction_time

        # 1. 惊吓自然衰减 (减缓10倍: 原 2.5*dt 调整为 0.25*dt，更持久的受惊戒备期)
        if self.fright > 0:
            self.fright = max(0.0, self.fright - 0.25 * dt)

        # 2. 闲置充能机制 (长时间无人打扰，精力蓄积 - 延缓 10 倍)
        if idle_duration > 20.0 and self.fright < 15.0:
            # 停止兴奋衰减，转为极缓慢充能积攒拆家冲动 (+0.1/s，延缓10倍)
            self.excitement = min(100.0, self.excitement + 0.1 * dt)
            # 舒适度由于缺少陪伴极缓慢下降 (-0.04/s，延缓10倍)
            self.comfort = max(10.0, self.comfort - 0.04 * dt)
        else:
            # 正常情况下：兴奋随时间消耗衰减 (-0.3/s，平缓衰减)
            if self.excitement > 10.0:
                self.excitement = max(10.0, self.excitement - 0.3 * dt)
            # 舒适自然向基准线 (25) 平缓回落
            if self.comfort > 25.0:
                self.comfort = max(25.0, self.comfort - 0.15 * dt)
            elif self.comfort < 25.0 and self.fright < 10.0:
                self.comfort = min(25.0, self.comfort + 0.1 * dt)

        # 3. 平静度动态平衡计算
        stress = max(self.fright, self.excitement * 0.7, (self.comfort - 30) * 0.5)
        self.calm = max(0.0, min(100.0, 100.0 - stress))

        # 3. 疲劳度更新逻辑
        if behavior == BehaviorType.REST_SLEEP:
            # 睡眠状态：严格暂停随时间增加的被动疲劳增长（增量为 0）
            # 稳定执行精力恢复（速率 -0.10 点/秒，即每分钟恢复 6 点疲劳，疲劳只减不增）
            sleep_recovery_rate = -0.10
            self.fatigue = max(0.0, min(100.0, self.fatigue + sleep_recovery_rate * dt))
        else:
            # 清醒状态：活动消耗 + 随时间自然疲劳积累
            active_rates = {
                # Preserve approximately the old total change over the new,
                # minute-scale action durations.
                BehaviorType.IDLE_BLINK: -0.00035,
                BehaviorType.IDLE_WADDLE: 0.0026,
                BehaviorType.IDLE_FLY: 0.65,
                BehaviorType.EXCITE_PLAY_BALL: 0.05,
                BehaviorType.EAT_PLANT: 0.04,
                BehaviorType.MAGIC_TRICK: 0.04,
                BehaviorType.SKATEBOARD: 0.05,
                BehaviorType.EXCITE_HOP: 0.0019,
                BehaviorType.EXCITE_BOB: 0.007,
                BehaviorType.EXCITE_HEART_WINGS: 0.09,
                BehaviorType.EXCITE_SING: 0.0012,
                BehaviorType.EXCITE_BONK: 0.008,
                BehaviorType.MISCHIEF_CHEW: 0.10,
                BehaviorType.COMFORT_APPROACH: 0.35,
                BehaviorType.FRIGHT_PANIC_FLY: 0.55,
                BehaviorType.COMFORT_FLUFF: -0.0010,
                BehaviorType.COMFORT_PREEN: -0.0016,
                BehaviorType.COMFORT_YAWN: -0.0050,
            }
            if behavior in active_rates:
                rate = active_rates[behavior]
            elif self.calm >= 70.0:
                rate = -0.035
            else:
                rate = 0.02

            # 清醒状态下，每分钟额外随时间增加 1 点疲劳 (+1.0 / 60.0 点/秒)
            passive_fatigue_rate = 1.0 / 60.0
            total_rate = rate + passive_fatigue_rate

            # 兴奋状态下，疲劳累积速度提升 2 倍
            is_excited_state = (self.excitement >= 40.0 or behavior in EXCITED_BEHAVIORS)
            if is_excited_state and total_rate > 0:
                total_rate *= 2.0

            self.fatigue = max(0.0, min(100.0, self.fatigue + total_rate * dt))

    def must_sleep(self, now: float = None) -> bool:
        """疲劳度大于 90% 且惊吓值 < 50% 时，强制进入睡眠。
        若处于唤醒冷却期 (sleep_cooldown_until) 或刚刚发生过主动交互，不强制入睡，保护用户交互体验。
        """
        now = time.time() if now is None else now
        if now < self.sleep_cooldown_until:
            return False
        if now - self.last_interaction_time < 15.0:
            return False
        return self.fatigue > 90.0 and self.fright < 50.0

    def can_sleep(self, now: float = None) -> bool:
        now = time.time() if now is None else now
        # 惊吓值优先级最高: 大于等于 50% 无论多困都绝对无法入睡
        if self.fright >= 50.0:
            return False
        # 若处于唤醒冷却保护期或最近交互保护期内，绝对不入睡
        if now < self.sleep_cooldown_until or now - self.last_interaction_time < 5.0:
            return False
        # 疲劳度大于 90% 强制可入睡
        if self.fatigue > 90.0:
            return True
        # 疲劳值大于 50% 且惊吓值小于 50% 可概率入睡
        return self.fatigue > 50.0

    def should_sleep(self, now: float = None) -> bool:
        """疲劳值大于50%后，疲劳值越大入睡概率越大；疲劳值>90%强制必睡(100%)；惊吓值>=50%绝对不睡"""
        now = time.time() if now is None else now
        if self.fright >= 50.0:
            return False
        # 处于唤醒冷却或交互保护期内不入睡
        if now < self.sleep_cooldown_until or now - self.last_interaction_time < 5.0:
            return False
        if self.fatigue > 90.0:
            return True
        if not self.can_sleep(now):
            return False
        # 疲劳值在 50~90 之间，入睡概率由 15% 平滑增加至 85%
        chance = 0.15 + ((self.fatigue - 50.0) / 40.0) * 0.70
        return random.random() < chance

    def can_seek_petting(self, now: float = None) -> bool:
        now = time.time() if now is None else now
        return now - self.last_head_pet_time >= 1800.0

    def pet_head(self) -> Tuple[float, float, str]:
        """抚摸头颈部 (安全区交互)"""
        now = time.time()
        self.last_interaction_time = now
        self.last_head_pet_time = now

        old_comfort = self.comfort
        self.comfort = min(100.0, self.comfort + 7.0)
        self.fright = max(0.0, self.fright - 5.0)
        self.excitement = min(100.0, self.excitement + 1.5)
        return (self.comfort - old_comfort, 0.0, "舒服地享受抚摸")

    def touch_body(self) -> Tuple[bool, str]:
        """触碰躯干/翅膀 (禁区交互)
        返回: (是否触发恐慌惊飞, 行为说明)
        """
        now = time.time()
        self.last_interaction_time = now
        # 记录点击时间戳，剔除 2 秒外的记录
        self.body_click_timestamps = [t for t in self.body_click_timestamps if now - t <= 2.0]
        self.body_click_timestamps.append(now)

        # 高亲密度特权检查
        if self.comfort > 85.0 and len(self.body_click_timestamps) == 1:
            self.comfort -= 20.0
            self.fright = min(100.0, self.fright + 8.0)
            return (False, "虽不满但看在深厚交情份上未咬人")

        click_count = len(self.body_click_timestamps)
        if click_count >= 3:
            # 2秒内连续点 3 次，应激爆发
            self.fright = min(100.0, self.fright + 35.0)
            self.comfort = max(0.0, self.comfort - 30.0)
            return (True, "连续被戳，极度应激惊飞逃跑！")
        elif click_count == 2:
            self.fright = min(100.0, self.fright + 25.0)
            self.comfort = max(0.0, self.comfort - 20.0)
            return (False, "愤怒反咬并哈气！")
        else:
            self.fright = min(100.0, self.fright + 18.0)
            self.comfort = max(0.0, self.comfort - 15.0)
            return (False, "闪电反咬鼠标！")

    def hover_head_tick(self, dt: float = 0.1):
        """鼠标悬停在头顶的温和抚慰"""
        self.last_interaction_time = time.time()
        self.comfort = min(100.0, self.comfort + 1.5 * dt)
        if self.fright > 0:
            self.fright = max(0.0, self.fright - 2.0 * dt)

    def select_next_behavior(self, current_behavior: BehaviorType = None, is_at_edge: bool = False) -> Tuple[BehaviorDef, float]:
        """基于当前四维心态向量通过轮盘赌抽取下一个行为与持续时长"""
        # 如果惊吓值极高，直接强偏置
        weights: List[float] = []
        candidates: List[BehaviorDef] = []

        for b_code, b_def in BEHAVIOR_CATALOG.items():
            # 过滤不可作为自发行为的动作 (如闪电咬只有在被戳瞬间发生，打哈欠仅在理毛后概率触发，心形翅膀已隐藏)
            if b_code in (BehaviorType.FRIGHT_BITE, BehaviorType.REST_SLEEP, BehaviorType.REST_FALL_ASLEEP, BehaviorType.REST_WAKE, BehaviorType.REST_WAKE_CURIOUS, BehaviorType.COMFORT_YAWN, BehaviorType.EXCITE_HEART_WINGS):
                continue
            # 敲击屏幕 (EXCITE_BONK) 仅在处于屏幕边缘时才允许自发触发
            if b_code == BehaviorType.EXCITE_BONK and not is_at_edge:
                continue
            if (b_code in (BehaviorType.COMFORT_APPROACH, BehaviorType.COMFORT_BOW)
                    and not self.can_seek_petting()):
                continue

            # 滑板、魔术、踩红球设定为高阶兴奋动作，兴奋度 > 20 才允许自发触发
            if b_code in (BehaviorType.SKATEBOARD, BehaviorType.MAGIC_TRICK, BehaviorType.EXCITE_PLAY_BALL):
                if self.excitement <= 20.0:
                    continue

            w = b_def.base_weight \
                + b_def.w_fright * self.fright \
                + b_def.w_comfort * self.comfort \
                + b_def.w_excite * self.excitement \
                + random.gauss(0, 1.5)

            # 避免重复相同动作的轻微惩罚
            if current_behavior == b_code:
                w *= 0.6

            w = max(0.01, w)
            candidates.append(b_def)
            weights.append(w)

        chosen: BehaviorDef = random.choices(candidates, weights=weights, k=1)[0]
        # 持续时间正态抽样
        duration = random.gauss(chosen.duration_mean, chosen.duration_std)
        duration = max(1.0, min(900.0, duration))
        return chosen, duration
