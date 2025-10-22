# ares/core/render_bg.py — turntable Eevee MP4 robuste (headless safe)
from __future__ import annotations

import math
import contextlib
from pathlib import Path
from typing import Tuple

import inspect
def _set_scene_camera_compat(cam):
    """Compat: accepte _set_scene_camera_compat(cam) ou set_scene_camera(scene, cam)."""
    try:
        sig = inspect.signature(set_scene_camera)
        if len(sig.parameters) >= 2:
            return set_scene_camera(bpy.context.scene, cam)
        else:
            return _set_scene_camera_compat(cam)
    except Exception:
        bpy.context.scene.camera = cam
try:
    import bpy  # type: ignore
except Exception as _e:
    bpy = None

# --- Constantes (import si dispo, sinon défauts) ---
try:
    from .constants import (
        TT_RIG_NAME,
        TT_TARGET_NAME,
        TT_CAMERA_NAME,
        DEFAULT_RES_X,
        DEFAULT_RES_Y,
        DEFAULT_FPS,
        DEFAULT_RADIUS,
        DEFAULT_HEIGHT,
    )
except Exception:
    TT_RIG_NAME = "TT_Rig"
    TT_TARGET_NAME = "TT_Target"
    TT_CAMERA_NAME = "TT_Camera"
    DEFAULT_RES_X = 1280
    DEFAULT_RES_Y = 720
    DEFAULT_FPS = 24
    DEFAULT_RADIUS = 2.5
    DEFAULT_HEIGHT = 1.0

# --- Utils (prend safe_utils si présent, sinon fallback local) ---
with contextlib.suppress(Exception):
    from .safe_utils import purge_scene_defaults, set_scene_camera, ensure_eevee_defaults

if "purge_scene_defaults" not in globals():
    def purge_scene_defaults():
        """Purge les objets/colls par défaut sans lancer d'ops destructives hasardeuses."""
        scene = bpy.context.scene
        # Supprime tout objet de la scène de départ (Cube, Light, Camera…)
        for obj in list(bpy.data.objects):
            with contextlib.suppress(Exception):
                bpy.data.objects.remove(obj, do_unlink=True)
        # Nettoie les collections vides sauf master
        for coll in list(bpy.data.collections):
            if coll is not scene.collection:
                with contextlib.suppress(Exception):
                    bpy.data.collections.remove(coll)

if "set_scene_camera" not in globals():
    def _set_scene_camera_compat(cam):
        bpy.context.scene.camera = cam

if "ensure_eevee_defaults" not in globals():
    def ensure_eevee_defaults(scene):
        r = scene.render
        r.engine = "BLENDER_EEVEE"
        # Réglages sûrs
        scene.eevee.use_gtao = True
        scene.eevee.use_bloom = False
        scene.eevee.shadow_cube_size = "1024"
        scene.eevee.shadow_cascade_size = "1024"

# Compat util depuis ares.__init__ (déjà ajouté)
from ares import ensure_collection, link_only_to_collection

def _ensure_camera(name: str = TT_CAMERA_NAME) -> "bpy.types.Object":
    cam_data = bpy.data.cameras.new(name)
    cam = bpy.data.objects.new(name, cam_data)
    return cam

def _ensure_target(name: str = TT_TARGET_NAME) -> "bpy.types.Object":
    empty = bpy.data.objects.new(name, None)
    empty.empty_display_type = "PLAIN_AXES"
    return empty

def _animate_rig_rotation(rig: "bpy.types.Object", frame_start: int, frame_end: int):
    rig.rotation_mode = "XYZ"
    rig.rotation_euler = (0.0, 0.0, 0.0)
    rig.keyframe_insert(data_path="rotation_euler", frame=frame_start, index=-1)
    rig.rotation_euler = (0.0, 0.0, 2 * math.pi)
    rig.keyframe_insert(data_path="rotation_euler", frame=frame_end, index=-1)

def _set_output_mp4(scene: "bpy.types.Scene", out_path: Path):
    r = scene.render
    out_path.parent.mkdir(parents=True, exist_ok=True)
    r.filepath = str(out_path)
    r.image_settings.file_format = "FFMPEG"
    r.ffmpeg.format = "MPEG4"
    r.ffmpeg.codec = "H264"
    r.ffmpeg.audio_codec = "AAC"
    r.ffmpeg.constant_rate_factor = "MEDIUM"
    r.ffmpeg.video_bitrate = 6000  # raisonnable pour 720p
    r.ffmpeg.minrate = 0
    r.ffmpeg.maxrate = 9000
    r.ffmpeg.buffersize = 224 * 8

def demo_turntable_mp4(
    out_path: str = "renders/demo_tt.mp4",
    seconds: int = 1,
    fps: int = DEFAULT_FPS,
    res: Tuple[int, int] = (DEFAULT_RES_X, DEFAULT_RES_Y),
) -> str:
    """
    Turntable robuste:
      - Empty TT_Rig (centré) qui tourne sur Z
      - Caméra parente du rig, offset (radius,height)
      - TrackTo camera -> TT_Target
      - Encode MP4 (FFMPEG/H264/AAC)
    """
    if bpy is None:
        raise RuntimeError("bpy indisponible (demo_turntable_mp4)")

    scene = bpy.context.scene
    ensure_eevee_defaults(scene)

    # Nettoyage scène
    purge_scene_defaults()

    # Résolution / FPS / frames
    scene.render.resolution_x, scene.render.resolution_y = res
    scene.render.fps = fps
    scene.frame_start = 1
    scene.frame_end = max(1, int(seconds * fps))

    coll = ensure_collection("ARES_RenderBG_Demo")

    # Rig + cible + caméra
    rig = bpy.data.objects.new(TT_RIG_NAME, None)
    tgt = _ensure_target(TT_TARGET_NAME)
    cam = _ensure_camera(TT_CAMERA_NAME)

    # Link propre (seule coll)
    link_only_to_collection(rig, coll)
    link_only_to_collection(tgt, coll)
    link_only_to_collection(cam, coll)

    # Placement
    radius = DEFAULT_RADIUS
    height = DEFAULT_HEIGHT
    cam.location = (radius, 0.0, height)
    tgt.location = (0.0, 0.0, 0.0)

    # Parent & contraintes
    cam.parent = rig
    con = cam.constraints.new("TRACK_TO")
    con.target = tgt
    con.track_axis = "TRACK_NEGATIVE_Z"
    con.up_axis = "UP_Y"

    # Animate 0 → 360°
    _animate_rig_rotation(rig, scene.frame_start, scene.frame_end)

    # Caméra de scène
    _set_scene_camera_compat(cam)

    # Sortie MP4
    out = Path(out_path)
    _set_output_mp4(scene, out)

    # Rendu
    with contextlib.suppress(Exception):
        bpy.ops.render.render(animation=True)

    # Garanties de retour
    if not out.exists() or out.stat().st_size == 0:
        # Essaye fallback dans // (Blender peut altérer filepath)
        alt = Path(bpy.path.abspath("//")) / out.name
        if alt.exists() and alt.stat().st_size > 0:
            return str(alt)
    return str(out)


