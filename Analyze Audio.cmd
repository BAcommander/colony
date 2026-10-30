@echo off
setlocal
set "ANALYSIS_ROOT=%~dp0"
set "ANALYSIS_PYTHON=%ANALYSIS_ROOT%.local\audio-analysis\Scripts\python.exe"
if not exist "%ANALYSIS_PYTHON%" set "ANALYSIS_PYTHON=python"
"%ANALYSIS_PYTHON%" "%ANALYSIS_ROOT%scripts\analyze_ambient_audio.py" --open %*
if errorlevel 1 pause
