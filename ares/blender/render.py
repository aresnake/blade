import math
from dataclasses import dataclass
from pathlib import Path

import bpy

from ares.modules.turntable.api import compute_orbit_for_object


@dataclass(frozen=True)
class RenderPreset:
    res_x: int = 1280
    res_y: int = 720
    fps: int = 25
    samples: int = 64
    codec: str = "H264"  # H264 | PNG_SEQ

class AresRenderError(RuntimeError):
    ...

def _ensure_scene_setup(preset: RenderPreset):
    scene = bpy.context.scene

    # --- choose engine robustly ---
    engines = {e.identifier for e in bpy.types.RenderSettings.bl_rna.properties["engine"].enum_items}
    if "BLENDER_EEVEE" in engines:
        scene.render.engine = "BLENDER_EEVEE"
    elif "BLENDER_EEVEE_NEXT" in engines:
        scene.render.engine = "BLENDER_EEVEE_NEXT"
    else:
        scene.render.engine = "CYCLES"

    # --- samples per engine (best effort) ---
    try:
        if scene.render.engine.startswith("BLENDER_EEVEE"):
            # Eevee / Eevee Next
            try:
                scene.eevee.taa_render_samples = preset.samples
            except Exception:
                pass
        elif scene.render.engine == "CYCLES":
            scene.cycles.samples = preset.samples
            scene.cycles.use_adaptive_sampling = True
    except Exception:
        pass

    # --- resolution & fps ---
    scene.render.resolution_x = preset.res_x
    scene.render.resolution_y = preset.res_y
    scene.render.fps = preset.fps

    # --- output format ---
    if preset.codec == "H264":
        scene.render.image_settings.file_format = "FFMPEG"
        scene.render.ffmpeg.format = "MPEG4"
        scene.render.ffmpeg.codec = "H264"
        scene.render.ffmpeg.constant_rate_factor = "MEDIUM"
        scene.render.ffmpeg.gopsize = preset.fps * 2
        scene.render.ffmpeg.max_b_frames = 2
    else:
        scene.render.image_settings.file_format = "PNG"

def _get_output_path(obj_name: str, is_video: bool) -> Path:
    from ares.core.paths import ROOT
    out_dir = ROOT / "renders" / "turntable"
    out_dir.mkdir(parents=True, exist_ok=True)
    ext = ".mp4" if is_video else "_####.png"
    return out_dir / f"{obj_name}{ext}"

def render_turntable(obj, preset: RenderPreset | None = None, seconds: int = 8) -> Path:
    """Crée une caméra orbit, anime 0->360°, rend en mp4 (par défaut)."""
    if obj is None:
        raise AresRenderError("No active object to render")

    preset = preset or RenderPreset()
    _ensure_scene_setup(preset)

    scene = bpy.context.scene
    obj_name = (obj.name or "Object").replace(" ", "_")
    video = (preset.codec == "H264")
    out_path = _get_output_path(obj_name, is_video=video)
    scene.render.filepath = str(out_path)

    # Cam + empty pivot
    cam = next((o for o in scene.objects if o.type == "CAMERA"), None)
    if cam is None:
        cam_data = bpy.data.cameras.new("AresCam")
        cam = bpy.data.objects.new("AresCam", cam_data)
        scene.collection.objects.link(cam)
    empty = bpy.data.objects.new("AresOrbit", None)
    scene.collection.objects.link(empty)

    # Position/parenting
    spec = compute_orbit_for_object(obj)
    cam.data.lens_unit = "FOV"
    cam.data.angle = math.radians(spec.fov_deg)

    empty.location = obj.location.copy()
    cam.parent = empty
    cam.location = (spec.radius, 0.0, spec.height)

    # orienter la caméra (comment séparé pour éviter E501)
    cam.rotation_euler = (
        math.radians(0),
        math.radians(0),
        math.radians(180),
    )

    # Track constraint
    c = cam.constraints.get("TRACK_TO") or cam.constraints.new(type="TRACK_TO")
    c.name = "TRACK_TO"
    c.target = obj
    c.track_axis = "TRACK_NEGATIVE_Z"
    c.up_axis = "UP_Y"

    # Animation orbit
    total_frames = max(1, int(preset.fps * seconds))
    scene.frame_start = 1
    scene.frame_end = total_frames
    empty.rotation_euler = (0.0, 0.0, math.radians(0))
    empty.keyframe_insert(data_path="rotation_euler", frame=1)
    empty.rotation_euler = (0.0, 0.0, math.radians(360))
    empty.keyframe_insert(data_path="rotation_euler", frame=total_frames)

    # Interpolation linéaire
    if empty.animation_data and empty.animation_data.action:
        for fcu in empty.animation_data.action.fcurves:
            for kp in fcu.keyframe_points:
                kp.interpolation = "LINEAR"

    # Rendu
    bpy.ops.render.render(animation=True)
    return Path(scene.render.filepath)
