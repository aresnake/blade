# tests/run_dog_turntable.py
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import bpy

from ares.helpers import select_engine
from ares.modules.animals import create_lowpoly_dog
from ares.modules.turntable import render_turntable

print("[DOG] Blender:", bpy.app.version_string)
select_engine()
dog = create_lowpoly_dog()
out = render_turntable(target=dog, radius=3.0, seconds=4, fps=24, mp4_path="renders/dog_turntable.mp4")
print("[DOG] ✅ Done:", out)
