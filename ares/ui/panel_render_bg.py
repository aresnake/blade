# SPDX-License-Identifier: MIT
# Path: ares/ui/panel_render_bg.py

import contextlib
import importlib

import bpy
from bpy.props import IntProperty, PointerProperty, StringProperty

from ares.modules.render_bg import preset as PR
from ares.modules.render_bg import turntable_rig as TR

importlib.reload(PR)
importlib.reload(TR)


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

class ARES_OT_RenderBGCreateTurntable(bpy.types.Operator):
    """Nettoie ancien rig, supprime Cam/Light du New, crée Cube+Sun, puis rig (cible=Cube)."""
    bl_idname = "ares.render_bg_create_turntable"
    bl_label = "Create Turntable"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        scn = context.scene
        ui = getattr(scn, "ares_renderbg", None)
        fps = int(ui.fps) if ui and ui.fps else int(scn.render.fps or 24)
        seconds = int(ui.seconds) if ui and ui.seconds else 4
        radius = float(ui.radius) if ui else 5.0
        cam_z = float(ui.camera_z) if ui else 5.0

        # 1) Cleanup ancien rig + éléments par défaut du New
        TR.cleanup_turntable(preserve_demo=False)
        TR.cleanup_new_scene_elements()

        # 2) Demo scene (Cube + Sun)
        cube = TR.make_demo_cube_sun()

        # 3) Crée rig en ciblant le Cube (TrackTo + DOF)
        info = TR.create_turntable(
            scn,
            seconds=seconds,
            fps=fps,
            radius=radius,
            camera_height=cam_z,
            focus_obj=cube,
        )
        self.report({"INFO"}, f"Turntable OK ({info['frames']}) • r={radius} • z={cam_z}")
        return {"FINISHED"}


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
    """Render de l'animation complète (frame_start→frame_end)."""
    bl_idname = "ares.render_bg_render_mp4"
    bl_label = "Render MP4"
    bl_options = {"REGISTER"}

    def execute(self, context):
        bpy.ops.render.render(animation=True)
        self.report({"INFO"}, "Render MP4 terminé")
        return {"FINISHED"}


class ARES_OT_RenderBGRenderQuick(bpy.types.Operator):
    """Render rapide ~1 seconde (utile pour les tests)."""
    bl_idname = "ares.render_bg_render_quick"
    bl_label = "Render Preview (1s)"
    bl_options = {"REGISTER"}

    def execute(self, context):
        scn = context.scene
        fps = max(1, int(scn.render.fps))
        orig_end = scn.frame_end
        scn.frame_end = scn.frame_start + fps - 1
        try:
            bpy.ops.render.render(animation=True)
        finally:
            scn.frame_end = orig_end
        self.report({"INFO"}, "Preview 1s terminé")
        return {"FINISHED"}


class ARES_OT_RenderBGRenderStill(bpy.types.Operator):
    """Render d'une seule image — force temporairement PNG puis restaure."""
    bl_idname = "ares.render_bg_render_still"
    bl_label = "Render Still"
    bl_options = {"REGISTER"}

    def execute(self, context):
        scn = context.scene
        r = scn.render
        prev_fmt = r.image_settings.file_format
        prev_fp = r.filepath
        # Forcer PNG si format vidéo (FFMPEG)
        if r.image_settings.file_format == "FFMPEG":
            r.image_settings.file_format = "PNG"
            if not prev_fp or prev_fp.lower().endswith(".mp4"):
                r.filepath = "//renders/still.png"
        try:
            bpy.ops.render.render(write_still=True)
        finally:
            r.image_settings.file_format = prev_fmt
            r.filepath = prev_fp
        self.report({"INFO"}, "Still PNG OK")
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
        row = col.row(align=True)
        row.prop(ui, "radius")
        row.prop(ui, "camera_z")

        layout.separator()
        row = layout.row(align=True)
        row.operator("ares.render_bg_create_turntable", icon="OUTLINER_OB_CAMERA")
        row.operator("ares.render_bg_apply_preset", icon="SETTINGS")
        row = layout.row(align=True)
        row.operator("ares.render_bg_render_still", icon="RENDER_STILL")
        row.operator("ares.render_bg_render_quick", icon="RENDER_ANIMATION")
        row = layout.row(align=True)
        row.operator("ares.render_bg_render_mp4", icon="RENDER_ANIMATION")


# --- Registration --------------------------------------------------------------

CLASSES = (
    ARES_RenderBG_Props,
    ARES_OT_RenderBGCreateTurntable,
    ARES_OT_RenderBGApplyPreset,
    ARES_OT_RenderBGRender,
    ARES_OT_RenderBGRenderQuick,
    ARES_OT_RenderBGRenderStill,
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
    if not hasattr(bpy.types.Scene, "ares_renderbg"):
        bpy.types.Scene.ares_renderbg = PointerProperty(type=ARES_RenderBG_Props)


def unregister():
    if hasattr(bpy.types.Scene, "ares_renderbg"):
        with contextlib.suppress(Exception):
            del bpy.types.Scene.ares_renderbg
    for c in reversed(CLASSES):
        _safe_unregister(c)





