@echo off
setlocal
rem Kudosy launcher for Windows. Works from any folder (paths are relative to this file).
rem All settings, cookies, history and logs are stored in the "data" folder next to this file.
set "KUDOSY_DATA_DIR=%~dp0data"
set "VENV_PY=%~dp0.venv\Scripts\python.exe"

if not exist "%VENV_PY%" (
    echo Virtual environment not found: "%~dp0.venv"
    echo Create it in the project folder with:
    echo     python -m venv .venv
    echo     .venv\Scripts\python -m pip install -e ".[dev]"
    pause
    exit /b 1
)

echo Data folder: %KUDOSY_DATA_DIR%
"%VENV_PY%" -X utf8 -m kudosy
