"""
ARES Core LTS v13 — render_bg
Turntable & rendu MP4 en headless (Eevee), 100% data-first (pas de dépendance active/selected).
Règles: BLENDER_EEVEE, TrackTo strict, animer curve.data.eval_time (pas FollowPath.offset_factor).
"""
from __future__ import annotations
import os
import math

try:
    import bpy  # type: ignore
    import bmesh  # type: ignore
    from mathutils import Vector  # type: ignore
except Exception as e:
    raise RuntimeError("Ce script doit être exécuté depuis Blender.") from e

from .constants import (
    RENDER_ENGINE, DEFAULT_FPS, DEFAULT_RES_X, DEFAULT_RES_Y,
    TT_PATH_NAME, TT_RIG_NAME, TT_CAMERA_NAME, TT_TARGET_NAME,
)
from .safe_utils import (
    ensure_collection, link_only_to_collection, ensure_eevee_defaults, safe_set
)

# ---------- Utils de création data-first ----------
def _new_object_from_mesh(name: str, mesh: bpy.types.Mesh, collection: bpy.types.Collection) -> bpy.types.Object:
    obj = bpy.data.objects.new(name, mesh)
    link_only_to_collection(obj, collection)
    return obj

def create_cube(name: str, size: float, collection: bpy.types.Collection) -> bpy.types.Object:
    """Crée un cube via bmesh (pas de bpy.ops)."""
    mesh = bpy.data.meshes.new(name + "_ME")
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=size)
    bm.to_mesh(mesh); bm.free()
    return _new_object_from_mesh(name, mesh, collection)

def _new_curve_object_circle(name: str, radius: float, collection: bpy.types.Collection) -> bpy.types.Object:
    """Crée une courbe BEZIER approximant un cercle (4 points) — suffisante pour Follow Path."""
    curve_data = bpy.data.curves.new(name=name + "_CU", type="CURVE")
    curve_data.dimensions = '3D'
    spline = curve_data.splines.new(type='BEZIER')
    spline.bezier_points.add(3)  # total 4
    # 4 points cardinaux
    pts = [
        ( radius, 0.0,   0.0),
        ( 0.0,   radius, 0.0),
        (-radius,0.0,    0.0),
        ( 0.0,  -radius, 0.0),
    ]
    for i, p in enumerate(spline.bezier_points):
        p.co = Vector(pts[i])
        p.handle_left_type = 'AUTO'
        p.handle_right_type = 'AUTO'
    curve_data.use_path = True
    curve_obj = bpy.data.objects.new(name, curve_data)
    link_only_to_collection(curve_obj, collection)
    return curve_obj

def ensure_turntable_rig(collection: bpy.types.Collection, radius: float, height: float,
                         seconds: float, fps: int) -> tuple[bpy.types.Object, bpy.types.Object, bpy.types.Object]:
    """Crée TT_Path (curve), TT_Rig (Empty avec Follow Path), TT_Camera (TrackTo vers TT_Target)."""
    frames = int(round(seconds * fps))

    # Path (curve)
    path = bpy.data.objects.get(TT_PATH_NAME)
    if not path:
        path = _new_curve_object_circle(TT_PATH_NAME, radius=radius, collection=collection)

    # Rig (Empty)
    rig = bpy.data.objects.get(TT_RIG_NAME)
    if not rig:
        rig = bpy.data.objects.new(TT_RIG_NAME, None)
        link_only_to_collection(rig, collection)
    # Follow Path constraint
    fp = next((c for c in rig.constraints if c.type == 'FOLLOW_PATH'), None)
    if not fp:
        fp = rig.constraints.new(type='FOLLOW_PATH')
    fp.target = path
    fp.use_fixed_location = False  # on animera eval_time sur la courbe
    # Path duration + animation eval_time
    curve = path.data
    safe_set(curve, "path_duration", frames)
    # keyframes sur curve.eval_time (0 -> frames)
    curve.eval_time = 0.0
    curve.keyframe_insert(data_path="eval_time", frame=1)
    curve.eval_time = float(frames)
    curve.keyframe_insert(data_path="eval_time", frame=frames + 1)

    # Cible (Empty au centre)
    target = bpy.data.objects.get(TT_TARGET_NAME)
    if not target:
        target = bpy.data.objects.new(TT_TARGET_NAME, None)
        link_only_to_collection(target, collection)
        target.location = (0.0, 0.0, 0.0)

    # Caméra
    cam = bpy.data.objects.get(TT_CAMERA_NAME)
    if not cam:
        cam_data = bpy.data.cameras.new(TT_CAMERA_NAME + "_DATA")
        cam = bpy.data.objects.new(TT_CAMERA_NAME, cam_data)
        link_only_to_collection(cam, collection)
    # Parentage + placement caméra sur le rig, à (radius, 0, height)
    cam.parent = rig
    cam.location = (radius, 0.0, height)
    # Track To strict vers la cible
    t = next((c for c in cam.constraints if c.type == 'TRACK_TO'), None)
    if not t:
        t = cam.constraints.new(type='TRACK_TO')
    t.target = target
    t.track_axis = 'TRACK_NEGATIVE_Z'
    t.up_axis = 'UP_Y'

    return path, rig, cam

# ---------- Configuration rendu ----------
def configure_output(scene: bpy.types.Scene, out_path: str, res_x: int, res_y: int, fps: int) -> None:
    scene.render.engine = RENDER_ENGINE
    scene.render.resolution_x = res_x
    scene.render.resolution_y = res_y
    scene.render.fps = fps
    # FFmpeg H.264 + AAC / MP4
    scene.render.image_settings.file_format = 'FFMPEG'
    ff = scene.render.ffmpeg
    ff.format = 'MPEG4'
    ff.codec = 'H264'
    ff.constant_rate_factor = 'MEDIUM'
    ff.audio_codec = 'AAC'
    # Chemin
    scene.render.filepath = out_path

def ensure_project_dirs(base_dir: str) -> str:
    renders = os.path.join(base_dir, "renders")
    os.makedirs(renders, exist_ok=True)
    return renders

# ---------- Pipeline principal ----------
def render_turntable(subject: bpy.types.Object | None = None,
                     seconds: float = 4.0,
                     fps: int = DEFAULT_FPS,
                     res_x: int = DEFAULT_RES_X,
                     res_y: int = DEFAULT_RES_Y,
                     radius: float = 3.0,
                     height: float = 1.7) -> str:
    """
    Construit un rig de turntable autour du centre et rend un MP4.
    Retourne le chemin du fichier de sortie.
    """
    scene = bpy.context.scene
    ensure_eevee_defaults(scene)

    # Collection de travail
    coll = ensure_collection("ARES_Turntable")

    # Sujet si absent → créer un cube data-first
    if subject is None:
        subject = bpy.data.objects.get("ARES_Subject")
        if subject is None:
            subject = create_cube("ARES_Subject", size=1.5, collection=coll)
        else:
            link_only_to_collection(subject, coll)

    # Rig + Caméra
    path, rig, cam = ensure_turntable_rig(coll, radius=radius, height=height, seconds=seconds, fps=fps)

    # Sortie
    base_dir = bpy.path.abspath("//")  # dossier courant (blend ou CWD)
    renders_dir = ensure_project_dirs(base_dir)
    out_path = os.path.join(renders_dir, "out.mp4")
    configure_output(scene, out_path, res_x=res_x, res_y=res_y, fps=fps)

    # Frames
    total = int(round(seconds * fps)) + 1
    scene.frame_start = 1
    scene.frame_end = total

    print(f"[ARES] Render Turntable → {out_path} ({res_x}x{res_y} @ {fps}fps, {seconds}s)")
    bpy.ops.render.render(animation=True)
    return out_path

# ---------- Entrée script ----------
if __name__ == "__main__":
    render_turntable(
        subject=None,     # prendra/creera un cube
        seconds=4.0,
        fps=DEFAULT_FPS,
        res_x=DEFAULT_RES_X,
        res_y=DEFAULT_RES_Y,
        radius=3.0,
        height=1.7,
    )
