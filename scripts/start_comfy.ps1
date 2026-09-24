$ErrorActionPreference = 'Stop'
$colonyRoot = Split-Path $PSScriptRoot -Parent
$pythonPath = Join-Path $colonyRoot '.local/comfy-env/Scripts/python.exe'
$comfyPath = Join-Path $colonyRoot '.local/ComfyUI'
$outputPath = Join-Path $colonyRoot 'creative/ringfall/animation/wan-tests'
& $pythonPath (Join-Path $comfyPath 'main.py') --listen 127.0.0.1 --port 8188 --disable-api-nodes --lowvram --reserve-vram 1 --output-directory $outputPath
