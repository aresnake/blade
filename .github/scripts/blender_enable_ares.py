import os
import sys

# workspace du job GitHub
workspace = os.environ.get("GITHUB_WORKSPACE", ".")
if workspace and workspace not in sys.path:
    sys.path.insert(0, workspace)

print("[SMOKE] sys.path[0] =", sys.path[0])
import bpy  # assuré par Blender

# Le module doit être importable via le workspace
import ares

print("[SMOKE] ares.__version__ =", getattr(ares, "__version__", "n/a"))

# Optionnel : tenter l'activation si l'addon a un bl_info et un nom de module "ares"
try:
    bpy.ops.preferences.addon_enable(module="ares")
    print("[SMOKE] addon_enable OK")
except Exception as e:
    print(f"[SMOKE] addon_enable WARN: {e}")
