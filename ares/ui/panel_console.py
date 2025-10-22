# ARES v13 — UI minimale : panneau + bouton "Render Turntable (demo)"
from __future__ import annotations

try:
    import bpy  # type: ignore
except Exception as e:
    raise RuntimeError("Ce module UI doit être chargé depuis Blender.") from e

from bpy.props import IntProperty, StringProperty
from bpy.types import Operator, Panel


# Import tardif pour éviter les erreurs si Blender n'est pas chargé
def _render_demo(out_path: str, seconds: int, fps: int, res_x: int, res_y: int) -> str:
    from ares.core import render_bg as rb
    return rb.demo_turntable_mp4(
        out_path=out_path,
        seconds=seconds,
        fps=fps,
        res=(res_x, res_y),
    )

class ARES_OT_render_turntable(Operator):
    bl_idname = "ares.render_turntable_demo"
    bl_label = "Render Turntable (Demo)"
    bl_description = "Rend une courte turntable en MP4 (headless-safe)"

    seconds: IntProperty(name="Seconds", default=1, min=1, max=60)
    fps:     IntProperty(name="FPS", default=24, min=1, max=120)
    res_x:   IntProperty(name="Res X", default=640, min=160, max=7680)
    res_y:   IntProperty(name="Res Y", default=360, min=120, max=4320)
    out_path: StringProperty(name="Output", default="//renders/demo_tt.mp4", subtype='FILE_PATH')

    def execute(self, context):
        # Résout // vers un chemin absolu dans le blend courant
        out_abs = bpy.path.abspath(self.out_path)
        try:
            final = _render_demo(out_abs, self.seconds, self.fps, self.res_x, self.res_y)
            self.report({'INFO'}, f"Rendered: {final}")
            return {'FINISHED'}
        except Exception as e:
            self.report({'ERROR'}, str(e))
            return {'CANCELLED'}

class ARES_PT_panel_console(Panel):
    bl_label = "ARES — Core LTS"
    bl_idname = "ARES_PT_panel_console"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "ARES"

    def draw(self, context):
        col = self.layout.column(align=True)
        col.label(text="Render Turntable (Demo)")
        op = col.operator("ares.render_turntable_demo", text="Render (MP4)")
        # Valeurs par défaut pratiques
        op.seconds = 1
        op.fps = 24
        op.res_x = 640
        op.res_y = 360
        op.out_path = "//renders/demo_tt.mp4"

CLASSES = (ARES_OT_render_turntable, ARES_PT_panel_console)

def register():
    for cls in CLASSES:
        bpy.utils.register_class(cls)

def unregister():
    for cls in reversed(CLASSES):
        bpy.utils.unregister_class(cls)
