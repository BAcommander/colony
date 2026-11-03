@echo off
setlocal
set "SNOWLINE_ROOT=%~dp0"
set "SNOWLINE_PY=python"
if exist "%SNOWLINE_ROOT%.local\audio-analysis\Scripts\python.exe" (
  set "SNOWLINE_PY=%SNOWLINE_ROOT%.local\audio-analysis\Scripts\python.exe"
)
"%SNOWLINE_PY%" "%SNOWLINE_ROOT%scripts\restore_snowline_session.py" %*
if errorlevel 1 (
  pause
  exit /b 1
)
"%SNOWLINE_PY%" "%SNOWLINE_ROOT%scripts\restore_snowline_nov3.py" %*
if errorlevel 1 (
  pause
  exit /b 1
)
"%SNOWLINE_PY%" "%SNOWLINE_ROOT%scripts\restore_snowline_snow_session.py" %*
if errorlevel 1 (
  pause
  exit /b 1
)
start "" "%SNOWLINE_ROOT%music\snowline-snow-2026-11-03\RESUME.md"
