# ares/modules/turntable_gen.py
import contextlib

import bpy

from ares import link_object, make_curve_circle


def set_render_engine(scene: bpy.types.Scene, engine: str = "BLENDER_EEVEE"):
    with contextlib.suppress(Exception):
        scene.render.engine = engine


def create_turntable(radius: float = 2.5, cam_height: float = 1.6):
    """Generate a minimal turntable rig and return its components."""
    scene = bpy.context.scene
    path = bpy.data.objects.get("TT_Path") or make_curve_circle("TT_Path", radius=radius)
    rig_col = scene.collection

    rig = bpy.data.objects.get("TT_Rig") or bpy.data.objects.new("TT_Rig", None)
    link_object(rig, rig_col)

    cam_data = bpy.data.cameras.new("TT_Camera")
    cam = link_object(bpy.data.objects.new("TT_Camera", cam_data), rig_col)
    cam.location = (radius, 0.0, cam_height)
    cam.parent = rig

    with contextlib.suppress(Exception):
        follow = rig.constraints.get("Follow Path") or rig.constraints.new(type="FOLLOW_PATH")
        follow.target = path
        follow.use_fixed_location = False

    with contextlib.suppress(Exception):
        track = cam.constraints.get("Track To") or cam.constraints.new(type="TRACK_TO")
        track.target = path
        track.track_axis = "TRACK_NEGATIVE_Z"
        track.up_axis = "UP_Y"

    # Animate curve
    curve = path.data
    curve.path_duration = 90
    curve.use_path = True
    curve.use_path_follow = True
    curve.eval_time = 1
    curve.keyframe_insert(data_path="eval_time", frame=1)
    curve.eval_time = 90
    curve.keyframe_insert(data_path="eval_time", frame=90)

    with contextlib.suppress(Exception):
        scene.camera = cam

    return {"objects": {"path": path, "rig": rig, "camera": cam}}
