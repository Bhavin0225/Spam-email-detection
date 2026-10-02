@echo off
title Spam Email Detection System

cd /d "%~dp0"

echo ========================================================
echo        SPAM EMAIL DETECTION ^& AUDITING PLATFORM
echo ========================================================
echo.

:: 1. Verify Docker Availability
echo [1/5] Checking Docker daemon status...
docker info >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Docker is not running or not installed.
    echo Please launch Docker Desktop and wait until it is ready, then run this file again.
    echo.
    pause
    exit /b 1
)
echo [OK] Docker daemon is running.
echo.

:: 2. Stop Existing Docker Containers
echo [2/5] Stopping existing project containers...
docker-compose down

:: 3. Build and Start Docker Services
echo.
echo [3/5] Building and starting Docker services (DB, FastAPI backend, React frontend)...
echo (This incorporates all latest frontend and backend changes)
docker-compose up -d --build --force-recreate
if errorlevel 1 (
    echo [ERROR] Failed to start Docker services.
    pause
    exit /b 1
)

:: 4. Start Streamlit Admin Console
echo.
echo [4/5] Launching Streamlit Admin Console in background...
set "PY_CMD=python"
if exist "%~dp0backend\venv\Scripts\python.exe" set "PY_CMD=%~dp0backend\venv\Scripts\python.exe"
if exist "%~dp0backend\.venv\Scripts\python.exe" set "PY_CMD=%~dp0backend\.venv\Scripts\python.exe"

start "Streamlit Admin Console" cmd /k "cd /d "%~dp0backend" && set MONGODB_URI=mongodb://localhost:27018/phishing_detection_db&& %PY_CMD% -m streamlit run scripts\streamlit_app.py"

:: 5. Health Check and Open Browser
echo.
echo [5/5] Waiting for services to initialize...
timeout /t 6 /nobreak >nul

echo.
echo ========================================================
echo             SERVICES ARE UP AND RUNNING!
echo ========================================================
echo  * Web Application (React):   http://localhost:3000
echo  * Streamlit Admin Console:   http://localhost:8501
echo  * FastAPI Swagger API Docs:  http://localhost:8000/docs
echo  * MongoDB Database:          localhost:27018
echo.
echo  Default Credentials:
echo  - Admin: admin@example.com / AdminPassword123!
echo  - User:  bhavin0225@gmail.com / bhavin252006
echo ========================================================
echo.
echo Opening Web Application and Streamlit Console in your browser...
start http://localhost:3000
start http://localhost:8501

echo.
echo Done! All services are active.
echo To shut down all containers, open a terminal here and run 'docker-compose down'.
echo.
pause
