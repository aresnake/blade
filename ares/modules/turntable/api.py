from dataclasses import dataclass


@dataclass(frozen=True)
class OrbitSpec:
    radius: float
    height: float
    fov_deg: float
    start_deg: float = 0.0
    end_deg: float = 360.0

def _bbox_world(obj):
    import mathutils
    ws = obj.matrix_world
    return [ws @ mathutils.Vector(c) for c in obj.bound_box]

def compute_orbit_for_object(obj, margin: float = 0.15) -> OrbitSpec:
    """Calcule un orbit cam simple à partir de la bbox de l'objet."""
    pts = _bbox_world(obj)
    xs = [p.x for p in pts]
    ys = [p.y for p in pts]
    zs = [p.z for p in pts]

    # centre uniquement en Z (on garde la cam orientée via constraint)
    cz = (max(zs) + min(zs)) / 2.0

    sx = max(xs) - min(xs)
    sy = max(ys) - min(ys)
    sz = max(zs) - min(zs)

    radius = max(sx, sy) * (0.6 + margin) + 0.001
    height = cz + sz * 0.15
    fov_deg = 50.0
    return OrbitSpec(radius=radius, height=height, fov_deg=fov_deg)
