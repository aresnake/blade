bl_info = {
    "name": "ARES Blade Panel",
    "author": "Adrien + ARES",
    "version": (0, 1, 0),
    "blender": (4, 5, 0),
    "location": "View3D > Sidebar (N) > ARES",
    "description": "Turntable FAST, Spawn Dog (placeholder), Render BG demo",
    "category": "3D View",
}

import bpy
import bmesh
from math import pi
from mathutils import Vector

# -----------------------------
# Helpers (data-first, no ops)
# -----------------------------

def link_object(obj, scene=None):
    scene = scene or bpy.context.scene
    if obj.name not in scene.collection.objects:
        scene.collection.objects.link(obj)
    return obj

def make_mesh_object(name, verts, faces):
    me = bpy.data.meshes.new(name + "_mesh")
    me.from_pydata(verts, [], faces)
    me.validate()
    me.update()
    obj = bpy.data.objects.new(name, me)
    return link_object(obj)

def make_box(name, size=1.0, center=Vector((0,0,0))):
    s = size * 0.5
    v = [
        center + Vector((-s,-s,-s)), center + Vector(( s,-s,-s)),
        center + Vector(( s, s,-s)), center + Vector((-s, s,-s)),
        center + Vector((-s,-s, s)), center + Vector(( s,-s, s)),
        center + Vector(( s, s, s)), center + Vector((-s, s, s)),
    ]
    f = [(0,1,2,3),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)]
    return make_mesh_object(name, v, f)

def make_uvsphere(name, radius=0.2, segments=16, rings=8, center=Vector((0,0,0))):
    me = bpy.data.meshes.new(name + "_mesh")
    bm = bmesh.new()
    bmesh.ops.create_uvsphere(
        bm, u_segments=segments, v_segments=rings, radius=radius
    )
    bmesh.ops.translate(bm, verts=bm.verts, vec=center)
    bm.to_mesh(me)
    bm.free()
    obj = bpy.data.objects.new(name, me)
    return link_object(obj)

def make_curve_circle(name="TT_Path", radius=3.0):
    # NURBS circle path for consistent Follow Path
    curve = bpy.data.curves.new(name, type='CURVE')
    curve.dimensions = '3D'
    spline = curve.splines.new('NURBS')
    spline.points.add(7)  # total 8 points
    coords = [
        ( radius, 0.0, 0.0, 1.0),
        ( 0.0,  radius, 0.0, 1.0),
        (-radius, 0.0, 0.0, 1.0),
        ( 0.0, -radius, 0.0, 1.0),
        ( radius, 0.0, 0.0, 1.0),
        ( 0.0,  radius, 0.0, 1.0),
        (-radius, 0.0, 0.0, 1.0),
        ( 0.0, -radius, 0.0, 1.0),
    ]
    for p, co in zip(spline.points, coords):
        p.co = co
        p.weight = 1.0
    spline.order_u = 4
    spline.use_endpoint_u = True
    obj = bpy.data.objects.new(name, curve)
    link_object(obj)
    curve.use_path = True
    curve.use_path_follow = True
    curve.eval_time = 0
    curve.path_duration = 250
    return obj

def ensure_world_settings(scene=None):
    scene = scene or bpy.context.scene
    from .helpers import engine as ares_engine
    ares_engine.ensure_engine(bpy, scene)
    try:
        scene.eevee.use_bloom = True
    except Exception:
        pass
    return scene

# ---------------------------------
# ARES Turntable (standard v2025-09-22)
# ---------------------------------

def build_turntable(radius=3.0, cam_height=1.6, fov_deg=50.0):
    scene = ensure_world_settings()
    path = bpy.data.objects.get("TT_Path") or make_curve_circle("TT_Path", radius=radius)
    rig = bpy.data.objects.get("TT_Rig")
    if not rig:
        rig = bpy.data.objects.new("TT_Rig", None)
        link_object(rig)
    cam = bpy.data.objects.get("TT_Cam")
    if not cam:
        cam_data = bpy.data.cameras.new("TT_Cam_data")
        cam = bpy.data.objects.new("TT_Cam", cam_data)
        link_object(cam)

    # position camera and parenting
    cam.location = (radius, 0.0, cam_height)
    cam.rotation_euler = (0.0, 0.0, pi)  # will be overridden by Track To
    cam.parent = rig

    # Follow Path constraint on rig
    c = rig.constraints.get("Follow Path") or rig.constraints.new(type='FOLLOW_PATH')
    c.target = path
    c.use_fixed_location = False

    # Track To constraint on camera (TRACK_NEGATIVE_Z, UP_Y)
    t = cam.constraints.get("Track To") or cam.constraints.new(type='TRACK_TO')
    t.target = rig
    t.track_axis = 'TRACK_NEGATIVE_Z'
    t.up_axis = 'UP_Y'

    # Path anim via curve.eval_time (user can keyframe)
    path.data.use_path = True
    path.data.path_duration = max(1, path.data.path_duration or 250)
    return {"path": path, "rig": rig, "cam": cam}

# -----------------------------
# Operators
# -----------------------------

class ARES_OT_turntable_fast(bpy.types.Operator):
    bl_idname = "ares.turntable_fast"
    bl_label = "Turntable FAST"
    bl_description = "Create standard ARES turntable rig (Path + Rig + Cam)"

    def execute(self, context):
        res = build_turntable(radius=3.0, cam_height=1.6)
        self.report({'INFO'}, f"Turntable ready: {', '.join(res.keys())}")
        return {'FINISHED'}

class ARES_OT_spawn_dog(bpy.types.Operator):
    bl_idname = "ares.spawn_dog"
    bl_label = "Spawn Dog (placeholder)"
    bl_description = "Spawn a simple placeholder dog (box+head+tail)"

    def execute(self, context):
        body = make_box("Dog_Body", size=1.0, center=Vector((0,0,0.5)))
        head = make_box("Dog_Head", size=0.5, center=Vector((0.6,0,0.9)))
        tail = make_uvsphere("Dog_Tail", radius=0.12, center=Vector((-0.6,0,0.9)))
        for o in (body, head, tail):
            o.display_type = 'TEXTURED'
        self.report({'INFO'}, "Spawned Dog placeholder")
        return {'FINISHED'}

class ARES_OT_render_bg(bpy.types.Operator):
    bl_idname = "ares.render_bg"
    bl_label = "Render BG (demo)"
    bl_description = "Quick render demo: set Eevee, 1920x1080, PNG to //renders/"

    def execute(self, context):
        scene = ensure_world_settings()
        scene.render.resolution_x = 1920
        scene.render.resolution_y = 1080
        scene.render.filepath = "//renders/ares_demo.png"
        scene.render.image_settings.file_format = 'PNG'
        # Trigger a normal render (foreground). For true background use CLI -b.
        try:
            bpy.ops.render.render('INVOKE_DEFAULT', write_still=True)
            self.report({'INFO'}, f"Render started → {scene.render.filepath}")
        except Exception as e:
            self.report({'WARNING'}, f"Render failed: {e}")
        return {'FINISHED'}

# -----------------------------
# UI Panel
# -----------------------------

class VIEW3D_PT_ares_panel(bpy.types.Panel):
    bl_label = "ARES"
    bl_idname = "VIEW3D_PT_ares_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "ARES"

    def draw(self, context):
        layout = self.layout
        col = layout.column(align=True)
        col.operator("ares.turntable_fast", icon='OUTLINER_OB_CAMERA')
        col.operator("ares.spawn_dog", icon='MESH_CUBE')
        col.separator()
        col.operator("ares.render_bg", icon='RENDER_STILL')

# -----------------------------
# Register
# -----------------------------

classes = (
    ARES_OT_turntable_fast,
    ARES_OT_spawn_dog,
    ARES_OT_render_bg,
    VIEW3D_PT_ares_panel,
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

if __name__ == "__main__":
    register()

__version__ = "13.0.0-test"