@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo EduMind 演示数据初始化
echo.
python scripts\seed-demo-data.py
if errorlevel 1 (
  echo.
  echo 演示数据初始化失败，请检查 Python 环境和后端依赖。
  pause
  exit /b 1
)
echo.
echo 演示数据初始化完成。
pause
