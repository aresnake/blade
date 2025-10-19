import importlib  # keep imports at top (ruff E402)

bl_info = {
    "name":        "ARES",
    "author":      "Adrien",
    "version":     (0, 1, 0),
    "blender":     (4, 5, 0),
    "location":    "View3D > Sidebar",
    "description": "ARES tools (Render BG, turntable rig)",
    "category":    "Render",
}

# --- Shim legacy: allow `from ares import link_object` ---
try:
    from .modules.render_bg.turntable_rig import _link_only_to_collection as link_object
except Exception:
    link_object = None
try:
    from .modules.render_bg.turntable_rig import _add_circle_path as make_curve_circle
except Exception:
    make_curve_circle = None
def _safe_register(mod):
    if hasattr(mod, "register"):
        try:
            mod.register()
        except Exception as e:
            print("[ARES] register() failed in", getattr(mod, "__name__", mod), ":", e)

def _safe_unregister(mod):
    if hasattr(mod, "unregister"):
        try:
            mod.unregister()
        except Exception as e:
            print("[ARES] unregister() failed in", getattr(mod, "__name__", mod), ":", e)

def register():
    # UI
    try:
        from .ui import panel_render_bg as panel_render_bg
        importlib.reload(panel_render_bg)
        _safe_register(panel_render_bg)
    except Exception as e:
        print("[ARES] UI register failed:", e)

    # Rig (just ensure import works)
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
