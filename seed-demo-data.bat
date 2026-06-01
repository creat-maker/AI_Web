@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo EduMind demo data seed
echo.
python scripts\seed_demo_data.py
if errorlevel 1 (
  echo.
  echo Demo data seed failed. Please check Python and backend dependencies.
  pause
  exit /b 1
)
echo.
echo Demo data seed completed.
pause
