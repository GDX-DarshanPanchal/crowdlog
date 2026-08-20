@echo off
setlocal
cd /d "%~dp0"

set "PYTHON_CMD="
py -3 -c "import sys; assert sys.version_info >= (3, 11)" >nul 2>nul
if not errorlevel 1 set "PYTHON_CMD=py -3"

if not defined PYTHON_CMD (
  python -c "import sys; assert sys.version_info >= (3, 11)" >nul 2>nul
  if not errorlevel 1 set "PYTHON_CMD=python"
)

if not defined PYTHON_CMD (
  python3 -c "import sys; assert sys.version_info >= (3, 11)" >nul 2>nul
  if not errorlevel 1 set "PYTHON_CMD=python3"
)

if not defined PYTHON_CMD (
  echo Python 3.11 or newer could not be started.
  echo.
  echo This is not an internet problem. Windows may be opening the Microsoft Store
  echo shortcut instead of the Python installation.
  echo.
  echo Please reinstall Python from https://www.python.org/downloads/windows/
  echo and select "Add python.exe to PATH" on the first installation screen.
  echo Then restart Windows and double-click this file again.
  pause
  exit /b 1
)

%PYTHON_CMD% -c "import openpyxl" >nul 2>nul
if errorlevel 1 (
  echo Installing the required Excel package. Please wait...
  %PYTHON_CMD% -m pip install -r requirements.txt
  if errorlevel 1 (
    echo.
    echo The required package could not be installed.
    echo The message above contains the specific reason.
    echo If this is a company computer, your IT security policy may block Python packages.
    pause
    exit /b 1
  )
)

if not exist output mkdir output
set OPEN_BROWSER=1
start "Crowdlog Monthly Report - keep this window open" %PYTHON_CMD% "%~dp0web_app.py"
exit /b 0
