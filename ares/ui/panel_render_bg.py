from __future__ import annotations

import contextlib

import bpy


def _ensure_scene_settings(scn: bpy.types.Scene, fps: int, seconds: int, filepath: str):
    # Moteur Eevee (safe)
    with contextlib.suppress(Exception):
        scn.render.engine = "BLENDER_EEVEE"

    # Timeline
    scn.render.fps = fps
    scn.frame_start = 1
    scn.frame_end = max(1, fps * max(1, seconds))

    # Sortie vidéo MP4 / H.264
    scn.render.filepath = filepath
    scn.render.image_settings.file_format = "FFMPEG"
    scn.render.ffmpeg.format = "MPEG4"
    scn.render.ffmpeg.codec = "H264"
    scn.render.ffmpeg.constant_rate_factor = "MEDIUM"
    scn.render.ffmpeg.ffmpeg_preset = "GOOD"
    scn.render.ffmpeg.audio_codec = "AAC"
    scn.render.ffmpeg.audio_bitrate = 192000
    scn.render.ffmpeg.gopsize = 12
    # bitrate vidéo raisonnable
    scn.render.ffmpeg.video_bitrate = 8000
    scn.render.ffmpeg.maxrate = 12000


class ARES_OT_RenderBG(bpy.types.Operator):
    bl_idname = "ares.render_bg_mp4"
    bl_label = "Render MP4 (H.264)"
    bl_description = "Render animation to MP4 (H.264) with simple preset"

    filepath: bpy.props.StringProperty(
        name="Output",
        subtype="FILE_PATH",
        default="//renders/out.mp4",
    )
    seconds: bpy.props.IntProperty(name="Seconds", min=1, default=4)
    fps: bpy.props.IntProperty(name="FPS", min=1, default=24)

    def execute(self, context):
        scn = context.scene
        _ensure_scene_settings(scn, fps=self.fps, seconds=self.seconds, filepath=self.filepath)

        # Rendu animation
        with context.temp_override(area=None, region=None, window=None):
            bpy.ops.render.render(animation=True)

        self.report({"INFO"}, f"Rendered → {self.filepath}")
        return {"FINISHED"}

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self, width=420)


class ARES_PT_RenderBG(bpy.types.Panel):
    bl_label = "ARES Render BG"
    bl_idname = "ARES_PT_RenderBG"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "ARES"

    def draw(self, context):
        layout = self.layout
        col = layout.column(align=True)
        op = col.operator(ARES_OT_RenderBG.bl_idname, icon="RENDER_ANIMATION")
        op.filepath = "//renders/out.mp4"
        op.seconds = 4
        op.fps = 24


def register():
    for cls in (ARES_OT_RenderBG, ARES_PT_RenderBG):
        with contextlib.suppress(Exception):
            bpy.utils.unregister_class(cls)
        bpy.utils.register_class(cls)


def unregister():
    for cls in (ARES_PT_RenderBG, ARES_OT_RenderBG):
        with contextlib.suppress(Exception):
            bpy.utils.unregister_class(cls)
