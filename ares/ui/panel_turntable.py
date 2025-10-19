# ares/ui/panel_turntable.py
import contextlib

import bpy


def safe_register(cls):
    with contextlib.suppress(Exception):
        bpy.utils.unregister_class(cls)
    with contextlib.suppress(ValueError):
        bpy.utils.register_class(cls)


def safe_unregister(cls):
    with contextlib.suppress(Exception):
        bpy.utils.unregister_class(cls)


class ARES_PT_Turntable(bpy.types.Panel):
    bl_label = "ARES Turntable"
    bl_idname = "ARES_PT_Turntable"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "ARES"

    def draw(self, context):
        layout = self.layout
        layout.operator("ares.create_turntable", icon="CAMERA_DATA")


class ARES_OT_CreateTurntable(bpy.types.Operator):
    bl_idname = "ares.create_turntable"
    bl_label = "Create Turntable"
    bl_description = "Create a simple turntable rig for the active object"

    def execute(self, context):
        try:
            import ares.modules.turntable_gen as T
            T.create_turntable()
            with contextlib.suppress(Exception):
                T.set_render_engine(context, "BLENDER_EEVEE_NEXT")
            return {"FINISHED"}
        except Exception as e:
            self.report({"ERROR"}, f"ARES: {e}")
            return {"CANCELLED"}


def register():
    safe_register(ARES_PT_Turntable)
    safe_register(ARES_OT_CreateTurntable)


def unregister():
    safe_unregister(ARES_PT_Turntable)
    safe_unregister(ARES_OT_CreateTurntable)
