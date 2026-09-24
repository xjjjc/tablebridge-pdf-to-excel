@echo off
cd /d "%~dp0"
if exist ".venv\Scripts\python.exe" goto run
py -3 -m venv .venv
if errorlevel 1 (
  echo Install Python 3.11 or newer from python.org, then try again.
  pause
  exit /b 1
)
:run
.venv\Scripts\python.exe -c "import pdfplumber, openpyxl" >nul 2>&1
if not errorlevel 1 goto launch
.venv\Scripts\python.exe -m pip install -r requirements.txt
if errorlevel 1 (
  echo Dependency installation failed. Check your internet connection and retry.
  pause
  exit /b 1
)
:launch
.venv\Scripts\python.exe app.py
pause
