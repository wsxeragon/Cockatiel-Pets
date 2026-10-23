import os
import sys
import re
import json
import tempfile
import zipfile
import subprocess
import urllib.request
import urllib.error
from pathlib import Path
from typing import Optional, Tuple, Dict, Any

from PySide6.QtCore import QThread, Signal
from config import get_base_dir, APP_VERSION

GITHUB_REPO = "wsxeragon/Cockatiel-Pets"
RELEASES_API_URL = f"https://api.github.com/repos/{GITHUB_REPO}/releases"

# 镜像加速地址（应对国内无法直连 api.github.com 或 github.com 下载卡顿）
GHPROXY_PREFIX = "https://ghproxy.net/"

def normalize_version(v_str: str) -> Tuple[int, ...]:
    """
    版本号解析与归一化（严格忽略前导 'v' 或 'V'，仅比对纯数字段）
    例如：
      'V0.0.6' -> (0, 0, 6)
      '0.0.6'  -> (0, 0, 6)
      'v0.0.5' -> (0, 0, 5)
      'V1.2.0-pre' -> (1, 2, 0)
    """
    if not v_str:
        return (0, 0, 0)
    s = str(v_str).strip()
    if s.startswith(('v', 'V')):
        s = s[1:].strip()
    # 截取元数据前的主干版本号
    s = s.split('-')[0].split('+')[0].strip()
    parts = []
    for p in s.split('.'):
        m = re.match(r'^\d+', p)
        if m:
            parts.append(int(m.group(0)))
        else:
            parts.append(0)
    while len(parts) < 3:
        parts.append(0)
    return tuple(parts)

def is_newer_version(cloud_ver_str: str, local_ver_str: str = APP_VERSION) -> bool:
    """比对云端版本号是否高于本地版本号（纯数值元组比对，完全不带 V 参与判断）"""
    return normalize_version(cloud_ver_str) > normalize_version(local_ver_str)

def fetch_latest_release_info(timeout: int = 10) -> Dict[str, Any]:
    """
    从 GitHub 获取最新发布的 Release 信息。
    优先官方接口，失败时自动尝试镜像加速。
    """
    urls_to_try = [
        RELEASES_API_URL,
        f"{GHPROXY_PREFIX}{RELEASES_API_URL}"
    ]

    last_error = ""
    for url in urls_to_try:
        try:
            req = urllib.request.Request(
                url,
                headers={
                    "User-Agent": "CockatielPets-Updater",
                    "Accept": "application/vnd.github.v3+json"
                }
            )
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                if not isinstance(data, list) or len(data) == 0:
                    raise ValueError("未在 GitHub 仓库中找到任何 Release 发布记录")
                
                # 取第一个（最新的 Release，支持 pre-release）
                latest = data[0]
                tag_name = latest.get("tag_name", "").strip()
                title = latest.get("name", "") or tag_name
                body = latest.get("body", "") or "暂无更新说明"
                assets = latest.get("assets", [])

                # 寻找更新发布包：优先增量补丁包 / 标准更新包 (Cockatiel-Pets-Windows-x64.zip 或包含 patch)，次选全量安装包
                target_asset = None
                for a in assets:
                    name_lower = a.get("name", "").lower()
                    if name_lower == "cockatiel-pets-windows-x64.zip" or "patch" in name_lower:
                        target_asset = a
                        break
                if not target_asset:
                    for a in assets:
                        if a.get("name", "").lower().endswith(".zip"):
                            target_asset = a
                            break

                download_url = target_asset["browser_download_url"] if target_asset else ""
                size_bytes = target_asset["size"] if target_asset else 0

                return {
                    "tag_name": tag_name,
                    "title": title,
                    "body": body,
                    "download_url": download_url,
                    "size_bytes": size_bytes,
                    "has_update": is_newer_version(tag_name, APP_VERSION)
                }
        except Exception as e:
            last_error = str(e)
            continue

    raise RuntimeError(f"获取更新信息失败: {last_error}")

class CheckUpdateWorker(QThread):
    """异步检查更新后台线程"""
    check_finished = Signal(bool, dict, str) # success, info, error_msg

    def run(self):
        try:
            info = fetch_latest_release_info()
            self.check_finished.emit(True, info, "")
        except Exception as e:
            self.check_finished.emit(False, {}, str(e))

class DownloadUpdateWorker(QThread):
    """异步下载更新包后台线程"""
    progress = Signal(int, int, int) # percent, downloaded_bytes, total_bytes
    finished = Signal(bool, str, str) # success, saved_zip_path, error_msg

    def __init__(self, download_url: str, expected_size: int = 0):
        super().__init__()
        self.download_url = download_url
        self.expected_size = expected_size
        self._is_cancelled = False

    def cancel(self):
        self._is_cancelled = True

    def run(self):
        # 尝试直连与镜像双通道
        urls_to_try = [self.download_url]
        if not self.download_url.startswith(GHPROXY_PREFIX):
            urls_to_try.append(f"{GHPROXY_PREFIX}{self.download_url}")

        temp_dir = Path(tempfile.gettempdir()) / "cockatiel_update"
        temp_dir.mkdir(parents=True, exist_ok=True)
        save_path = temp_dir / "update_package.zip"

        last_error = ""
        for url in urls_to_try:
            if self._is_cancelled:
                self.finished.emit(False, "", "用户已取消下载")
                return

            try:
                req = urllib.request.Request(
                    url,
                    headers={"User-Agent": "CockatielPets-Updater"}
                )
                with urllib.request.urlopen(req, timeout=15) as resp:
                    total_len = int(resp.headers.get("Content-Length", self.expected_size or 0))
                    downloaded = 0
                    chunk_size = 64 * 1024 # 64KB

                    with open(save_path, "wb") as f_out:
                        while True:
                            if self._is_cancelled:
                                self.finished.emit(False, "", "用户已取消下载")
                                return
                            chunk = resp.read(chunk_size)
                            if not chunk:
                                break
                            f_out.write(chunk)
                            downloaded += len(chunk)
                            percent = int((downloaded / total_len) * 100) if total_len > 0 else 0
                            self.progress.emit(percent, downloaded, total_len)

                # 下载完成并校验 zip 有效性
                if zipfile.is_zipfile(save_path):
                    self.finished.emit(True, str(save_path), "")
                    return
                else:
                    last_error = "下载的文件不是有效的 ZIP 格式"
            except Exception as e:
                last_error = str(e)
                continue

        self.finished.emit(False, "", f"下载失败: {last_error}")

def launch_updater_and_exit(zip_path: str, target_dir: Optional[Path] = None):
    """
    生成并启动独立的批处理更新器，解压全量包覆盖并重启主程序。
    """
    if target_dir is None:
        target_dir = get_base_dir()

    target_dir_abs = os.path.abspath(target_dir)
    zip_path_abs = os.path.abspath(zip_path)
    pid = os.getpid()

    temp_dir = Path(tempfile.gettempdir()) / "cockatiel_update"
    temp_dir.mkdir(parents=True, exist_ok=True)
    bat_path = temp_dir / "update_and_restart.bat"
    extract_dir = temp_dir / "extracted"

    bat_content = f"""@echo off
chcp 65001 >nul
title 正在为小玄凤安装新版本更新...

echo ======================================================
echo    🐤 正在更新 Cockatiel-Pets 到最新版本...
echo ======================================================
echo 正在等待原程序完全退出 (PID: {pid})...

:: 循环等待原进程完全释放锁定
:WAIT_LOOP
tasklist /fi "PID eq {pid}" | findstr "{pid}" >nul
if %ERRORLEVEL% equ 0 (
    timeout /t 1 /nobreak >nul
    goto WAIT_LOOP
)

:: 额外缓冲 1 秒确保文件句柄释放
timeout /t 1 /nobreak >nul

echo 正在解压新版资源与文件...
if exist "{extract_dir}" rmdir /s /q "{extract_dir}"
powershell -Command "Expand-Archive -Path '{zip_path_abs}' -DestinationPath '{extract_dir}' -Force"

echo 正在覆盖程序文件至 {target_dir_abs}...
:: 判断解压出来是否包含顶级 CockatielPets 目录
if exist "{extract_dir}\\CockatielPets" (
    xcopy /y /e /q "{extract_dir}\\CockatielPets\\*" "{target_dir_abs}\\" >nul
) else (
    xcopy /y /e /q "{extract_dir}\\*" "{target_dir_abs}\\" >nul
)

echo 正在重启小玄凤桌宠...
cd /d "{target_dir_abs}"
if exist "{target_dir_abs}\\CockatielPets.exe" (
    start "" "{target_dir_abs}\\CockatielPets.exe"
) else (
    start "" "启动桌宠.bat"
)

echo 更新完成！
:: 清理临时解压目录与脚本自身
rmdir /s /q "{extract_dir}" >nul 2>nul
del "{zip_path_abs}" >nul 2>nul
(goto) 2>nul & del "%~f0"
exit
"""
    with open(bat_path, "w", encoding="ansi") as f:
        f.write(bat_content)

    # 启动后台批处理
    subprocess.Popen(
        ["cmd.exe", "/c", str(bat_path)],
        cwd=target_dir_abs,
        creationflags=subprocess.CREATE_NEW_CONSOLE if sys.platform == "win32" else 0
    )

    # 主进程退出
    from PySide6.QtWidgets import QApplication
    app = QApplication.instance()
    if app:
        app.quit()
    else:
        sys.exit(0)
