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

# 确保 assets/sprites 图片就绪
sprites_dir = os.path.join(os.path.dirname(__file__), "assets", "sprites")
if not os.path.exists(sprites_dir) or len(os.listdir(sprites_dir)) < 5:
    from generate_sprites_pixel import generate_all
    print("正在生成像素风玄凤鹦鹉帧素材...")
    generate_all()

from PySide6.QtWidgets import QApplication
from cockatiel_window import CockatielWindow
from radar_hud import RadarHUD

def main():
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)

    # 创建玄凤桌面宠物主窗口
    pet = CockatielWindow()

    # 创建四维心态雷达图监视器
    hud = RadarHUD(pet)
    pet.set_hud(hud)

    # 放置雷达监视器在桌宠旁边
    hud.move(max(20, pet.x() - 340), max(20, pet.y() - 280))

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
