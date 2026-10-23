import os
import shutil
import subprocess
import zipfile
from pathlib import Path

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

    # 确保没有后台残留的旧进程占用 DLL 文件
    os.system("taskkill /f /im CockatielPets.exe >nul 2>nul")

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

    # 2. 拷贝三套羽冠动画精灵帧与大便组件资源
    for sprite_dir in ["sprites", "sprites_classic", "sprites_triple", "poop"]:
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
     - 开机自启: 右键菜单直接开启/关闭随 Windows 登录自动启动；
     - 逗它唱歌、强制入睡、清空疲劳等控制指令。

感谢体验 Cockatiel-Pets！祝您与小玄凤相处愉快~
"""
    with open(os.path.join(dist_folder, "使用说明.txt"), "w", encoding="utf-8") as f:
        f.write(readme_txt)

    # 写入空白 txt 文件作为 0.0.9 版本变更验证标志
    with open(os.path.join(dist_folder, "version_0.0.9.txt"), "w", encoding="utf-8") as f:
        pass

    print("=== [4/4] 压缩打包绿色全量包与增量补丁包 ===")
    from config import APP_VERSION

    # 1. 全量独立安装包 (含 _internal/ 等全部依赖，约 54MB，供新用户使用)
    full_zip_name = f"Cockatiel-Pets-v{APP_VERSION}-Full-Setup.zip"
    full_zip_path = os.path.join(dist_root, full_zip_name)
    if os.path.exists(full_zip_path):
        os.remove(full_zip_path)

    print(f"正在压缩全量独立发布包: {full_zip_name} ...")
    with zipfile.ZipFile(full_zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(dist_folder):
            for file in files:
                full_path = os.path.join(root, file)
                rel_path = os.path.relpath(full_path, dist_root)
                zipf.write(full_path, rel_path)
    full_size_mb = os.path.getsize(full_zip_path) / (1024 * 1024)

    # 2. 增量热更新补丁包 (排除庞大的 _internal/，仅打包 CockatielPets.exe 与 assets，约 4.57MB)
    # 命名为 Cockatiel-Pets-v{APP_VERSION}-Patch-x64.zip，版本号清晰明确，更新器精准识别
    patch_zip_name = f"Cockatiel-Pets-v{APP_VERSION}-Patch-x64.zip"
    patch_zip_path = os.path.join(dist_root, patch_zip_name)
    if os.path.exists(patch_zip_path):
        os.remove(patch_zip_path)

    # 清理旧的无版本号补丁包
    old_patch_path = os.path.join(dist_root, "Cockatiel-Pets-Windows-x64.zip")
    if os.path.exists(old_patch_path):
        os.remove(old_patch_path)

    print(f"正在压缩增量更新补丁包: {patch_zip_name} ...")
    with zipfile.ZipFile(patch_zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(dist_folder):
            if "_internal" in Path(root).parts:
                continue
            for file in files:
                full_path = os.path.join(root, file)
                rel_path = os.path.relpath(full_path, dist_root)
                zipf.write(full_path, rel_path)
    patch_size_mb = os.path.getsize(patch_zip_path) / (1024 * 1024)

    print("==================================================")
    print("=== [SUCCESS] 全部打包完成！ ===")
    print(f"  1. 增量更新补丁包 (版本化补丁包): {patch_zip_path} ({patch_size_mb:.2f} MB)")
    print(f"  2. 全量独立安装包 (新用户/手动安装): {full_zip_path} ({full_size_mb:.2f} MB)")
    print("==================================================")

if __name__ == "__main__":
    main()
