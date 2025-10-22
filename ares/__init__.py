# ares/__init__.py — Public API & compat layer (v13)
# - Ré-expose des helpers legacy attendus par modules/tests :
#   link_object(), make_curve_circle()
# - Data-first, pas de dépendance à active/selected.
# - Sûr en headless (scene.collection existe).

from __future__ import annotations

import contextlib
from typing import Optional

try:
    import bpy
except Exception as _e:
    bpy = None  # permet import hors Blender (ex: out-of-process tooling)

# --- Exports internes (stables) ---
# N.B. On n’échoue pas si ces modules n’existent pas encore ; les helpers ci-dessous couvrent le besoin.
with contextlib.suppress(Exception):
    from .core import constants  # noqa: F401


# --- Utils internes sûrs ---

def _ensure_scene() -> "bpy.types.Scene":
    if bpy is None:
        raise RuntimeError("bpy indisponible (import hors Blender).")
    scene = getattr(bpy.context, "scene", None)
    if scene is None:
        raise RuntimeError("Aucune scène active dans bpy.context.")
    return scene


def ensure_collection(name: str) -> "bpy.types.Collection":
    """Retourne une Collection existante ou la crée + linke à la racine scène."""
    scene = _ensure_scene()
    coll = bpy.data.collections.get(name)
    if coll is None:
        coll = bpy.data.collections.new(name)
        # Link en enfant de la racine de la scène
        with contextlib.suppress(Exception):
            scene.collection.children.link(coll)
    return coll


def link_only_to_collection(obj: "bpy.types.Object",
                            collection: "bpy.types.Collection") -> "bpy.types.Object":
    """Assure que l'objet n'est linké que dans `collection` (unlink des autres)."""
    if bpy is None:
        raise RuntimeError("bpy indisponible.")
    # Unlink des autres collections pour éviter duplications
    for c in list(getattr(obj, "users_collection", []) or []):
        if c != collection:
            with contextlib.suppress(Exception):
                c.objects.unlink(obj)
    if obj.name not in collection.objects:
        with contextlib.suppress(Exception):
            collection.objects.link(obj)
    return obj


# --- API publique (legacy) ---

def link_object(obj: "bpy.types.Object",
                collection: Optional["bpy.types.Collection"] = None) -> "bpy.types.Object":
    """Lien sûr d'un objet dans une collection (par défaut: racine de la scène).

    - Si `collection` est None → utilise `scene.collection`.
    - Ne dépend pas d'un objet actif/sélectionné.
    - Idempotent (ne duplique pas le lien).
    """
    if bpy is None:
        raise RuntimeError("bpy indisponible.")
    scene = _ensure_scene()
    target = collection or scene.collection
    if obj.name not in target.objects:
        with contextlib.suppress(Exception):
            target.objects.link(obj)
    return obj


def make_curve_circle(name: str = "TT_Path",
                      radius: float = 1.0,
                      collection_name: Optional[str] = None) -> "bpy.types.Object":
    """Crée un cercle NURBS (closed) comme chemin d’orbite.

    - `radius` en unités Blender.
    - Linke dans `collection_name` si fourni, sinon dans une collection 'ARES' (créée si absente).
    """
    if bpy is None:
        raise RuntimeError("bpy indisponible.")
    crv = bpy.data.curves.new(name=name, type="CURVE")
    crv.dimensions = "3D"
    spline = crv.splines.new("NURBS")
    # 4 points pour un cercle NURBS de base (ordre 4), cyclic
    spline.points.add(3)
    pts = [
        ( radius, 0.0,   0.0, 1.0),
        ( 0.0,   radius, 0.0, 1.0),
        (-radius, 0.0,   0.0, 1.0),
        ( 0.0,  -radius, 0.0, 1.0),
    ]
    for p, co in zip(spline.points, pts):
        p.co = (co[0], co[1], co[2], co[3])
    spline.use_cyclic_u = True
    spline.order_u = 4

    obj = bpy.data.objects.new(name, crv)
    # Choix de collection
    if collection_name:
        coll = ensure_collection(collection_name)
    else:
        coll = ensure_collection("ARES")
    link_only_to_collection(obj, coll)
    return obj


__all__ = [
    # Compat & legacy public API
    "link_object",
    "make_curve_circle",
    # Utils utiles
    "ensure_collection",
    "link_only_to_collection",
    # Modules publics (si existants)
    "constants",
]
