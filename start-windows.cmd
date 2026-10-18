@echo off
setlocal
cd /d "%~dp0"
if not exist ".venv\Scripts\pythonw.exe" (
  echo Create the environment first: python -m venv .venv
  echo Then install: .venv\Scripts\python.exe -m pip install -e ".[desktop]"
  pause
  exit /b 1
)
".venv\Scripts\python.exe" -c "import tkinter, pandas, matplotlib" >nul 2>&1
if errorlevel 1 (
  echo Install desktop support: .venv\Scripts\python.exe -m pip install -e ".[desktop]"
  pause
  exit /b 1
)
start "" ".venv\Scripts\pythonw.exe" -m activity_monitor --desktop
