# -*- coding: utf-8 -*-
import os
import bpy
import importlib

# Import depuis le repo local si possible
BASE = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if BASE not in os.sys.path:
    os.sys.path.insert(0, BASE)

import ares
importlib.reload(ares)
from ares.modules import turntable_gen as tt

# Build rig + set frame 1
tt.create_turntable(radius=6.0, height=2.0, path_duration=120, fps=24)
bpy.context.scene.frame_set(1)

# Output path
out_dir = os.path.join(BASE, "dist")
os.makedirs(out_dir, exist_ok=True)
bpy.context.scene.render.filepath = os.path.join(out_dir, "tt_frame1.png")

# Render one still (ops is fine for render)
bpy.ops.render.render(write_still=True)
print("[RENDER] Wrote:", bpy.context.scene.render.filepath)