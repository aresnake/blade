"""
Turntable rig (ARES/Blade V13)
- Empty TT_Rig following a NURBS circle TT_Path via Follow Path
- Camera parented to TT_Rig (radius, 0, height)
- Track To (TRACK_NEGATIVE_Z, UP_Y) targeting TT_Target
- Animate curve.data.eval_time (no need for use_fixed_position on Blender 4.5)
- Render engine: BLENDER_EEVEE
- Data API only (no bpy.ops)
"""
import contextlib
import math

import bpy


def ensure_collection(name: str):
    col = bpy.data.collections.get(name)
    if not col:
        col = bpy.data.collections.new(name)
        bpy.context.scene.collection.children.link(col)
    return col


def link_object(obj, collection=None):
    col = collection or bpy.context.scene.collection
    if obj.name not in col.objects:
        col.objects.link(obj)
    return obj


def new_empty(name, location=(0.0, 0.0, 0.0)):
    obj = bpy.data.objects.new(name, None)
    obj.location = location
    return obj


def new_camera(name, location=(0.0, 0.0, 0.0)):
    cam_data = bpy.data.cameras.new(name + "_data")
    cam = bpy.data.objects.new(name, cam_data)
    cam.location = location
    return cam


def new_nurbs_circle_path(name, radius=5.0):
    curve = bpy.data.curves.new(name + "_data", type="CURVE")
    curve.dimensions = "3D"
    curve.resolution_u = 64

    spline = curve.splines.new("NURBS")
    n = 8
    spline.points.add(n - 1)
    step = 2.0 * math.pi / n
    for i in range(n):
        ang = i * step
        x = radius * math.cos(ang)
        y = radius * math.sin(ang)
        spline.points[i].co = (x, y, 0.0, 1.0)
    spline.use_cyclic_u = True
    spline.order_u = 3

    curve.use_path = True
    curve.path_duration = 240

    obj = bpy.data.objects.new(name, curve)
    return obj


def set_render_engine(scene, engine="BLENDER_EEVEE"):
    from contextlib import suppress
    with suppress(Exception):
        scene.render.engine = engine


def create_turntable(scene=None, *, radius=6.0, height=2.0, path_duration=240, fps=24):
    scene = scene or bpy.context.scene
    set_render_engine(scene, "BLENDER_EEVEE")

    rig_col = ensure_collection("TT_Rig_Collection")

    target = link_object(new_empty("TT_Target", (0.0, 0.0, 0.0)), rig_col)
    path = link_object(new_nurbs_circle_path("TT_Path", radius=radius), rig_col)
    curve = path.data
    curve.path_duration = int(path_duration)

    rig = link_object(new_empty("TT_Rig", (radius, 0.0, height)), rig_col)
    follow = rig.constraints.new("FOLLOW_PATH")
    follow.target = path
    # Blender 4.5 may not expose use_fixed_position; we don't need it since we animate eval_time.
    with contextlib.suppress(Exception):
        follow.use_fixed_position = False

    cam = link_object(new_camera("TT_Camera", (radius, 0.0, height)), rig_col)
    cam.parent = rig
    tr = cam.constraints.new("TRACK_TO")
    tr.target = target
    tr.track_axis = "TRACK_NEGATIVE_Z"
    tr.up_axis = "UP_Y"

    scene.frame_start = 1
    scene.frame_end = int(path_duration)
    scene.render.fps = int(fps)

    curve.eval_time = 0.0
    curve.keyframe_insert(data_path="eval_time", frame=1)
    curve.eval_time = float(path_duration)
    curve.keyframe_insert(data_path="eval_time", frame=scene.frame_end)

    with contextlib.suppress(Exception):
        scene.camera = cam

    return {
        "objects": {"target": target, "path": path, "rig": rig, "camera": cam},
        "settings": {
            "engine": scene.render.engine,
            "fps": scene.render.fps,
            "frame_start": scene.frame_start,
            "frame_end": scene.frame_end,
            "path_duration": curve.path_duration,
        },
    }




