from __future__ import annotations

import importlib
import math
from dataclasses import dataclass
from typing import Optional


# ---------------------------------------------------------------------------
# Chargement des modules internes ARES
# ---------------------------------------------------------------------------
try:
    tt = importlib.import_module("ares.modules.turntable.turntable")
except Exception as e:  # pragma: no cover
    raise RuntimeError(
        f"[ARES] Unable to import ares.modules.turntable.turntable: {e}"
    )

try:
    tg = importlib.import_module("ares.modules.turntable_gen")
except Exception:  # pragma: no cover
    # Le shim reste utilisable pour le rendu direct même si le gen est manquant
    tg = None  # type: ignore


# ---------------------------------------------------------------------------
# Helpers "Never Again" — fournis au besoin à turntable_gen
# ---------------------------------------------------------------------------
def _ensure_collection(name: str = "ARES_Turntable"):
    import bpy

    coll = bpy.data.collections.get(name)
    if not coll:
        coll = bpy.data.collections.new(name)
        root = bpy.context.scene.collection
        if coll.name not in [c.name for c in root.children]:
            root.children.link(coll)
    return coll


def _link_only_to_collection(obj, collection):
    for c in list(obj.users_collection):
        try:
            c.objects.unlink(obj)
        except Exception:
            pass
    if obj.name not in collection.objects:
        collection.objects.link(obj)
    return obj


def _make_curve_circle(name: str = "TT_Path", radius: float = 3.0):
    import bpy

    obj = bpy.data.objects.get(name)
    if obj and obj.type == "CURVE":
        obj.data.dimensions = "3D"
        return obj

    crv = bpy.data.curves.new(name + "_Curve", type="CURVE")
    crv.dimensions = "3D"
    spl = crv.splines.new("NURBS")
    spl.points.add(7)  # total 8 points
    coords = [
        (1, 0),
        (0.707, 0.707),
        (0, 1),
        (-0.707, 0.707),
        (-1, 0),
        (-0.707, -0.707),
        (0, -1),
        (0.707, -0.707),
    ]
    for i, (x, y) in enumerate(coords):
        spl.points[i].co = (x * radius, y * radius, 0.0, 1.0)

    spl.use_cyclic_u = True
    obj = bpy.data.objects.new(name, crv)
    bpy.context.scene.collection.objects.link(obj)
    return obj


if tg is not None:
    if getattr(tg, "ensure_collection", None) is None:
        tg.ensure_collection = _ensure_collection  # type: ignore
    if getattr(tg, "link_object", None) is None:
        tg.link_object = _link_only_to_collection  # type: ignore
    if getattr(tg, "make_curve_circle", None) is None:
        tg.make_curve_circle = _make_curve_circle  # type: ignore


# ---------------------------------------------------------------------------
# API stable exposée à la UI / aux appels externes
# ---------------------------------------------------------------------------
@dataclass
class RenderPreset:
    """Preset minimal pour compat UI.

    Note: moteur/sortie/échantillons restent gérés par l’implémentation réelle.
    """

    res_x: int = 1280
    res_y: int = 720
    fps: int = 24
    samples: int = 32


def create_turntable_rig(radius: float = 3.0) -> bool:
    """Proxy pour création rig via turntable_gen si dispo.
    Retourne True si au moins path/coll existent.
    """
    if tg is None:
        return False
    coll = tg.ensure_collection("ARES_Turntable")
    path = tg.make_curve_circle("TT_Path", radius=radius)
    _link_only_to_collection(path, coll)
    return True


def _set_render_engine_eevee(scn) -> None:
    """Règle moteur sur BLENDER_EEVEE (Never Again) en mode tolérant."""
    try:
        scn.render.engine = "BLENDER_EEVEE"
    except Exception:
        try:
            scn.render.engine = "BLENDER_EEVEE_NEXT"
        except Exception:
            pass
    # Safe set d’options fréquentes (tolérant aux builds)
    ee = getattr(scn, "eevee", None)
    if ee:
        for attr, val in [
            ("use_bloom", True),
            ("use_gtao", True),
            ("shadow_method", "ESM"),
        ]:
            try:
                setattr(ee, attr, val)
            except Exception:
                pass


def render_turntable(  # noqa: D401
    target: Optional[object] = None,
    radius: float = 2.0,
    seconds: int = 1,
    fps: int = 24,
    mp4_path: str | None = None,
    samples: int = 16,
    preset: RenderPreset | None = None,
):
    """Rend une animation de turntable.

    Si `mp4_path` est fourni, force une sortie MP4 (FFMPEG/H264) vers un chemin ABSOLU.
    Sinon, Blender utilisera la sortie courante (séquence d’images).
    """
    import bpy
    from pathlib import Path

    scn = bpy.context.scene

    # Moteur EEVEE par défaut (Never Again)
    _set_render_engine_eevee(scn)

    # Optionnel: preset résolution/échantillons
    if preset:
        try:
            scn.render.resolution_x = getattr(preset, "res_x", scn.render.resolution_x)
            scn.render.resolution_y = getattr(preset, "res_y", scn.render.resolution_y)
            fps = getattr(preset, "fps", fps)
            samples = getattr(preset, "samples", samples)
        except Exception:
            pass

    # Durée & samples
    scn.render.fps = fps
    try:
        scn.cycles.samples = samples  # si moteur Cycles, ignore si EEVEE
    except Exception:
        pass

    total_frames = max(1, int(seconds * fps))
    scn.frame_start = 1
    scn.frame_end = total_frames

    # Caméra basique si absente
    if bpy.context.scene.camera is None:
        cam_data = bpy.data.cameras.new("TT_Camera")
        cam_obj = bpy.data.objects.new("TT_Camera", cam_data)
        bpy.context.collection.objects.link(cam_obj)
        bpy.context.scene.camera = cam_obj

    cam = bpy.context.scene.camera
    cam.location = (radius, 0.0, radius * 0.5)
    cam.rotation_euler = (math.radians(45), 0.0, math.radians(135))

    # Sortie vidéo si mp4_path fourni
    if mp4_path:
        p = Path(mp4_path).with_suffix(".mp4")
        p.parent.mkdir(parents=True, exist_ok=True)

        scn.render.image_settings.file_format = "FFMPEG"
        scn.render.ffmpeg.format = "MPEG4"
        scn.render.ffmpeg.codec = "H264"
        try:
            scn.render.ffmpeg.audio_codec = "AAC"
        except Exception:
            pass
        scn.render.ffmpeg.constant_rate_factor = "MEDIUM"
        scn.render.ffmpeg.use_max_b_frames = False

        scn.render.use_file_extension = True
        scn.render.use_overwrite = True
        scn.render.use_placeholder = False

        scn.render.filepath = str(p)
        print("[ARES][render] filepath ->", scn.render.filepath)

    # Lancement rendu
    bpy.ops.render.render(animation=True)

    # Vérif post-rendu si MP4 demandé
    if mp4_path:
        p = Path(mp4_path).with_suffix(".mp4")
        if p.exists():
            print("[ARES][render][OK] wrote:", p, p.stat().st_size, "bytes")
        else:
            print("[ARES][render][WARN] not found:", p)
