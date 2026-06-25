@echo off
echo ==========================================
echo  GWF Logo Overlay Server + ngrok Tunnel
echo ==========================================
echo.

:: Start Flask server in background
start "GWF Overlay Server" python "C:\Users\fuzzy\OneDrive\Documents\Claude projects\GrowwestFinance_MVP\overlay_server.py"

:: Wait for Flask to start
timeout /t 3 /nobreak > nul

:: Start ngrok tunnel (exposes port 5050 publicly)
echo Starting ngrok tunnel on port 5050...
echo.
echo COPY the ngrok https URL below and use it in Make.com:
echo   POST https://xxxx-xxx-xxx.ngrok-free.app/overlay
echo.
ngrok http 5050

pause
