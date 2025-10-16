param([string]$BlenderExe = $env:BLENDER_EXE)
if (-not $BlenderExe -or -not (Test-Path $BlenderExe)) { $BlenderExe = "D:\blender-4.5.3-windows-x64\blender.exe" }
if (-not (Test-Path $BlenderExe)) { Write-Host "❌ Blender introuvable." -ForegroundColor Red; exit 1 }
& $BlenderExe -b -noaudio -P "tests/run_render_bg_demo.py"
