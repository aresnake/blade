"""
ARES Turntable Panel
--------------------
UI panel providing quick access to the stable turntable render
through ares.core.turntable (shim layer).
"""

import bpy
from bpy.props import IntProperty, PointerProperty
from bpy.types import Operator, Panel, PropertyGroup

# Import stable shim (core)
from ares.core import turntable as tt


# ------------------------------------------------------------------------
# Properties
# ------------------------------------------------------------------------
class ARES_PT_TurntableProps(PropertyGroup):
    seconds: IntProperty(
        name="Duration (s)",
        default=4,
        min=1,
        description="Number of seconds for the turntable render",
    )
    fps: IntProperty(
        name="FPS",
        default=24,
        min=1,
        description="Frames per second",
    )


# ------------------------------------------------------------------------
# Operator
# ------------------------------------------------------------------------
class ARES_OT_RenderTurntable(Operator):
    """Render a short turntable animation of the active object"""

    bl_idname = "ares.render_turntable"
    bl_label = "Render Turntable"
    bl_options = {"REGISTER"}

    def execute(self, context):
        obj = context.active_object
        if obj is None:
            self.report({"WARNING"}, "No active object to render")
            return {"CANCELLED"}

        props = context.scene.ares_turntable
        fps = props.fps
        seconds = props.seconds

        # Output path
        import os
        base_dir = bpy.path.abspath("//renders")
        os.makedirs(base_dir, exist_ok=True)
        out_path = os.path.join(base_dir, "turntable_ui.mp4")

        # Create preset
        preset = tt.RenderPreset(res_x=1280, res_y=720, fps=fps, samples=32)

        # Ensure rig/collection exist
        tt.create_turntable_rig(radius=3.0)

        # Run render
        self.report({"INFO"}, f"Rendering turntable ({seconds}s @ {fps}fps)")
        tt.render_turntable(
            target=obj,
            radius=3.0,
            seconds=seconds,
            fps=fps,
            mp4_path=out_path,
            samples=32,
            preset=preset,
        )

        self.report({"INFO"}, f"Saved to: {out_path}")
        return {"FINISHED"}


# ------------------------------------------------------------------------
# Panel
# ------------------------------------------------------------------------
class ARES_PT_TurntablePanel(Panel):
    """ARES Turntable Control Panel"""

    bl_label = "ARES Turntable"
    bl_idname = "ARES_PT_TurntablePanel"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "ARES Tools"

    def draw(self, context):
        layout = self.layout
        props = context.scene.ares_turntable

        col = layout.column(align=True)
        col.prop(props, "seconds")
        col.prop(props, "fps")

        layout.operator("ares.render_turntable", icon="RENDER_ANIMATION")


# ------------------------------------------------------------------------
# Registration
# ------------------------------------------------------------------------
classes = (
    ARES_PT_TurntableProps,
    ARES_OT_RenderTurntable,
    ARES_PT_TurntablePanel,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Scene.ares_turntable = PointerProperty(type=ARES_PT_TurntableProps)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
    del bpy.types.Scene.ares_turntable


if __name__ == "__main__":
    register()
