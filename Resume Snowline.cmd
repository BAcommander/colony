@echo off
setlocal
set "SNOWLINE_ROOT=%~dp0"
if exist "%SNOWLINE_ROOT%.local\audio-analysis\Scripts\python.exe" (
  "%SNOWLINE_ROOT%.local\audio-analysis\Scripts\python.exe" "%SNOWLINE_ROOT%scripts\restore_snowline_session.py" %*
) else (
  python "%SNOWLINE_ROOT%scripts\restore_snowline_session.py" %*
)
if errorlevel 1 (
  pause
  exit /b 1
)
start "" "%SNOWLINE_ROOT%music\snowline-sound-design-2026-11-02\RESUME.md"
