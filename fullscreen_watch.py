"""全屏应用检测（Windows）。

判断前台是否正在运行全屏程序（独占全屏游戏、无边框全屏游戏、全屏视频等）。
用途：全屏期间把桌宠与仪表盘临时隐藏——置顶窗口压在游戏画面上会让游戏失去
独立翻转（MPO）导致掉帧，同时避免新窗口抢走键鼠/手柄焦点。

非 Windows 平台或任何异常情况一律返回 False（宁可不动，也不要误藏）。
"""
import ctypes
import os
import sys

_QUNS_BUSY = 2                     # 有全屏应用在运行（非 D3D）
_QUNS_RUNNING_D3D_FULL_SCREEN = 3  # D3D 独占全屏

_MONITOR_DEFAULTTONEAREST = 2
_GWL_STYLE = -16
_WS_CAPTION = 0x00C00000


class _MONITORINFO(ctypes.Structure):
    _fields_ = [
        ("cbSize", ctypes.c_ulong),
        ("rcMonitor", ctypes.c_long * 4),
        ("rcWork", ctypes.c_long * 4),
        ("dwFlags", ctypes.c_ulong),
    ]


def _covers_monitor(hwnd) -> bool:
    """前台窗口是否正好铺满所在显示器（容忍 2px 误差，用来区分最大化窗口的隐藏边框）。"""
    from ctypes import wintypes

    user32 = ctypes.windll.user32
    rect = wintypes.RECT()
    if not user32.GetWindowRect(hwnd, ctypes.byref(rect)):
        return False

    mon = user32.MonitorFromWindow(hwnd, _MONITOR_DEFAULTTONEAREST)
    if not mon:
        return False

    info = _MONITORINFO()
    info.cbSize = ctypes.sizeof(_MONITORINFO)
    if not user32.GetMonitorInfoW(mon, ctypes.byref(info)):
        return False

    ml, mt, mr, mb = info.rcMonitor
    tol = 2
    return (abs(rect.left - ml) <= tol and abs(rect.top - mt) <= tol
            and abs(rect.right - mr) <= tol and abs(rect.bottom - mb) <= tol)


def _is_borderless(hwnd) -> bool:
    """没有标题栏（WS_CAPTION）——无边框全屏游戏的特征；最大化的浏览器/资源管理器有标题栏。"""
    user32 = ctypes.windll.user32
    user32.GetWindowLongPtrW.restype = ctypes.c_ssize_t
    user32.GetWindowLongPtrW.argtypes = [ctypes.c_void_p, ctypes.c_int]
    style = user32.GetWindowLongPtrW(hwnd, _GWL_STYLE) & 0xFFFFFFFF
    return not (style & _WS_CAPTION)


def is_fullscreen_app_foreground(exclude_pid: int = None) -> bool:
    """前台是否在全屏应用上。

    exclude_pid 传入自身进程号时，自家窗口在前台不会被判成全屏（避免把自己藏了）。
    """
    if sys.platform != "win32":
        return False

    try:
        from ctypes import wintypes

        user32 = ctypes.windll.user32
        hwnd = user32.GetForegroundWindow()
        if not hwnd:
            return False

        pid = wintypes.DWORD()
        user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
        own = os.getpid() if exclude_pid is None else exclude_pid
        if pid.value == own:
            return False

        # 1) 系统通知状态：全屏应用在跑时系统会报 BUSY / D3D 独占全屏
        try:
            shell32 = ctypes.windll.shell32
            shell32.SHQueryUserNotificationState.restype = ctypes.c_long
            shell32.SHQueryUserNotificationState.argtypes = [ctypes.POINTER(ctypes.c_int)]
            state = ctypes.c_int(0)
            if shell32.SHQueryUserNotificationState(ctypes.byref(state)) == 0:
                if state.value in (_QUNS_BUSY, _QUNS_RUNNING_D3D_FULL_SCREEN):
                    return True
        except Exception:
            pass

        # 2) 兜底：无边框 + 正好铺满整块显示器
        return _covers_monitor(hwnd) and _is_borderless(hwnd)
    except Exception:
        return False
