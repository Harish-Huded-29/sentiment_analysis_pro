@echo off
REM Change to project directory
cd /d D:\Segement_analysis_project

REM Activate virtual environment
call venv\Scripts\activate

REM Start Python app in background
start /B python app.py

REM Wait for server to start (adjust time if needed)
timeout /t 3 /nobreak >nul

REM Open browser
start http://127.0.0.1:5000

REM Close the batch file window
exit