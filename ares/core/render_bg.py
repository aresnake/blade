"""
ARES Core LTS v13 — render_bg
Turntable & rendu MP4 en headless (Eevee/EeveeNext), 100% data-first.
Règles: moteur Eevee si dispo, TrackTo strict, animer curve.data.eval_time.
"""
from __future__ import annotations

import math
import os

try:
    import bmesh  # type: ignore
    import bpy  # type: ignore
except Exception as e:
    raise RuntimeError("Ce script doit être exécuté depuis Blender.") from e

from .constants import (
    DEFAULT_FPS,
    DEFAULT_RES_X,
    DEFAULT_RES_Y,
    TT_CAMERA_NAME,
    TT_PATH_NAME,
    TT_TARGET_NAME,
)
from .safe_utils import (
    ensure_collection,
    ensure_eevee_defaults,
    link_only_to_collection,
    purge_scene_defaults,
    set_scene_camera,
)


def demo_turntable_mp4(
    out_path: str = "renders/demo_tt.mp4",
    seconds: int = 1,
    fps: int = DEFAULT_FPS,
    res: tuple[int, int] = (DEFAULT_RES_X, DEFAULT_RES_Y),
) -> str:
    """
    Génère une courte animation turntable et encode en MP4 (Eevee/EeveeNext).
    Retourne le chemin du MP4 écrit.
    """
    # --- scène & engine ---
    scene = bpy.context.scene
    ensure_eevee_defaults(scene)

    # Nettoyage des éléments par défaut (Cube/Camera/Light)
    purge_scene_defaults()

    # Résolution / FPS / frames
    scene.render.resolution_x, scene.render.resolution_y = res
    scene.render.fps = fps
    scene.frame_start = 1
    scene.frame_end = max(1, int(seconds * fps))

    # --- collection de travail ---
    coll = ensure_collection("ARES_RenderBG_Demo")

    # Objet: cube via bmesh (data-first)
    mesh = bpy.data.meshes.new("DemoCube")
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    bm.to_mesh(mesh)
    bm.free()
    obj = bpy.data.objects.new("DemoCube", mesh)
    link_only_to_collection(obj, coll)

    # Cible (Empty) au centre
    tgt = bpy.data.objects.new(TT_TARGET_NAME, None)
    tgt.empty_display_size = 0.2
    tgt.empty_display_type = "PLAIN_AXES"
    link_only_to_collection(tgt, coll)

    # Caméra
    cam = bpy.data.objects.new(TT_CAMERA_NAME, bpy.data.cameras.new(TT_CAMERA_NAME))
    cam.location = (2.5, 0.0, 1.2)
    link_only_to_collection(cam, coll)
    # Force la caméra ARES comme caméra de scène
    set_scene_camera(scene, cam)

    # Piste NURBS circulaire
    curve_data = bpy.data.curves.new(TT_PATH_NAME, "CURVE")
    curve_data.dimensions = "3D"
    curve_data.resolution_u = 64
    spline = curve_data.splines.new("NURBS")
    spline.points.add(7)
    angles = (0, math.pi/4, math.pi/2, 3*math.pi/4, math.pi, 5*math.pi/4, 3*math.pi/2, 7*math.pi/4)
    for i, ang in enumerate(angles):
        x = 2.5 * math.cos(ang)
        y = 2.5 * math.sin(ang)
        spline.points[i].co = (x, y, 0.0, 1.0)
    curve_obj = bpy.data.objects.new(TT_PATH_NAME, curve_data)
    link_only_to_collection(curve_obj, coll)

    # Contraintes: Follow Path + Track To (axes stricts)
    follow = cam.constraints.new(type="FOLLOW_PATH")
    follow.target = curve_obj
    follow.use_fixed_location = False
    follow.use_curve_follow = False

    track = cam.constraints.new(type="TRACK_TO")
    track.target = tgt
    track.track_axis = "TRACK_NEGATIVE_Z"
    track.up_axis = "UP_Y"

    # Animation: animer curve.eval_time
    curve_data.path_duration = max(1, scene.frame_end - scene.frame_start + 1)
    curve_data.use_path = True
    curve_data.eval_time = 0.0
    curve_data.keyframe_insert(data_path="eval_time", frame=scene.frame_start)
    curve_data.eval_time = float(curve_data.path_duration)
    curve_data.keyframe_insert(data_path="eval_time", frame=scene.frame_end)

    # Sortie MP4 (H.264/AAC) — robuste Windows/Blender
    out_path = os.path.abspath(out_path)
    os.makedirs(os.path.dirname(out_path), exist_ok=True)

    scene.render.image_settings.file_format = "FFMPEG"
    scene.render.ffmpeg.format = "MPEG4"
    scene.render.ffmpeg.codec = "H264"
    scene.render.ffmpeg.audio_codec = "AAC"
    scene.render.ffmpeg.constant_rate_factor = "MEDIUM"

    # Écrire directement le chemin final (évite double extension)
    scene.render.filepath = out_path
    scene.render.use_file_extension = False

    # Rendu animation
    bpy.ops.render.render(animation=True)

    # Résolution robuste du chemin écrit
    base, _ = os.path.splitext(out_path)
    candidates = [
        out_path,
        base + ".mp4",
        base + "-0001.mp4",
        base + "-0000.mp4",
    ]
    for p in candidates:
        if os.path.exists(p):
            return p
    return out_path
