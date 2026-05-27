@echo off
setlocal

echo [EduMind] This will close processes using local development ports 8000 and 5173.
echo [EduMind] No files will be deleted.
echo.
pause

for %%P in (8000 5173) do (
  echo Checking port %%P...
  for /f "tokens=5" %%A in ('netstat -ano ^| findstr ":%%P" ^| findstr "LISTENING"') do (
    echo Stopping PID %%A on port %%P...
    taskkill /PID %%A /F
  )
)

echo.
echo Done. Ports 8000 and 5173 have been checked.
pause
exit /b 0
