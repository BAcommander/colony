@echo off
setlocal
set "TEXTURE_ROOT=%~dp0"
set "TEXTURE_PYTHON=%TEXTURE_ROOT%.local\audio-analysis\Scripts\python.exe"
if not exist "%TEXTURE_PYTHON%" (
  echo The local audio-analysis Python environment is missing.
  echo See creative\music\reference-analysis\nonmusical-2026-11-02\README.md for setup.
  pause
  exit /b 1
)
"%TEXTURE_PYTHON%" "%TEXTURE_ROOT%scripts\analyze_radio_texture.py" %* --open
if errorlevel 1 pause
