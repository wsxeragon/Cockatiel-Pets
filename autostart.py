"""
autostart.py - Windows 开机自启管理模块

使用 Windows 注册表 HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Run
实现用户级开机自启（无需管理员权限，随系统登录自动启动）。
"""
import sys
import os
from pathlib import Path
from typing import Tuple
from config import get_base_dir

REG_RUN_KEY = r"Software\Microsoft\Windows\CurrentVersion\Run"
REG_APP_NAME = "CockatielPets"

def is_auto_start_supported() -> bool:
    """判断当前操作系统是否支持自启配置（目前仅支持 Windows）"""
    return sys.platform == "win32"

def get_launch_command() -> str:
    """
    获取开机自启动时的执行命令字符串。
    - 打包独立版 (frozen): "D:\\...\\CockatielPets.exe"
    - 源码运行版: "D:\\...\\pythonw.exe" "D:\\...\\main.py"
    """
    if getattr(sys, "frozen", False):
        exe_path = Path(sys.executable).resolve()
        return f'"{exe_path}"'
    
    # 源码开发环境下，优先查找同目录下的 pythonw.exe（无控制台黑框）
    py_dir = Path(sys.executable).parent
    pythonw = py_dir / "pythonw.exe"
    py_bin = pythonw if pythonw.exists() else Path(sys.executable)
    main_py = (get_base_dir() / "main.py").resolve()
    return f'"{py_bin.resolve()}" "{main_py}"'

def is_auto_start_enabled() -> bool:
    """
    检查当前是否已启用开机自启。
    读取注册表 HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Run 中的 CockatielPets 项。
    """
    if not is_auto_start_supported():
        return False
    try:
        import winreg
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, REG_RUN_KEY, 0, winreg.KEY_READ) as key:
            val, _ = winreg.QueryValueEx(key, REG_APP_NAME)
            return bool(val and str(val).strip())
    except (FileNotFoundError, OSError):
        return False

def set_auto_start(enable: bool) -> Tuple[bool, str]:
    """
    开启或关闭开机自启。
    :param enable: True 为开启，False 为关闭
    :return: (是否成功, 提示信息)
    """
    if not is_auto_start_supported():
        return False, "当前系统非 Windows，暂不支持开机自启"

    try:
        import winreg
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, REG_RUN_KEY, 0, winreg.KEY_SET_VALUE) as key:
            if enable:
                cmd = get_launch_command()
                winreg.SetValueEx(key, REG_APP_NAME, 0, winreg.REG_SZ, cmd)
                return True, "已开启开机自启"
            else:
                try:
                    winreg.DeleteValue(key, REG_APP_NAME)
                except FileNotFoundError:
                    pass
                return True, "已关闭开机自启"
    except Exception as e:
        return False, f"操作注册表失败: {e}"

def sync_auto_start_path() -> None:
    """
    如果已开启自启，但注册表中的路径与当前程序所在路径不一致（例如用户移动了文件夹），
    自动更新注册表中的自启路径，防止启动失效。
    """
    if not is_auto_start_supported():
        return
    try:
        import winreg
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, REG_RUN_KEY, 0, winreg.KEY_READ) as key:
            val, _ = winreg.QueryValueEx(key, REG_APP_NAME)
        
        current_cmd = get_launch_command()
        if val and str(val).strip() != current_cmd:
            # 路径变更，静默更新为当前绝对路径
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, REG_RUN_KEY, 0, winreg.KEY_SET_VALUE) as key:
                winreg.SetValueEx(key, REG_APP_NAME, 0, winreg.REG_SZ, current_cmd)
    except Exception:
        pass
