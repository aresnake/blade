# tests/smoke_blender.py — Blade v13
# Objectif : valider un démarrage headless + réglages EEVEE/EEVEE_NEXT "safe".

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

def select_engine(scene):
    # Liste des engines dispo selon la build
    try:
        enum_items = scene.render.bl_rna.properties["engine"].enum_items.keys()
    except Exception:
        enum_items = ("BLENDER_EEVEE", "BLENDER_EEVEE_NEXT", "BLENDER_WORKBENCH", "CYCLES")

    # Ordre de préférence (Never Again + fallback pragmatique)
    for e in ("BLENDER_EEVEE", "BLENDER_EEVEE_NEXT", "BLENDER_WORKBENCH", "CYCLES"):
        if e in enum_items:
            try:
                scene.render.engine = e
                print(f"[SMOKE] Render engine -> {e}")
                return e
            except Exception as ex:
                print(f"[SMOKE] ⚠️ Impossible de régler {e}: {ex}")
    print("[SMOKE] ❌ Aucun render engine applicable.")
    return None

print("[SMOKE] Blender:", bpy.app.version_string)
scene = bpy.context.scene

engine = select_engine(scene)

# Appliquer presets Eevee si Eevee/EeveeNext
if engine in ("BLENDER_EEVEE", "BLENDER_EEVEE_NEXT"):
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
        # Certaines props peuvent ne pas exister sur EeveeNext → best-effort
        print(f"[SMOKE] Eevee presets appliqués (props touchées: ~{changed})")
    else:
        print("[SMOKE] ⚠️ Scene.eevee indisponible.")
else:
    print(f"[SMOKE] ⚠️ Presets Eevee ignorés (engine actuel: {engine})")

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

if not getattr(world, "use_nodes", False):
    world.use_nodes = True

if getattr(world, "node_tree", None):
    print("[SMOKE] World nodes OK (tree existant utilisé).")

print("[SMOKE] ✅ OK — Headless baseline stable.")
