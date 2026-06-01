@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo EduMind demo readiness check
echo.
python scripts\check-demo-ready.py
if errorlevel 1 (
  echo.
  echo Demo readiness check failed. Please seed demo data or start services first.
  pause
  exit /b 1
)
echo.
echo Demo readiness check completed.
pause
