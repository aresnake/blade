import bpy

from ares.blender.render import RenderPreset, render_turntable
from ares.core.paths import ROOT
from ares.modules.asset_core.api import quick_export_glb


class ARES_OT_TurntableQuick(bpy.types.Operator):
    bl_idname = "ares.turntable_quick"
    bl_label = "Turntable (720p)"

    seconds: bpy.props.IntProperty(name="Seconds", default=8, min=1, max=60)
    fps: bpy.props.IntProperty(name="FPS", default=25, min=1, max=120)

    def execute(self, ctx):
        obj = ctx.active_object
        if not obj:
            self.report({"ERROR"}, "No active object")
            return {"CANCELLED"}
        render_turntable(obj, RenderPreset(res_x=1280, res_y=720, fps=self.fps), seconds=self.seconds)
        self.report({"INFO"}, "Turntable started")
        return {"FINISHED"}

class ARES_OT_ExportGLB(bpy.types.Operator):
    bl_idname = "ares.export_glb"
    bl_label = "Export .glb (selected)"

    def execute(self, ctx):
        obj = ctx.active_object
        if not obj:
            self.report({"ERROR"}, "No active object")
            return {"CANCELLED"}
        out = (ROOT / "renders" / "exports" / f"{obj.name}.glb")
        out.parent.mkdir(parents=True, exist_ok=True)
        quick_export_glb(obj, out)
        self.report({"INFO"}, f"Exported: {out}")
        return {"FINISHED"}

class ARES_PT_Tools(bpy.types.Panel):
    bl_label = "ARES Tools"
    bl_idname = "ARES_PT_tools"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "ARES"

    def draw(self, ctx):
        col = self.layout.column(align=True)
        col.operator("ares.turntable_quick", icon="RENDER_ANIMATION", text="Turntable (720p)")
        col.operator("ares.export_glb", icon="EXPORT", text="Export .glb")

def register():
    bpy.utils.register_class(ARES_OT_TurntableQuick)
    bpy.utils.register_class(ARES_OT_ExportGLB)
    bpy.utils.register_class(ARES_PT_Tools)

def unregister():
    bpy.utils.unregister_class(ARES_PT_Tools)
    bpy.utils.unregister_class(ARES_OT_ExportGLB)
    bpy.utils.unregister_class(ARES_OT_TurntableQuick)
