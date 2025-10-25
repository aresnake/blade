"""
ARES Sandbox quick test — Blender headless safe.
- Auto-sélectionne le meilleur render engine disponible.
- Respect des règles "Never Again" (no-ops, safe-set).
"""
import json
import sys

try:
    import bpy
except Exception:
    bpy = None

def enum_render_engines():
    try:
        prop = bpy.types.RenderSettings.bl_rna.properties["engine"]
        return [e.identifier for e in prop.enum_items]
    except Exception:
        return []

def set_if(obj, attr, value):
    try:
        if obj and hasattr(obj, attr):
            setattr(obj, attr, value)
            return True
    except Exception:
        pass
    return False

def choose_engine(preferred=("BLENDER_EEVEE","BLENDER_EEVEE_NEXT","CYCLES")):
    avail = enum_render_engines()
    for eng in preferred:
        if eng in avail:
            return eng, avail
    return (avail[0] if avail else None), avail

def main():
    payload = {"runner":"blender-headless","argv":sys.argv,"has_bpy": bpy is not None}
    if bpy:
        payload["blender_version"] = bpy.app.version_string
        payload["engine_before"] = bpy.context.scene.render.engine
        # Auto-choix moteur
        target, avail = choose_engine()
        payload["engines_available"] = avail
        payload["engine_target"] = target
        if target:
            set_if(bpy.context.scene.render, "engine", target)
        payload["engine_after"] = bpy.context.scene.render.engine

        # EEVEE toggles (safe, ignorés si non supportés)
        eevee = getattr(bpy.context.scene, "eevee", None)
        if eevee:
            set_if(eevee, "use_gtao", True)
            set_if(eevee, "use_bloom", True)
            set_if(eevee, "use_soft_shadows", True)

        payload["scene_name"] = bpy.context.scene.name
    print("[ARES] SANDBOX:", json.dumps(payload))

if __name__ == "__main__":
    main()
