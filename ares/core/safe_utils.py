"""Minimal safe utils for ARES v13 (data-first)."""
from __future__ import annotations

import contextlib

try:
    import bpy  # type: ignore
except Exception as e:
    raise RuntimeError("safe_utils must run inside Blender.") from e

from .constants import ENGINE_CANDIDATES

# -------------------- Collections & Linking --------------------

def ensure_collection(name: str) -> bpy.types.Collection:
    coll = bpy.data.collections.get(name)
    if coll is None:
        coll = bpy.data.collections.new(name)
        bpy.context.scene.collection.children.link(coll)
    return coll

def link_only_to_collection(obj: bpy.types.Object, collection: bpy.types.Collection) -> None:
    # Unlink de toutes les collections puis link unique vers target
    for coll in list(obj.users_collection):
        with contextlib.suppress(Exception):
            coll.objects.unlink(obj)
    if obj.name not in collection.objects:
        collection.objects.link(obj)

# -------------------- Render Engine & Eevee defaults --------------------

def select_render_engine(scene: bpy.types.Scene) -> str:
    """Choisit le premier moteur dispo parmi ENGINE_CANDIDATES et l'applique."""
    for eng in ENGINE_CANDIDATES:
        with contextlib.suppress(Exception):
            scene.render.engine = eng
            if scene.render.engine == eng:
                return eng
    return scene.render.engine

def ensure_eevee_defaults(scene: bpy.types.Scene) -> None:
    """Préférence Eevee/EeveeNext, et quelques flags sûrs si dispo."""
    eng = select_render_engine(scene)
    def _set(o, attr, val):
        with contextlib.suppress(Exception):
            setattr(o, attr, val)
    if eng in {"BLENDER_EEVEE", "BLENDER_EEVEE_NEXT"}:
        _set(scene.eevee, "use_gtao", True)
        _set(scene.eevee, "use_bloom", True)
        _set(scene.eevee, "use_soft_shadows", True)

def safe_set(obj, prop: str, value) -> None:
    """Set sans planter si l'attribut n'existe pas (différences de versions)."""
    with contextlib.suppress(Exception):
        setattr(obj, prop, value)

# -------------------- Scene Hygiene --------------------

def purge_scene_defaults(keep_collections: tuple[str, ...] = ()) -> None:
    """
    Supprime proprement tout objet et collections par défaut (Cube/Camera/Light, etc.).
    Data-first, sans operators.
    """
    # 1) Supprimer tous les objets (unlink + remove)
    for obj in list(bpy.data.objects):
        # Unlink from all collections
        for coll in list(obj.users_collection):
            with contextlib.suppress(Exception):
                coll.objects.unlink(obj)
        with contextlib.suppress(Exception):
            bpy.data.objects.remove(obj, do_unlink=True)

    # 2) Supprimer collections vides sauf racine + celles explicitement gardées
    root = bpy.context.scene.collection
    for coll in list(bpy.data.collections):
        if coll == root or coll.name in keep_collections:
            continue
        with contextlib.suppress(Exception):
            bpy.data.collections.remove(coll)

    # 3) Nettoyer datablocks orphelins courants
    for datablock in (bpy.data.meshes, bpy.data.cameras, bpy.data.lights,
                      bpy.data.curves, bpy.data.materials):
        for datab in list(datablock):
            if datab.users == 0:
                with contextlib.suppress(Exception):
                    datablock.remove(datab)

def set_scene_camera(scene: bpy.types.Scene, cam_obj: bpy.types.Object) -> None:
    """Force la caméra de rendu pour la scène (si valide)."""
    if cam_obj and getattr(cam_obj, "type", None) == "CAMERA":
        with contextlib.suppress(Exception):
            scene.camera = cam_obj
