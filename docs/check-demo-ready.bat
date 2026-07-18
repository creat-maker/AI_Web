@echo off
setlocal
chcp 65001 >nul

set "REPO_ROOT=%~dp0.."
pushd "%REPO_ROOT%" >nul 2>&1
if errorlevel 1 (
  echo [FAIL] Cannot enter repository root: %REPO_ROOT%
  exit /b 2
)

echo [EduMind] Offline demo readiness check
echo [EduMind] Repository: %CD%
echo [EduMind] External LLM and Xfyun cloud calls are not required.
echo [EduMind] Real cloud capabilities remain unverified unless separately configured and tested.
echo.

python scripts\check-demo-ready.py --skip-http --output "交付成果_最新版/01_验收日志/demo_ready_check_第二轮_原始报告.md"
set "CHECK_EXIT=%ERRORLEVEL%"

echo.
if "%CHECK_EXIT%"=="0" (
  echo [PASS] Offline demo readiness check completed.
) else (
  echo [FAIL] Offline demo readiness check failed with exit code %CHECK_EXIT%.
  echo        Run python scripts\seed_demo_data.py and verify local dependencies.
)

popd >nul
exit /b %CHECK_EXIT%
