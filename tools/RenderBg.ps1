param(
  [string]$BlenderExe = $env:BLENDER_EXE,
  [int]$Frames = 5,
  [int]$Fps = 24,
  [string]$Out = "renders/out.mp4"
)
if (-not $BlenderExe -or -not (Test-Path $BlenderExe)) { $BlenderExe = "D:\blender-4.5.3-windows-x64\blender.exe" }
if (-not (Test-Path $BlenderExe)) { Write-Host "❌ Blender introuvable." -ForegroundColor Red; exit 1 }

$script = @"
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path: sys.path.insert(0, str(ROOT))
import bpy
from ares.modules.render_bg.demo import render_demo
print("[RUN] Blender:", bpy.app.version_string)
out = render_demo(mp4_path="$Out".replace("\\","/"), frame_count=$Frames, fps=$Fps)
print("[RUN] Output file:", out)
print("[RUN] ✅ Done")
"@
$Tmp = ".\tests\.tmp_run_render_bg_demo.py"
Set-Content -Encoding UTF8 $Tmp $script
& $BlenderExe -b -noaudio -P $Tmp
Remove-Item $Tmp -ErrorAction SilentlyContinue
