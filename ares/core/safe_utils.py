"""Minimal safe utils for ARES v13 (data-first)."""
from __future__ import annotations

import contextlib

try:
    import bpy  # type: ignore
except Exception as e:
    raise RuntimeError("safe_utils must run inside Blender.") from e

from .constants import ENGINE_CANDIDATES


def ensure_collection(name: str) -> bpy.types.Collection:
    coll = bpy.data.collections.get(name)
    if coll is None:
        coll = bpy.data.collections.new(name)
        bpy.context.scene.collection.children.link(coll)
    return coll

def link_only_to_collection(obj: bpy.types.Object, collection: bpy.types.Collection) -> None:
    # Unlink from all, puis lien unique vers collection
    for coll in list(obj.users_collection):
        with contextlib.suppress(Exception):
            coll.objects.unlink(obj)
    if obj.name not in collection.objects:
        collection.objects.link(obj)

def select_render_engine(scene: bpy.types.Scene) -> str:
    """Choisit le premier moteur dispo parmi ENGINE_CANDIDATES et l'applique."""
    for eng in ENGINE_CANDIDATES:
        with contextlib.suppress(Exception):
            scene.render.engine = eng
            if scene.render.engine == eng:
                return eng
    return scene.render.engine  # fallback: ce qui reste

def ensure_eevee_defaults(scene: bpy.types.Scene) -> None:
    eng = select_render_engine(scene)  # pref Eevee/EeveeNext si dispo
    def _set(o, attr, val):
        with contextlib.suppress(Exception):
            setattr(o, attr, val)
    if eng in {"BLENDER_EEVEE", "BLENDER_EEVEE_NEXT"}:
        _set(scene.eevee, "use_gtao", True)
        _set(scene.eevee, "use_bloom", True)
        _set(scene.eevee, "use_soft_shadows", True)

def safe_set(obj, prop: str, value) -> None:
    with contextlib.suppress(Exception):
        setattr(obj, prop, value)
def set_scene_camera(scene, cam_obj) -> None:
    """Force la caméra de rendu pour la scène."""
    try:
        if cam_obj and getattr(cam_obj, "type", None) == "CAMERA":
            scene.camera = cam_obj
    except Exception:
        pass
