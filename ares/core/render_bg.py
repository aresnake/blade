"""
ARES Core LTS v13 — render_bg
Turntable & rendu MP4 en headless (Eevee/EeveeNext), 100% data-first.
Règles: moteur Eevee si dispo, TrackTo strict, animer curve.data.eval_time.
"""
from __future__ import annotations

import math
import os

try:
    pass  # type: ignore
except Exception as e:
    raise RuntimeError("Ce script doit être exécuté depuis Blender.") from e

from .constants import (
    DEFAULT_FPS,
    DEFAULT_RES_X,
    DEFAULT_RES_Y,
    TT_CAMERA_NAME,
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
    Turntable robuste:
      - Empty "TT_Rig" au centre qui tourne sur Z
      - Caméra parente du rig, offset (radius,height)
      - TrackTo camera -> TT_Target
      - Encode MP4 (FFMPEG/H264/AAC)
    """
    import bpy  # type: ignore

    scene = bpy.context.scene
    ensure_eevee_defaults(scene)

    # Nettoyage de la scène par défaut
    purge_scene_defaults()

    # Résolution / FPS / frames
    scene.render.resolution_x, scene.render.resolution_y = res
    scene.render.fps = fps
    scene.frame_start = 1
    scene.frame_end = max(1, int(seconds * fps))

    coll = ensure_collection("ARES_RenderBG_Demo")

    # --- Rig central
    rig = bpy.data.objects.new(TT_RIG_NAME, None)
    rig.empty_display_type = "PLAIN_AXES"
    rig.empty_display_size = 0.4
    link_only_to_collection(rig, coll)

    # --- Cible (Empty) au centre
    tgt = bpy.data.objects.new(TT_TARGET_NAME, None)
    tgt.empty_display_type = "SPHERE"
    tgt.empty_display_size = 0.2
    tgt.location = (0.0, 0.0, 0.5)
    link_only_to_collection(tgt, coll)
    tgt.parent = rig

    # --- Caméra parente du rig
    cam_data = bpy.data.cameras.new(TT_CAMERA_NAME)
    cam = bpy.data.objects.new(TT_CAMERA_NAME, cam_data)
    link_only_to_collection(cam, coll)
    # Position voulue (coordonnées claires)
    radius, height = 2.5, 1.2
    cam.location = (radius, 0.0, height)
    cam.rotation_euler = (0.0, 0.0, 0.0)
    cam.parent = rig
    set_scene_camera(scene, cam)

    # TrackTo strict
    track = cam.constraints.new(type="TRACK_TO")
    track.target = tgt
    track.track_axis = "TRACK_NEGATIVE_Z"
    track.up_axis = "UP_Y"

    # --- Animation: rotation Z du rig (0 -> 2π)
    rig.rotation_mode = "XYZ"
    rig.rotation_euler = (0.0, 0.0, 0.0)
    rig.keyframe_insert(data_path="rotation_euler", frame=scene.frame_start, index=2)
    rig.rotation_euler[2] = 2.0 * math.pi
    rig.keyframe_insert(data_path="rotation_euler", frame=scene.frame_end, index=2)

    # Interpolation linéaire pour un mouvement uniforme
    for fcu in rig.animation_data.action.fcurves:
        for kp in fcu.keyframe_points:
            kp.interpolation = 'LINEAR'

    # --- Sortie MP4 (H.264/AAC)
    out_path = os.path.abspath(out_path)
    os.makedirs(os.path.dirname(out_path), exist_ok=True)

    scene.render.image_settings.file_format = "FFMPEG"
    scene.render.ffmpeg.format = "MPEG4"
    scene.render.ffmpeg.codec = "H264"
    scene.render.ffmpeg.audio_codec = "AAC"
    scene.render.ffmpeg.constant_rate_factor = "MEDIUM"

    scene.render.filepath = out_path
    scene.render.use_file_extension = False

    # Rendu animation
    bpy.ops.render.render(animation=True)

    # Résolution robuste du chemin écrit
    base, _ = os.path.splitext(out_path)
    for p in (out_path, base + ".mp4", base + "-0001.mp4", base + "-0000.mp4"):
        if os.path.exists(p):
            return p
    return out_path
