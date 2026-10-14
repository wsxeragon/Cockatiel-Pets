@echo off
chcp 936 >nul 2>nul
cd /d "%~dp0"

REM 1. 优先使用本地虚拟环境 (.venv)
if exist "%~dp0.venv\Scripts\pythonw.exe" (
    start "" "%~dp0.venv\Scripts\pythonw.exe" "%~dp0main.py"
    exit /b 0
)

REM 2. 检查是否有绿色免安装版
if exist "%~dp0dist\CockatielPets\CockatielPets.exe" (
    start "" "%~dp0dist\CockatielPets\CockatielPets.exe"
    exit /b 0
)

REM 3. 检查系统全局 Python
python -c "import PySide6" >nul 2>nul
if %errorlevel% equ 0 (
    start "" pythonw "%~dp0main.py"
    exit /b 0
)

echo =======================================================
echo [Cockatiel-Pets] 未检测到可用的运行环境
echo.
echo 方式 1 (推荐，绿色免安装):
echo   直接解压 dist/Cockatiel-Pets-Windows-x64.zip
echo   双击其中的 "CockatielPets.exe" 即可直接运行！
echo.
echo 方式 2 (源码运行):
echo   请先安装 Python 3.10+ 并执行:
echo   pip install -r requirements.txt
echo =======================================================
pause
