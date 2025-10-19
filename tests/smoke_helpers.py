# tests/smoke_helpers.py — Blade v13
# Injecte la racine du repo dans sys.path pour importer ares/ depuis tests/
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

try:
    pass
except Exception as e:
    print("[HELPERS] ❌ bpy import failed:", e)
    sys.exit(1)

from ares.helpers import assign_material, create_mesh_object, ensure_material, select_engine

print("[HELPERS] Blender:", getattr(__import__("bpy").app, "version_string", "?"))

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
