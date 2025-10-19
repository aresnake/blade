# ARES Turntable UI (clean rewrite)
# - safe_register / safe_unregister pour éviter les warnings headless
# - Panel simple + opérateur pour créer un turntable via ares.modules.turntable_gen

import bpy


# --- Safe (un)register helpers ------------------------------------------------
def safe_register(cls):
    try:
        bpy.utils.unregister_class(cls)
    except Exception:
        pass
    try:
        bpy.utils.register_class(cls)
    except ValueError:
        # déjà présent ou état incohérent -> ignorer
        pass

def safe_unregister(cls):
    try:
        bpy.utils.unregister_class(cls)
    except Exception:
        pass

# --- Operator -----------------------------------------------------------------
class ARES_OT_CreateTurntable(bpy.types.Operator):
    bl_idname = "ares.create_turntable"
    bl_label = "Create Turntable"
    bl_description = "Create a quick turntable rig in the current scene"

    def execute(self, context):
        try:
            import sys
            if r'D:\V13\workspace_v13' not in sys.path:
                # En headless nos tests ajoutent ce path; en GUI mieux vaut être tolérant
                sys.path.append(r'D:\V13\workspace_v13')
            import ares.modules.turntable_gen as T
            T.create_turntable()
            try:
                T.set_render_engine(context, 'BLENDER_EEVEE_NEXT')
            except Exception:
                pass
        except Exception as e:
            self.report({'ERROR'}, f"ARES: {e}")
            return {'CANCELLED'}
        return {'FINISHED'}

# --- Panel --------------------------------------------------------------------
class ARES_PT_Turntable(bpy.types.Panel):
    bl_idname = "ARES_PT_Turntable"
    bl_label = "ARES • Turntable"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "ARES"

    def draw(self, context):
        layout = self.layout
        col = layout.column(align=True)
        col.operator("ares.create_turntable", icon="FILE_MOVIE", text="Create Turntable")

# --- Addon registration -------------------------------------------------------
def register():
    # ordre: opérateur, puis panel
    safe_register(ARES_OT_CreateTurntable)
    safe_register(ARES_PT_Turntable)

def unregister():
    # ordre inverse
    safe_unregister(ARES_PT_Turntable)
    safe_unregister(ARES_OT_CreateTurntable)

if __name__ == "__main__":
    register()
