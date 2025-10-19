# SPDX-License-Identifier: MIT
# Path: ares/modules/render_bg/turntable_rig.py

from __future__ import annotations

from math import radians

import bpy

# ---------- Utils: collections / linking ----------

def _ensure_collection(name: str) -> bpy.types.Collection:
    coll = bpy.data.collections.get(name)
    if coll is None:
        coll = bpy.data.collections.new(name)
        bpy.context.scene.collection.children.link(coll)
    return coll


def _link_only_to_collection(obj: bpy.types.Object, collection: bpy.types.Collection) -> None:
    for c in list(obj.users_collection):
        c.objects.unlink(obj)
    if obj.name not in collection.objects:
        collection.objects.link(obj)


# ---------- Cleanup ----------

def cleanup_turntable(preserve_demo: bool = False) -> None:
    """Supprime l'ancien rig ARES_Turntable (pivot/carrier/camera/path/focus).
       Si preserve_demo=False, supprime aussi l'Empty focus ARES_Turntable_Focus.
    """
    names = {
        "coll": "ARES_Turntable",
        "path": "ARES_Turntable_Path",
        "pivot": "ARES_Turntable_Pivot",
        "carrier": "ARES_Turntable_Carrier",
        "camera": "ARES_Turntable_Camera",
        "focus": "ARES_Turntable_Focus",
    }

    coll = bpy.data.collections.get(names["coll"])
    if coll:
        for parent in list(coll.users_scene):
            parent.collection.children.unlink(coll)
        for obj in list(coll.objects):
            bpy.data.objects.remove(obj, do_unlink=True)
        bpy.data.collections.remove(coll)

    for key in ("path", "pivot", "carrier", "camera"):
        obj = bpy.data.objects.get(names[key])
        if obj:
            bpy.data.objects.remove(obj, do_unlink=True)

    if not preserve_demo:
        foc = bpy.data.objects.get(names["focus"])
        if foc:
            bpy.data.objects.remove(foc, do_unlink=True)


def cleanup_new_scene_elements() -> None:
    """Supprime les éléments du fichier New Blender: Camera/Light par défaut."""
    for name in ("Camera", "Light"):
        obj = bpy.data.objects.get(name)
        if obj:
            bpy.data.objects.remove(obj, do_unlink=True)


# ---------- Demo scene (Cube + Sun) ----------

def make_demo_cube_sun() -> bpy.types.Object:
    """Crée un cube (origine) et un Sun, renvoie le cube (pour DOF/TrackTo)."""
    cube = bpy.data.objects.get("Cube")
    if cube is None:
        bpy.ops.mesh.primitive_cube_add(size=2.0, location=(0.0, 0.0, 0.0))
        cube = bpy.context.active_object
        cube.name = "Cube"
    else:
        cube.location = (0.0, 0.0, 0.0)

    sun = bpy.data.lights.get("ARES_Sun")
    if sun is None:
        sun = bpy.data.lights.new(name="ARES_Sun", type="SUN")
    sun.energy = 3.0
    sun_obj = bpy.data.objects.get("ARES_Sun")
    if sun_obj is None:
        sun_obj = bpy.data.objects.new("ARES_Sun", sun)
        bpy.context.scene.collection.objects.link(sun_obj)
    sun_obj.location = (8.0, -6.0, 6.0)
    sun_obj.rotation_euler = (radians(45), 0.0, radians(30))

    return cube


# ---------- Rig building ----------

def _add_circle_path(radius: float, collection: bpy.types.Collection) -> bpy.types.Object:
    bpy.ops.curve.primitive_bezier_circle_add(radius=radius, location=(0.0, 0.0, 0.0))
    circle = bpy.context.active_object
    circle.name = "ARES_Turntable_Path"
    circle.data.use_path = True
    _link_only_to_collection(circle, collection)
    return circle


def _add_empty(name: str, collection: bpy.types.Collection, loc=(0.0, 0.0, 0.0)) -> bpy.types.Object:
    bpy.ops.object.empty_add(type="PLAIN_AXES", location=loc)
    empty = bpy.context.active_object
    empty.name = name
    _link_only_to_collection(empty, collection)
    return empty


def _add_camera(local_height: float, collection: bpy.types.Collection) -> bpy.types.Object:
    bpy.ops.object.camera_add(location=(0.0, 0.0, local_height), rotation=(0.0, 0.0, 0.0))
    cam = bpy.context.active_object
    cam.name = "ARES_Turntable_Camera"
    _link_only_to_collection(cam, collection)
    return cam


def _choose_focus_object(scene: bpy.types.Scene) -> bpy.types.Object:
    """Active > Cube > Empty focus au centre."""
    obj: bpy.types.Object | None = None
    obj = getattr(bpy.context, "active_object", None) or obj
    try:
        obj = scene.view_layers[0].objects.active or obj
    except Exception:
        pass
    if obj is None:
        obj = bpy.data.objects.get("Cube")
    if obj is None:
        coll = _ensure_collection("ARES_Turntable")
        obj = _add_empty("ARES_Turntable_Focus", coll, loc=(0.0, 0.0, 0.0))
    return obj


def _apply_dof(cam: bpy.types.Object, focus: bpy.types.Object) -> None:
    cam.data.dof.use_dof = True
    cam.data.dof.focus_object = focus
    if hasattr(cam.data.dof, "aperture_fstop"):
        cam.data.dof.aperture_fstop = 2.8


def _constrain_camera_and_carrier(
    cam: bpy.types.Object,
    carrier: bpy.types.Object,
    path: bpy.types.Object,
    focus: bpy.types.Object,
) -> None:
    track = next((c for c in cam.constraints if c.type == "TRACK_TO"), None)
    if track is None:
        track = cam.constraints.new(type="TRACK_TO")
    track.target = focus
    track.track_axis = "TRACK_NEGATIVE_Z"
    track.up_axis = "UP_Y"

    _apply_dof(cam, focus)

    follow = next((c for c in carrier.constraints if c.type == "FOLLOW_PATH"), None)
    if follow is None:
        follow = carrier.constraints.new(type="FOLLOW_PATH")
    follow.target = path
    follow.use_fixed_location = True
    follow.forward_axis = "FORWARD_Y"
    follow.up_axis = "UP_Z"

    path.data.use_path = True


def _animate_carrier_on_path(carrier: bpy.types.Object, frame_start: int, frame_end: int) -> None:
    follow = next((c for c in carrier.constraints if c.type == "FOLLOW_PATH"), None)
    if follow is None:
        return
    follow.offset_factor = 0.0
    follow.keyframe_insert(data_path="offset_factor", frame=frame_start)
    follow.offset_factor = 1.0
    follow.keyframe_insert(data_path="offset_factor", frame=frame_end)

    anim = carrier.animation_data
    if anim and anim.action:
        for fcu in anim.action.fcurves:
            if fcu.data_path.endswith("offset_factor"):
                for kp in fcu.keyframe_points:
                    kp.interpolation = "LINEAR"


def create_turntable(
    scene: bpy.types.Scene,
    *,
    seconds: int = 4,
    fps: int = 24,
    radius: float = 5.0,
    camera_height: float = 5.0,
    set_as_active_camera: bool = True,
    focus_obj: bpy.types.Object | None = None,
) -> dict[str, str]:
    """Pivot (0,0,0) > Carrier (child, follow-path) > Camera (child, local 0,0,Z).
       Camera: TrackTo + DOF vers un focus fiable (focus_obj si donné).
    """
    scn = scene
    frame_start = 1
    frame_end = frame_start + (seconds * max(1, int(fps))) - 1

    coll = _ensure_collection("ARES_Turntable")

    path = _add_circle_path(radius=radius, collection=coll)
    pivot = _add_empty("ARES_Turntable_Pivot", coll, loc=(0.0, 0.0, 0.0))
    carrier = _add_empty("ARES_Turntable_Carrier", coll, loc=(0.0, 0.0, 0.0))
    carrier.parent = pivot

    cam = _add_camera(local_height=camera_height, collection=coll)
    cam.parent = carrier

    focus = focus_obj or _choose_focus_object(scn)

    _constrain_camera_and_carrier(cam, carrier, path, focus)
    _animate_carrier_on_path(carrier, frame_start, frame_end)

    if set_as_active_camera:
        scn.camera = cam

    scn.frame_start = frame_start
    scn.frame_end = frame_end

    return {
        "collection": coll.name,
        "pivot": pivot.name,
        "carrier": carrier.name,
        "camera": cam.name,
        "focus": focus.name,
        "path": path.name,
        "frames": f"{frame_start}-{frame_end}",
    }
