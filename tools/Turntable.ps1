param(
  [string]$BlenderExe = $env:BLENDER_EXE,
  [string]$Preset = "FAST",
  [int]$Seconds = 4,
  [int]$Fps = 24,
  [float]$Radius = 2.5,
  [string]$Out = "renders/turntable.mp4"
)
if (-not $BlenderExe -or -not (Test-Path $BlenderExe)) { $BlenderExe = "D:\blender-4.5.3-windows-x64\blender.exe" }
if (-not (Test-Path $BlenderExe)) { Write-Host "❌ Blender introuvable." -ForegroundColor Red; exit 1 }

$script = @"
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path: sys.path.insert(0, str(ROOT))
import bpy
from ares.modules.turntable import render_turntable
print("[RUN] Blender:", bpy.app.version_string)
import yaml, json
# charger preset si dispo
try:
    with open("config/turntable_presets.yaml","r",encoding="utf-8") as f:
        presets = yaml.safe_load(f) or {}
    p = presets.get("$Preset", {})
except Exception:
    p = {}
sec = p.get("seconds", $Seconds)
fps = p.get("fps", $Fps)
rad = p.get("radius", $Radius)
smp = p.get("samples", 32)
out = render_turntable(radius=rad, seconds=sec, fps=fps, mp4_path="$Out".replace("\\\\","/"), samples=smp)
print("[RUN] preset:", "$Preset", {"seconds":sec,"fps":fps,"radius":rad,"samples":smp})
)
print("[RUN] Output:", out)
"@
$Tmp = ".\tests\.tmp_run_turntable.py"
Set-Content -Encoding UTF8 $Tmp $script
& $BlenderExe -b -noaudio -P $Tmp
Remove-Item $Tmp -ErrorAction SilentlyContinue

