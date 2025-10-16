param(
  [string]$BlenderExe = $env:BLENDER_EXE,
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
out = render_turntable(radius=$Radius, seconds=$Seconds, fps=$Fps, mp4_path="$Out".replace("\\\\","/"))
print("[RUN] Output:", out)
"@
$Tmp = ".\tests\.tmp_run_turntable.py"
Set-Content -Encoding UTF8 $Tmp $script
& $BlenderExe -b -noaudio -P $Tmp
Remove-Item $Tmp -ErrorAction SilentlyContinue
