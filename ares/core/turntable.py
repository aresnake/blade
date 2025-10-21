from __future__ import annotations

# Chargement des modules internes ARES
# - turntable réel (contient la vraie fonction render_turntable(...))
# - turntable_gen (génération du rig) : on complète ses helpers si absents
import importlib
from dataclasses import dataclass

try:
    tt = importlib.import_module("ares.modules.turntable.turntable")
except Exception as e:  # pragma: no cover
    raise RuntimeError(f"[ARES] Unable to import ares.modules.turntable.turntable: {e}")

try:
    tg = importlib.import_module("ares.modules.turntable_gen")
except Exception:  # pragma: no cover
    # Le shim reste utilisable pour le rendu direct même si le gen est manquant,
    # mais on le note clairement.
    tg = None  # type: ignore


# ---------------------------------------------------------------------------
# Helpers "Never Again" — fournis au besoin à turntable_gen
# ---------------------------------------------------------------------------
def _ensure_collection(name: str = "ARES_Turntable"):
    import bpy
    coll = bpy.data.collections.get(name)
    if not coll:
        coll = bpy.data.collections.new(name)
        # link au root de la scène si nécessaire
        root = bpy.context.scene.collection
        if coll.name not in [c.name for c in root.children]:
            root.children.link(coll)
    return coll


def _link_only_to_collection(obj, collection):
    # unlink partout
    for c in list(obj.users_collection):
        try:
            c.objects.unlink(obj)
        except Exception:
            pass
    # link unique
    if obj.name not in collection.objects:
        collection.objects.link(obj)
    return obj


def _make_curve_circle(name: str = "TT_Path", radius: float = 3.0):
    import bpy
    # Réutilise si existe
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


# Si turntable_gen est présent, on complète ses helpers manquants
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
    Note: le moteur/sortie/échantillons restent gérés par l'impl implémentation réelle.
    """
    res_x: int = 1280
    res_y: int = 720
    fps: int = 24
    samples: int = 32


def create_turntable_rig(radius: float = 3.0):
    """Facultatif: proxy pour création rig via turntable_gen si dispo.
    Retourne True si au moins le path/coll nécessaires ont été assurés.
    """
    if tg is None:
        return False
    # S'assure que la collection et le path existent
    coll = tg.ensure_collection("ARES_Turntable")
    path = tg.make_curve_circle("TT_Path", radius=radius)
    # On lie proprement (au cas où)
    _link_only_to_collection(path, coll)
    return True


def render_turntable(
    target=None,
    radius: float = 2.5,
    seconds: int = 4,
    fps: int | None = None,
    mp4_path: str = "renders/turntable.mp4",
    samples: int | None = None,
    preset: RenderPreset | None = None,
):
    """Wrapper stable qui délègue à la vraie implémentation de render_turntable.

    - ps / samples sont repris du preset si fournis.
    - preset.res_x / preset.res_y sont ignorés ici si l'impl réelle ne les supporte pas,
      mais on garde ce type pour compat UI.
    """
    # Harmonisation des paramètres depuis le preset éventuel
    if preset is not None:
        if fps is None:
            fps = preset.fps
        if samples is None:
            samples = preset.samples

    # Valeurs par défaut compatibles avec la signature réelle
    if fps is None:
        fps = 24
    if samples is None:
        samples = 32

    # Appel direct de l'implémentation réelle
    return tt.render_turntable(
        target=target,
        radius=radius,
        seconds=seconds,
        fps=fps,
        mp4_path=mp4_path,
        samples=samples,
    )


# __all__ explicite pour les imports "from ares.core import turntable"
__all__ = [
    "RenderPreset",
    "create_turntable_rig",
    "render_turntable",
]
