@echo off
setlocal
cd /d "%~dp0"

where python >nul 2>nul
if errorlevel 1 (
  echo Python was not found.
  echo Please install Python from https://www.python.org/downloads/
  echo During installation, select "Add Python to PATH".
  pause
  exit /b 1
)

python -c "import openpyxl" >nul 2>nul
if errorlevel 1 (
  echo Installing the required Excel package. Please wait...
  python -m pip install -r requirements.txt
  if errorlevel 1 (
    echo.
    echo Installation did not finish. Check your internet connection and try again.
    pause
    exit /b 1
  )
)

if not exist output mkdir output
set OPEN_BROWSER=0
start "Crowdlog Monthly Report" pythonw "%~dp0web_app.py"
timeout /t 3 /nobreak >nul
start "" "http://127.0.0.1:8765"
exit /b 0
