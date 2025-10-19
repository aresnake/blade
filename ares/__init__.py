bl_info = {
    "name":        "ARES",
    "author":      "Adrien",
    "version":     (0, 1, 0),
    "blender":     (4, 5, 0),
    "location":    "View3D > Sidebar",
    "description": "ARES tools (Render BG, turntable rig)",
    "category":    "Render",
}

import importlib

def _safe_register(mod):
    if hasattr(mod, "register"):
        mod.register()

def _safe_unregister(mod):
    if hasattr(mod, "unregister"):
        mod.unregister()

def register():
    # Charger/rafraîchir le panneau UI
    try:
        from .ui import panel_render_bg as panel_render_bg
        importlib.reload(panel_render_bg)
        _safe_register(panel_render_bg)
    except Exception as e:
        print("[ARES] UI register failed:", e)

    # Charger le rig pour être sûr qu'il est importable (pas de register requis)
    try:
        from .modules.render_bg import turntable_rig as turntable_rig
        importlib.reload(turntable_rig)
    except Exception as e:
        print("[ARES] rig load failed:", e)

def unregister():
    try:
        from .ui import panel_render_bg as panel_render_bg
        _safe_unregister(panel_render_bg)
    except Exception as e:
        print("[ARES] UI unregister failed:", e)