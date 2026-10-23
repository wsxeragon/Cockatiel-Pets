import os
import sys
import json
from pathlib import Path

# 当前应用版本号（不带 V 前缀）
APP_VERSION = "0.0.9"

def get_base_dir() -> Path:
    """获取运行根目录（自动兼容 PyInstaller 打包环境与源码开发环境）"""
    if getattr(sys, 'frozen', False):
        return Path(sys.executable).parent
    return Path(__file__).resolve().parent

def get_config_path() -> Path:
    return get_base_dir() / "assets" / "app_config.json"

def is_dev_mode() -> bool:
    """
    判断当前是否处于开发调试模式。
    优先级：
    1. 环境变量 COCKATIEL_DEV_MODE (1/true/dev)
    2. 配置文件 assets/app_config.json 中的 dev_mode 字段
    3. 默认策略: 打包版 (frozen) 为 False (发布模式)，源码运行为 True (开发模式)
    """
    # 1. 环境变量覆盖
    env_mode = os.environ.get("COCKATIEL_DEV_MODE")
    if env_mode is not None:
        return env_mode.strip().lower() in ("1", "true", "yes", "dev")

    # 2. 配置文件覆盖
    cfg_file = get_config_path()
    if cfg_file.exists():
        try:
            with open(cfg_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                if "dev_mode" in data and isinstance(data["dev_mode"], bool):
                    return data["dev_mode"]
        except Exception:
            pass

    # 3. 默认根据是否为打包独立可执行文件推断
    is_frozen = getattr(sys, 'frozen', False)
    return not is_frozen

def save_dev_mode(dev_mode: bool) -> None:
    """保存 dev_mode 配置至 assets/app_config.json"""
    cfg_file = get_config_path()
    data = {}
    if cfg_file.exists():
        try:
            with open(cfg_file, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception:
            data = {}
    data["dev_mode"] = dev_mode
    cfg_file.parent.mkdir(parents=True, exist_ok=True)
    with open(cfg_file, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def is_poop_disabled() -> bool:
    """获取是否禁止大小便配置 (默认 False，即允许自然排泄)"""
    cfg_file = get_config_path()
    if cfg_file.exists():
        try:
            with open(cfg_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                if "disable_poop" in data and isinstance(data["disable_poop"], bool):
                    return data["disable_poop"]
        except Exception:
            pass
    return False

def set_poop_disabled(disabled: bool) -> None:
    """保存禁止大小便配置至 assets/app_config.json"""
    cfg_file = get_config_path()
    data = {}
    if cfg_file.exists():
        try:
            with open(cfg_file, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception:
            data = {}
    data["disable_poop"] = disabled
    cfg_file.parent.mkdir(parents=True, exist_ok=True)
    with open(cfg_file, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
