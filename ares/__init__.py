bl_info = {
    "name":        "Blade v13 (ARES)",
    "author":      "Adrien / ARES",
    "version":     (0, 1, 0),
    "blender":     (4, 0, 0),
    "location":    "3D Viewport > N-panel > Blade v13",
    "description": "Turntable, low-poly dog, rendu background (demo)",
    "category":    "3D View"
}

__version__ = "0.1.0"

# --- Addon wiring ---
import bpy

from .modules.turntable import render_turntable
from .modules.animals.simple import create_lowpoly_dog
from .modules.render_bg.render_bg import ensure_output_and_override

class ARES_OT_turntable_fast(bpy.types.Operator):
    bl_idname = "ares.turntable_fast"
    bl_label = "Turntable FAST"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, ctx):
        path = bpy.path.abspath("//renders/ui_turntable_fast.mp4")
        render_turntable(radius=2.2, seconds=0.75, fps=24, mp4_path=path, samples=16)
        self.report({"INFO"}, f"Turntable: {path}")
        return {"FINISHED"}

class ARES_OT_spawn_dog(bpy.types.Operator):
    bl_idname = "ares.spawn_dog"
    bl_label = "Spawn Dog (low-poly)"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, ctx):
        create_lowpoly_dog()
        self.report({"INFO"}, "Dog spawned")
        return {"FINISHED"}

class ARES_OT_render_bg_demo(bpy.types.Operator):
    bl_idname = "ares.render_bg_demo"
    bl_label = "Render BG (demo 5 frames)"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, ctx):
        scene = bpy.context.scene
        # presets par défaut (mp4 H264/AAC) + out path
        ensure_output_and_override(scene, {
            "file_format": "FFMPEG",
            "filepath": "//renders/ui_demo.mp4",
            "ffmpeg": {"format": "MPEG4", "codec": "H264", "preset": "GOOD", "crf": "MEDIUM", "audio_codec": "AAC"}
        })
        # frames courtes
        scene.frame_start = 1
        scene.frame_end   = 5
        bpy.ops.render.render(animation=True)
        self.report({"INFO"}, "Render BG demo done")
        return {"FINISHED"}

class ARES_PT_panel(bpy.types.Panel):
    bl_label = "Blade v13"
    bl_idname = "ARES_PT_panel"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Blade v13"

    def draw(self, ctx):
        col = self.layout.column(align=True)
        col.operator("ares.turntable_fast", icon="FILE_VIDEO")
        col.operator("ares.spawn_dog", icon="MESH_MONKEY")
        col.operator("ares.render_bg_demo", icon="RENDER_ANIMATION")

CLASSES = (
    ARES_OT_turntable_fast,
    ARES_OT_spawn_dog,
    ARES_OT_render_bg_demo,
    ARES_PT_panel,
)

def register():
    for c in CLASSES:
        bpy.utils.register_class(c)

def unregister():
    for c in reversed(CLASSES):
        bpy.utils.unregister_class(c)
