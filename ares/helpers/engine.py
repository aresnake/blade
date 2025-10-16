# Blade v13 — helpers.engine
# Sélection moteur robuste (EEVEE → EEVEE_NEXT → WORKBENCH → CYCLES)
import bpy

def select_engine(scene=None):
    if scene is None:
        scene = bpy.context.scene
    try:
        enum_items = scene.render.bl_rna.properties["engine"].enum_items.keys()
    except Exception:
        enum_items = ("BLENDER_EEVEE", "BLENDER_EEVEE_NEXT", "BLENDER_WORKBENCH", "CYCLES")

    for e in ("BLENDER_EEVEE", "BLENDER_EEVEE_NEXT", "BLENDER_WORKBENCH", "CYCLES"):
        if e in enum_items:
            try:
                scene.render.engine = e
                return e
            except Exception:
                pass
    return None
