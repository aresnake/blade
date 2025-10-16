param(
  [string]$BlenderExe = $env:BLENDER_EXE,
  [string]$Preset = "FAST",
  [int]$Seconds = 4,
  [int]$Fps = 24,
  [double]$Radius = 2.5,
  [string]$Out = "renders/turntable.mp4",
  [int]$Samples = 32
)

# 1) Trouver Blender
if (-not $BlenderExe -or -not (Test-Path $BlenderExe)) {
  $BlenderExe = "D:\blender-4.5.3-windows-x64\blender.exe"
}
if (-not (Test-Path $BlenderExe)) {
  Write-Host "❌ Blender introuvable. Renseigne -BlenderExe ou BLENDER_EXE." -ForegroundColor Red
  exit 1
}

# 2) Exposer les paramètres via variables d'environnement (le script Python les lira)
$env:TT_PRESET  = $Preset
$env:TT_SECONDS = [string]$Seconds
$env:TT_FPS     = [string]$Fps
$env:TT_RADIUS  = [string]$Radius
$env:TT_OUT     = $Out
$env:TT_SAMPLES = [string]$Samples

# 3) Script Python temporaire (lit preset YAML + overrides env)
$py = @"
import os, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import bpy
from ares.modules.turntable import render_turntable

# Params depuis l'environnement
preset  = os.getenv("TT_PRESET", "FAST")
sec_env = float(os.getenv("TT_SECONDS", "4"))
fps_env = int(os.getenv("TT_FPS", "24"))
rad_env = float(os.getenv("TT_RADIUS", "2.5"))
out_env = os.getenv("TT_OUT", "renders/turntable.mp4")
smp_env = int(os.getenv("TT_SAMPLES", "32"))

# Charger YAML si dispo
p = {}
try:
    import yaml
    with open("config/turntable_presets.yaml","r",encoding="utf-8") as f:
        presets = yaml.safe_load(f) or {}
    p = presets.get(preset, {})
except Exception:
    p = {}

sec = float(p.get("seconds", sec_env))
fps = int(p.get("fps", fps_env))
rad = float(p.get("radius", rad_env))
smp = int(p.get("samples", smp_env))

print("[RUN] Blender:", bpy.app.version_string)
print("[RUN] preset:", preset, {"seconds":sec,"fps":fps,"radius":rad,"samples":smp})

out = render_turntable(radius=rad, seconds=sec, fps=fps, mp4_path=out_env.replace("\\\\","/"), samples=smp)
print("[RUN] Output:", out)
"@

$tmp = ".\tests\.tmp_run_turntable.py"
[System.IO.File]::WriteAllText($tmp, $py, [System.Text.Encoding]::UTF8)

# 4) Appel Blender
& $BlenderExe -b -noaudio -P $tmp
$code = $LASTEXITCODE

# 5) Nettoyage
Remove-Item $tmp -ErrorAction SilentlyContinue

exit $code
