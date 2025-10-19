from __future__ import annotations

import bpy


def apply_mp4_preset(scene: bpy.types.Scene, *, filepath="//renders/out.mp4", fps=24, seconds=4):
    from ares.ui.panel_render_bg import _ensure_scene_settings
    _ensure_scene_settings(scene, fps=fps, seconds=seconds, filepath=filepath)
    return {"filepath": filepath, "fps": fps, "seconds": seconds}

