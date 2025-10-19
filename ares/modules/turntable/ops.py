import bpy

from ares.blender.render import RenderPreset, render_turntable


class ARES_OT_Turntable(bpy.types.Operator):
    bl_idname = "ares.turntable_quick"
    bl_label = "Render Turntable (720p)"
    bl_options = {"REGISTER"}

    def execute(self, context):
        obj = context.active_object
        if obj is None:
            self.report({"ERROR"}, "No active object")
            return {"CANCELLED"}
        try:
            render_turntable(obj, RenderPreset())
            self.report({"INFO"}, "Turntable en cours (stub)")
            return {"FINISHED"}
        except Exception as e:
            self.report({"ERROR"}, str(e))
            return {"CANCELLED"}

def register():
    bpy.utils.register_class(ARES_OT_Turntable)

def unregister():
    bpy.utils.unregister_class(ARES_OT_Turntable)
