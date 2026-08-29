@echo off
setlocal
cd /d "%~dp0"
py eazy_windows.py %*
if errorlevel 1 pause
endlocal
