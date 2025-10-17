# tests/run_render_bg_demo.py — exécute un mini rendu .mp4 (5 frames) headless
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import bpy

from ares.modules.render_bg.demo import render_demo

print("[RUN] Blender:", bpy.app.version_string)
out = render_demo(mp4_path="//renders/out.mp4", frame_count=5, fps=24)
print("[RUN] Output file:", out)
print("[RUN] ✅ Done")
