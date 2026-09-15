@echo off
title Restaurant Management System - Startup
color 0A

echo ==========================================
echo  Restaurant Management System - Starting
echo ==========================================
echo.

REM === 1. Start Django Server (ASGI/Daphne) ===
echo [1/1] Starting Django Server with Daphne (ASGI)...
start /min "Django Server" cmd /k "cd /d %~dp0backend && daphne -b 127.0.0.1 -p 8000 core.asgi:application"
timeout /t 2 /nobreak > nul

echo.
echo ==========================================
echo  All services started successfully!
echo  Django: http://127.0.0.1:8000
echo ==========================================
echo.
echo Press any key to close this window...
pause > nul
