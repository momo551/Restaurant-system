@echo off
title Restaurant Management System - Startup
color 0A

echo ==========================================
echo  Restaurant Management System - Starting
echo ==========================================
echo.

REM === 1. Start Redis Server ===
echo [1/4] Starting Redis Server...
start "Redis Server" cmd /k "C:\Redis\redis-server.exe"
timeout /t 2 /nobreak > nul

REM === 2. Start Celery Worker ===
echo [2/4] Starting Celery Worker...
start "Celery Worker" cmd /k "cd /d %~dp0backend && celery -A core worker -l info -P solo"
timeout /t 2 /nobreak > nul

REM === 3. Start Celery Beat ===
echo [3/4] Starting Celery Beat (Scheduler)...
start "Celery Beat" cmd /k "cd /d %~dp0backend && celery -A core beat -l info"
timeout /t 2 /nobreak > nul

REM === 4. Start Django Server (ASGI/Daphne) ===
echo [4/4] Starting Django Server with Daphne (ASGI)...
start "Django Server" cmd /k "cd /d %~dp0backend && daphne -b 127.0.0.1 -p 8000 core.asgi:application"
timeout /t 2 /nobreak > nul

echo.
echo ==========================================
echo  All services started successfully!
echo  Django: http://127.0.0.1:8000
echo ==========================================
echo.
echo Press any key to close this window...
pause > nul
