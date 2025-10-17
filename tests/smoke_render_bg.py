# tests/smoke_render_bg.py — vérifie l'application de preset FFMPEG
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import bpy

from ares.helpers import select_engine
from ares.modules.render_bg import apply_output_preset

print("[RENDER_BG] Blender:", bpy.app.version_string)

eng = select_engine()
print("[RENDER_BG] engine:", eng)

res = apply_output_preset("config/render_output_defaults.yaml")
print("[RENDER_BG] preset:", res)

print("[RENDER_BG] ✅ OK (no render)")
