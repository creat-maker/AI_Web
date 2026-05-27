@echo off
setlocal

set "ROOT=%~dp0"
cd /d "%ROOT%"

echo [EduMind] Checking project structure...

if not exist "backend\" (
  echo [ERROR] Missing backend directory.
  goto error
)

if not exist "frontend\" (
  echo [ERROR] Missing frontend directory.
  goto error
)

if not exist "backend\app\main.py" (
  echo [ERROR] Missing backend\app\main.py.
  goto error
)

if not exist "frontend\package.json" (
  echo [ERROR] Missing frontend\package.json.
  goto error
)

if not exist "frontend\node_modules\" (
  echo [ERROR] Missing frontend\node_modules.
  echo Please install frontend dependencies first:
  echo   cd frontend
  echo   npm install
  goto error
)

echo [EduMind] Starting backend and frontend in separate windows...

start "EduMind Backend" cmd /k "cd /d ""%ROOT%backend"" && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"
start "EduMind Frontend" cmd /k "cd /d ""%ROOT%frontend"" && npm run dev"

echo.
echo Services are starting. Access URLs:
echo   Backend: http://localhost:8000
echo   API Docs: http://localhost:8000/docs
echo   Frontend: http://localhost:5173
echo   Dashboard: http://localhost:5173/dashboard
echo   TutorChat: http://localhost:5173/tutor-chat
echo   KnowledgeBase: http://localhost:5173/knowledge-base
echo   TeacherAnalysis: http://localhost:5173/teacher-analysis
echo.
echo Close this window when you are done reading these addresses.
pause
exit /b 0

:error
echo.
echo Startup aborted.
pause
exit /b 1
