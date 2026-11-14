@echo off
chcp 65001 > nul
set PYTHONIOENCODING=utf-8
title VQUANT REAL-TIME QUANTITATIVE WEB DASHBOARD
color 0B
cd /d "%~dp0"

echo ======================================================================
echo    VQUANT INSTITUTIONAL WEB DASHBOARD - REAL-TIME TELEMETRY SERVER
echo    Tac gia: Nguyen Manh Cuong _ B22DCCN099 (Khoa CNTT 1 - PTIT)
echo ======================================================================
echo.
echo Dang khoi dong Web Dashboard Server (FastAPI + WebSockets)...
echo Trinh duyet se tu dong mo tai: http://127.0.0.1:8000
echo Nhan Ctrl+C de dung server.
echo.

set PY_EXE=
if exist "%LOCALAPPDATA%\Programs\Python\Python311\python.exe" (
    set "PY_EXE=%LOCALAPPDATA%\Programs\Python\Python311\python.exe"
) else if exist ".venv\Scripts\python.exe" (
    set "PY_EXE=.venv\Scripts\python.exe"
) else (
    set "PY_EXE=python"
)

start "" http://127.0.0.1:8000
"%PY_EXE%" -m uvicorn src.web.app:app --host 127.0.0.1 --port 8000

echo.
echo Web Dashboard Server da dung.
pause
