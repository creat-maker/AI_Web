@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo EduMind 演示健康检查
echo.
python scripts\check-demo-ready.py
if errorlevel 1 (
  echo.
  echo 演示健康检查未通过，请按提示补齐演示数据或文件。
  pause
  exit /b 1
)
echo.
echo 演示健康检查完成。
pause
