@echo off
REM Export Trading Bot Logs for Email Sharing
REM Usage: export_logs.bat [days]

echo ======================================
echo   Trading Bot Log Export Utility
echo ======================================
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    echo Please install Python and try again.
    pause
    exit /b 1
)

REM Set number of days (default 7)
set DAYS=7
if not "%1"=="" set DAYS=%1

echo Exporting logs from last %DAYS% days...
echo.

REM Run the log export script
python log_export.py --days %DAYS%

echo.
echo ======================================
echo Log export completed!
echo.
echo To send via email:
echo 1. Open your email client
echo 2. Attach the ZIP file from exported_logs folder
echo 3. Use the email template shown above
echo ======================================
echo.

pause
