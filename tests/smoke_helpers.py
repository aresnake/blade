# tests/smoke_helpers.py — Blade v13
# Vérifie helpers de base (engine/materials/objects) en headless.

import sys
try:
    import bpy
except Exception as e:
    print("[HELPERS] ❌ bpy import failed:", e)
    sys.exit(1)

from ares.helpers import select_engine, ensure_material, assign_material, create_mesh_object

print("[HELPERS] Blender:", bpy.app.version_string)

# 1) Engine select (ne doit pas lever)
eng = select_engine()
print("[HELPERS] engine:", eng)

# 2) Create a simple triangle mesh object (no bpy.ops)
obj = create_mesh_object(
    name="V13_Triangle",
    verts=[(0,0,0), (1,0,0), (0,1,0)],
    edges=[(0,1), (1,2), (2,0)],
    faces=[(0,1,2)],
)

# 3) Ensure/assign material
mat = ensure_material("V13_Mat")
ok = assign_material(obj, mat, slot_index=0)
print("[HELPERS] assign mat:", ok)

print("[HELPERS] ✅ OK")
