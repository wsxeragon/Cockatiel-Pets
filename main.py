import os
import sys

# Windows 控制台编码安全配置
if sys.stdout and hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass
if sys.stderr and hasattr(sys.stderr, 'reconfigure'):
    try:
        sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        pass

from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QIcon
from config import get_base_dir, is_dev_mode
from autostart import sync_auto_start_path
from cockatiel_window import CockatielWindow
from radar_hud import RadarHUD

# 确保启动时工作目录始终切至程序根目录（防止开机自启时 Windows 默认 CWD 为 System32 导致的相对路径问题）
os.chdir(get_base_dir())

# 同步开机自启路径（若移动了程序目录且此前已开启自启，自动更新注册表路径）
sync_auto_start_path()

# 确保 assets/sprites 图片就绪
sprites_dir = os.path.join(get_base_dir(), "assets", "sprites")
if not os.path.exists(sprites_dir) or len(os.listdir(sprites_dir)) < 5:
    from generate_sprites_pixel import generate_all
    print("正在生成像素风玄凤鹦鹉帧素材...")
    generate_all()

def main():
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)

    icon_path = os.path.join(get_base_dir(), "assets", "cockatiel.ico")
    if os.path.exists(icon_path):
        app.setWindowIcon(QIcon(icon_path))

    # 创建玄凤桌面宠物主窗口（开启屏幕外呼啸飞入出场动画）
    pet = CockatielWindow(start_with_fly_in=True)

    # 创建四维心态雷达图监视器
    hud = RadarHUD(pet)
    pet.set_hud(hud)

    # 放置雷达监视器在桌宠目标降落点周边（确保安全置于可用屏幕内）
    rect = pet.get_screen_rect(use_available=True)
    target_x = int(pet.fly_target_pos.x()) if pet.is_flying else pet.x()
    target_y = int(pet.fly_target_pos.y()) if pet.is_flying else pet.y()
    hud_x = max(rect.left() + 20, min(rect.right() - hud.width() - 20, target_x - 340 if target_x > rect.left() + 360 else target_x + 120))
    hud_y = max(rect.top() + 20, min(rect.bottom() - hud.height() - 20, target_y - 280))
    hud.move(hud_x, hud_y)

    pet.show()
    hud.show()

    print("==================================================")
    print("[Cockatiel Pet] 原始灰玄凤鹦鹉桌面宠物 Demo 已启动！")
    print("--------------------------------------------------")
    print("交互指南:")
    print("  1. 摸摸头: 鼠标点击鹦鹉头顶/脖子，积攒舒适度，平复惊恐；")
    print("  2. 悬停求撸: 鼠标放在头顶停留 >0.6秒，鹦鹉主动低头；")
    print("  3. 戳身体: 鼠标点击肚子/翅膀，鹦鹉闪电反咬；连戳 3 次触发惊飞！")
    print("  4. 闲置拆家: 长时间不理它，精力蓄积，它会自顾自去啃咬屏幕；")
    print("  5. 右键菜单: 可开关雷达图、逗乐唱歌、重置心态或退出；")
    print("  6. 拖拽移动: 按住鼠标左键可直接在屏幕上拖拽放置。")
    print("==================================================")

    sys.exit(app.exec())

if __name__ == "__main__":
    main()
