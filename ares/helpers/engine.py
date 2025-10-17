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
# === ARES engine helpers (safe for 4.5.x) ===
def pick_engine(bpy):
    """Return a safe engine identifier available in this Blender build."""
    enums = {i.identifier for i in bpy.types.RenderSettings.bl_rna.properties['engine'].enum_items}
    if 'BLENDER_EEVEE' in enums:
        return 'BLENDER_EEVEE'
    if 'BLENDER_EEVEE_NEXT' in enums:
        return 'BLENDER_EEVEE_NEXT'
    return 'CYCLES'

def ensure_engine(bpy, scene=None):
    """Ensure scene.render.engine is set to a valid, preferred engine."""
    scene = scene or bpy.context.scene
    eng = pick_engine(bpy)
    if scene.render.engine != eng:
        scene.render.engine = eng
    return eng
