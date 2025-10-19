# ARES / Blade — __init__.py (Lot 1: safe cleanup)
# - Imports at top (fix E402)
# - No callable defaults (fix B008)
# - contextlib.suppress instead of try/except/pass (fix SIM105)
# - Remove unused locals (fix F841)
# - No behavior change intended.

from __future__ import annotations

import contextlib
from collections.abc import Iterable, Sequence
from math import pi

import bmesh
import bpy
from mathutils import Vector

__all__ = [
    "__version__",
    "ensure_world_settings",
    "link_object",
    "make_mesh_object",
    "make_box",
    "make_uvsphere",
    "make_curve_circle",
    "build_turntable",
]

__version__ = "13.0.0-test"


# ----------------------------- Core helpers ---------------------------------


def link_object(
    obj: bpy.types.Object,
    collection: bpy.types.Collection | None = None,
) -> bpy.types.Object:
    """Link an object to the active scene collection if not provided, and return it."""
    col = collection or bpy.context.scene.collection
    if obj.name not in col.objects:
        col.objects.link(obj)
    return obj


def make_mesh_object(
    name: str,
    verts: Sequence[Vector],
    faces: Sequence[Sequence[int]],
) -> bpy.types.Object:
    """Create a mesh datablock from verts/faces arrays and return the new object."""
    me = bpy.data.meshes.new(name + "_mesh")
    me.from_pydata(verts, [], faces)
    me.update()
    obj = bpy.data.objects.new(name, me)
    return link_object(obj)


def make_box(name: str, size: float = 1.0, center: Vector | None = None) -> bpy.types.Object:
    """Axis-aligned box, centered on `center` with full edge length = `size`."""
    c = center if center is not None else Vector((0.0, 0.0, 0.0))
    s = size * 0.5
    v = [
        c + Vector((-s, -s, -s)), c + Vector((+s, -s, -s)),
        c + Vector((+s, +s, -s)), c + Vector((-s, +s, -s)),
        c + Vector((-s, -s, +s)), c + Vector((+s, -s, +s)),
        c + Vector((+s, +s, +s)), c + Vector((-s, +s, +s)),
    ]
    f = [
        [0, 1, 2, 3],  # bottom
        [4, 5, 6, 7],  # top
        [0, 1, 5, 4],  # sides
        [1, 2, 6, 5],
        [2, 3, 7, 6],
        [3, 0, 4, 7],
    ]
    return make_mesh_object(name, v, f)


def make_uvsphere(
    name: str,
    radius: float = 0.2,
    segments: int = 16,
    rings: int = 8,
    center: Vector | None = None,
) -> bpy.types.Object:
    """UV sphere (bmesh) centered on `center` with given radius."""
    c = center if center is not None else Vector((0.0, 0.0, 0.0))
    me = bpy.data.meshes.new(name + "_mesh")
    bm = bmesh.new()
    try:
        bmesh.ops.create_uvsphere(
            bm, u_segments=segments, v_segments=rings, radius=radius
        )
        bm.to_mesh(me)
    finally:
        bm.free()
    obj = bpy.data.objects.new(name, me)
    obj.location = c
    return link_object(obj)


def make_curve_circle(name: str, radius: float = 2.5) -> bpy.types.Object:
    """Create a NURBS circle curve used as a path (turntable orbit)."""
    curve = bpy.data.curves.new(name=name + "_curve", type="CURVE")
    curve.dimensions = "3D"
    curve.resolution_u = 64
    spl = curve.splines.new(type="NURBS")
    spl.points.add(7)  # 8 points total
    pts = [
        Vector((+radius, 0.0, 0.0, 1.0)),
        Vector((0.0, +radius, 0.0, 1.0)),
        Vector((-radius, 0.0, 0.0, 1.0)),
        Vector((0.0, -radius, 0.0, 1.0)),
        Vector((+radius, 0.0, 0.0, 1.0)),
        Vector((0.0, +radius, 0.0, 1.0)),
        Vector((-radius, 0.0, 0.0, 1.0)),
        Vector((0.0, -radius, 0.0, 1.0)),
    ]
    for i, p in enumerate(pts):
        spl.points[i].co = p
    spl.order_u = 4
    spl.use_endpoint_u = True
    obj = bpy.data.objects.new(name, curve)
    return link_object(obj)


# --------------------------- Scene / world setup -----------------------------


def ensure_world_settings() -> bpy.types.Scene:
    """Ensure minimal Eevee settings for previews; ignore missing props safely."""
    scene = bpy.context.scene
    with contextlib.suppress(Exception):
        scene.render.engine = "BLENDER_EEVEE"
    # Some Eevee props may be absent in certain builds; suppress instead of try/except/pass
    with contextlib.suppress(Exception):
        scene.eevee.use_bloom = True
    with contextlib.suppress(Exception):
        scene.eevee.shadow_cube_size = "1024"
    with contextlib.suppress(Exception):
        scene.eevee.use_gtao = True
    return scene


# ------------------------------- Turntable -----------------------------------


def build_turntable(radius: float = 3.0, cam_height: float = 1.6, fov_deg: float = 50.0) -> dict:
    """Create a basic turntable rig (path + rig empty + camera with Track To)."""
    scn = ensure_world_settings()

    path = bpy.data.objects.get("TT_Path") or make_curve_circle("TT_Path", radius=radius)
    rig = bpy.data.objects.get("TT_Rig")
    if rig is None:
        rig = bpy.data.objects.new("TT_Rig", None)
        link_object(rig)
        rig.empty_display_size = 0.3
        rig.empty_display_type = "SPHERE"

    # Camera
    cam_data = bpy.data.cameras.get("TT_Camera") or bpy.data.cameras.new("TT_Camera")
    cam_obj = bpy.data.objects.get("TT_Camera") or bpy.data.objects.new("TT_Camera", cam_data)
    link_object(cam_obj)
    cam_obj.location = (radius, 0.0, cam_height)
    with contextlib.suppress(Exception):
        cam_data.lens_unit = "FOV"
        cam_data.angle = pi * fov_deg / 180.0

    # Parenting and constraints
    cam_obj.parent = rig
    with contextlib.suppress(Exception):
        tr = cam_obj.constraints.get("Track To") or cam_obj.constraints.new(type="TRACK_TO")
        tr.target = path
        tr.track_axis = "TRACK_NEGATIVE_Z"
        tr.up_axis = "UP_Y"

    # Follow Path on rig
    with contextlib.suppress(Exception):
        fp = rig.constraints.get("Follow Path") or rig.constraints.new(type="FOLLOW_PATH")
        fp.target = path
        fp.use_fixed_location = False

    # Animate path via eval_time (frame 1..250 by default)
    scn.frame_start, scn.frame_end = 1, 250
    path.data.path_duration = (scn.frame_end - scn.frame_start) + 1
    path.data.use_path = True
    path.data.use_path_follow = True
    path.data.eval_time = scn.frame_start
    path.data.keyframe_insert(data_path="eval_time", frame=scn.frame_start)
    path.data.eval_time = scn.frame_end
    path.data.keyframe_insert(data_path="eval_time", frame=scn.frame_end)

    with contextlib.suppress(Exception):
        scn.camera = cam_obj

    return {
        "objects": {"path": path, "rig": rig, "camera": cam_obj},
        "settings": {"radius": radius, "height": cam_height, "fov_deg": fov_deg},
    }
