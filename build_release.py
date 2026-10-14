import os
import shutil
import subprocess
import zipfile

def main():
    print("=== [1/4] 开始 PyInstaller 打包流程 ===")

    dist_root = "dist"
    build_root = "build"
    app_name = "CockatielPets"

    assets_abs = os.path.abspath("assets")
    icon_abs = os.path.abspath(r"assets\cockatiel.ico")

    pyinstaller_cmd = [
        r"d:\pets\.venv\Scripts\pyinstaller.exe",
        f"--name={app_name}",
        "--noconsole",
        "--onedir",
        "--clean",
        "-y",
        f"--icon={icon_abs}",
        f"--distpath={dist_root}",
        f"--workpath={build_root}",
        f"--specpath={build_root}",
        "main.py"
    ]

    dist_folder = os.path.join(dist_root, app_name)
    if os.path.exists(dist_folder):
        shutil.rmtree(dist_folder, ignore_errors=True)

    print("执行命令:", " ".join(pyinstaller_cmd))
    subprocess.run(pyinstaller_cmd, check=True)

    print("=== [2/4] 补全资源与配置文件 ===")
    dest_assets = os.path.join(dist_folder, "assets")
    if os.path.exists(dest_assets):
        shutil.rmtree(dest_assets, ignore_errors=True)
    os.makedirs(dest_assets, exist_ok=True)

    # 1. 拷贝核心图标与羽冠配置
    for item in ["crest_config.json", "cockatiel.ico"]:
        src_item = os.path.join("assets", item)
        dst_item = os.path.join(dest_assets, item)
        if os.path.exists(src_item):
            shutil.copy2(src_item, dst_item)

    # 2. 写入发布版应用配置 (明确设定 dev_mode 为 False，隐藏调试按钮与多余菜单)
    import json
    with open(os.path.join(dest_assets, "app_config.json"), "w", encoding="utf-8") as f:
        json.dump({"dev_mode": False}, f, indent=2, ensure_ascii=False)

    # 2. 拷贝三套羽冠动画精灵帧
    for sprite_dir in ["sprites", "sprites_classic", "sprites_triple"]:
        src_dir = os.path.join("assets", sprite_dir)
        dst_dir = os.path.join(dest_assets, sprite_dir)
        if os.path.exists(src_dir):
            shutil.copytree(src_dir, dst_dir)

    print("=== [3/4] 写入便捷启动脚本与使用说明 ===")
    bat_content = '@echo off\ncd /d "%~dp0"\nstart "" "%~dp0CockatielPets.exe"\n'
    with open(os.path.join(dist_folder, "启动桌宠.bat"), "w", encoding="ansi") as f:
        f.write(bat_content)

    readme_txt = """==================================================
  🐤 Cockatiel-Pets (玄凤鹦鹉桌面宠物) 绿色免安装版
==================================================

【快速启动】
  直接双击运行 "CockatielPets.exe" (或 "启动桌宠.bat") 即可直接启动！
  * 无需安装 Python，无需安装任何第三方库与依赖，解压即用。

【桌面交互指南】
  1. 摸摸头: 鼠标点击头颈部安全区，积攒舒适度，平复惊吓；
  2. 悬停求撸: 鼠标悬停在头顶 >0.6 秒，鹦鹉主动低头眯眼撒娇；
  3. 戳身体: 鼠标点击腹部/翅膀禁区，鹦鹉闪电反咬；连戳 3 次触发暴怒与惊飞；
  4. 拖拽摆放: 鼠标左键按住鸟身，可随意拖拽放置在屏幕任意位置；
  5. 专属右键菜单:
     - 切换羽冠: 支持随时无缝切换【经典兔耳】或【灵动三毛】羽冠造型；
     - 雷达图监视器: 实时监控五维心态与疲劳动力学；
     - 逗它唱歌、强制入睡、清空疲劳等控制指令。

感谢体验 Cockatiel-Pets！祝您与小玄凤相处愉快~
"""
    with open(os.path.join(dist_folder, "使用说明.txt"), "w", encoding="utf-8") as f:
        f.write(readme_txt)

    print("=== [4/4] 压缩打包绿色发布 ZIP 文件 ===")
    zip_filename = os.path.join(dist_root, "Cockatiel-Pets-Windows-x64.zip")
    if os.path.exists(zip_filename):
        os.remove(zip_filename)

    with zipfile.ZipFile(zip_filename, "w", zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(dist_folder):
            for file in files:
                full_path = os.path.join(root, file)
                rel_path = os.path.relpath(full_path, dist_root)
                zipf.write(full_path, rel_path)

    zip_size_mb = os.path.getsize(zip_filename) / (1024 * 1024)
    print(f"=== 全部完成！绿色发布包已生成: {zip_filename} ({zip_size_mb:.2f} MB) ===")

if __name__ == "__main__":
    main()
