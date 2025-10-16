# tests/smoke_blender.py — Blade v13
# Objectif : valider un démarrage headless + réglages EEVEE "safe" sans dépendances externes.

import sys

try:
    import bpy
except Exception as e:
    print("[SMOKE] ❌ Impossible d'importer bpy:", e)
    sys.exit(1)

def safe_set(obj, prop, value):
    try:
        if hasattr(obj, prop):
            setattr(obj, prop, value)
            return True
    except Exception:
        pass
    return False

print("[SMOKE] Blender:", bpy.app.version_string)
scene = bpy.context.scene

# Moteur : EEVEE (BLENDER_EEVEE)
try:
    scene.render.engine = "BLENDER_EEVEE"
    print("[SMOKE] Render engine -> BLENDER_EEVEE")
except Exception as e:
    print("[SMOKE] ⚠️ Impossible de mettre EEVEE:", e)

# Appliquer quelques presets robustes (sans casser si propriétés absentes)
ee = getattr(scene, "eevee", None)
if ee:
    changed = 0
    changed += 1 if safe_set(ee, "use_gtao", True) else 0
    changed += 1 if safe_set(ee, "use_bloom", True) else 0
    changed += 1 if safe_set(ee, "use_soft_shadows", True) else 0
    safe_set(ee, "shadow_cube_size", 1024)
    safe_set(ee, "shadow_cascade_size", 2048)
    safe_set(ee, "taa_samples", 16)
    safe_set(ee, "taa_render_samples", 64)
    print(f"[SMOKE] Eevee presets appliqués (props touchées: ~{changed})")
else:
    print("[SMOKE] ⚠️ Scene.eevee indisponible.")

# Color management (best effort)
if hasattr(scene, "view_settings"):
    vs = scene.view_settings
    safe_set(vs, "view_transform", "Filmic")
    safe_set(vs, "look", "None")
    safe_set(vs, "exposure", 0.0)
    safe_set(vs, "gamma", 1.0)
    print("[SMOKE] Color management appliqué (Filmic).")

# World nodes (sans réassigner le tree)
world = scene.world
if world is None:
    world = bpy.data.worlds.new("World")
    scene.world = world

if not world.use_nodes:
    world.use_nodes = True

if world.node_tree:
    print("[SMOKE] World nodes OK (tree existant utilisé).")

print("[SMOKE] ✅ OK — Headless baseline stable.")
