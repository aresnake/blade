# SPDX-License-Identifier: MIT
# Path: ares/ui/panel_render_bg.py

import contextlib
import importlib

import bpy
from bpy.props import IntProperty, PointerProperty, StringProperty

from ares.modules.render_bg import preset as PR

importlib.reload(PR)


# --- Property Group (module-level, fiable) -------------------------------------

class ARES_RenderBG_Props(bpy.types.PropertyGroup):
    output_path: StringProperty(
        name="Output",
        description="Chemin de sortie MP4 (H.264)",
        subtype="FILE_PATH",
        default="//renders/out.mp4",
    )
    fps: IntProperty(
        name="FPS",
        description="Images par seconde",
        min=1,
        max=240,
        default=24,
    )
    seconds: IntProperty(
        name="Duration (s)",
        description="Durée en secondes",
        min=1,
        max=600,
        default=4,
    )


# --- Operators -----------------------------------------------------------------

class ARES_OT_RenderBGApplyPreset(bpy.types.Operator):
    """Appliquer le preset MP4 (H.264) et caler la scène (fps, frames, chemin)."""
    bl_idname = "ares.render_bg_apply_preset"
    bl_label = "Apply MP4 Preset"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        scn = context.scene
        d = PR.apply_mp4_preset(scn)

        ui = getattr(scn, "ares_renderbg", None)
        if ui is not None:
            scn.render.filepath = ui.output_path or d.get("filepath", "//renders/out.mp4")
            scn.render.fps = int(ui.fps) if ui.fps else int(d.get("fps", 24))
            seconds = int(ui.seconds) if ui.seconds else int(d.get("seconds", 4))
        else:
            scn.render.filepath = d.get("filepath", "//renders/out.mp4")
            scn.render.fps = int(d.get("fps", 24))
            seconds = int(d.get("seconds", 4))

        scn.frame_start = 1
        scn.frame_end = scn.frame_start + (seconds * scn.render.fps) - 1

        self.report({"INFO"}, "Preset OK")
        return {"FINISHED"}


class ARES_OT_RenderBGRender(bpy.types.Operator):
    """Lancer le rendu animation (encode MP4 H.264 selon le preset)."""
    bl_idname = "ares.render_bg_render_mp4"
    bl_label = "Render MP4"
    bl_options = {"REGISTER"}

    def execute(self, context):
        bpy.ops.render.render(animation=True)
        self.report({"INFO"}, "Render MP4 terminé")
        return {"FINISHED"}


# --- Panel ---------------------------------------------------------------------

class ARES_PT_RenderBG(bpy.types.Panel):
    """Panneau de rendu MP4 rapide (ARES)."""
    bl_label = "ARES • Render BG"
    bl_idname = "ARES_PT_RenderBG"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "output"

    def draw(self, context):
        scn = context.scene
        ui = getattr(scn, "ares_renderbg", None)
        layout = self.layout
        if ui is None:
            layout.label(text="Initialising...", icon="INFO")
            return
        col = layout.column(align=True)
        col.prop(ui, "output_path")
        row = col.row(align=True)
        row.prop(ui, "fps")
        row.prop(ui, "seconds")
        layout.separator()
        layout.operator("ares.render_bg_apply_preset", icon="SETTINGS")
        layout.operator("ares.render_bg_render_mp4", icon="RENDER_ANIMATION")


# --- Registration --------------------------------------------------------------

CLASSES = (
    ARES_RenderBG_Props,
    ARES_OT_RenderBGApplyPreset,
    ARES_OT_RenderBGRender,
    ARES_PT_RenderBG,
)


def _safe_register(cls):
    with contextlib.suppress(RuntimeError):
        bpy.utils.register_class(cls)


def _safe_unregister(cls):
    with contextlib.suppress(RuntimeError):
        bpy.utils.unregister_class(cls)


def register():
    for c in CLASSES:
        _safe_register(c)
    # PointerProperty après l'enregistrement du PropertyGroup
    if not hasattr(bpy.types.Scene, "ares_renderbg"):
        bpy.types.Scene.ares_renderbg = PointerProperty(type=ARES_RenderBG_Props)


def unregister():
    # Supprimer le pointeur de Scene si présent
    if hasattr(bpy.types.Scene, "ares_renderbg"):
        with contextlib.suppress(Exception):
            del bpy.types.Scene.ares_renderbg
    for c in reversed(CLASSES):
        _safe_unregister(c)
