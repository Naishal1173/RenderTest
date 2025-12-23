@echo off
title PDF Document Chatbot Server

echo.
echo ========================================
echo   PDF Document Chatbot Server
echo ========================================
echo.
echo 🚀 Starting your chatbot...

REM Change to script directory
cd /d "%~dp0"

REM Start the Python server
python web_frontend.py

echo.
echo ❌ Server stopped. Press any key to restart or close window to exit.
pause >nul
goto :eof