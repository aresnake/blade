# Blade v13 — QUICKSTART

## 1) Turntable ultra-court
powershell -NoProfile -File .\tools\Turntable.ps1 -Preset FAST -Out "renders/tt_fast.mp4"

## 2) Turntable normal
powershell -NoProfile -File .\tools\Turntable.ps1 -Preset NORMAL -Out "renders/tt_norm.mp4"

## 3) Low-poly dog + turntable (mp4)
$env:BLENDER_EXE = "D:\blender-4.5.3-windows-x64\blender.exe"
& $env:BLENDER_EXE -b -noaudio -P "tests/run_dog_turntable.py"

### Fichiers en sortie
- renders/tt_fast.mp4
- renders/tt_norm.mp4
- renders/dog_turntable.mp4
