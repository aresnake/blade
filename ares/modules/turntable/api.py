from dataclasses import dataclass


@dataclass(frozen=True)
class OrbitSpec:
    radius: float
    height: float
    fov_deg: float
    start_deg: float = 0.0
    end_deg: float = 360.0

def compute_orbit_for_object(obj, margin: float = 0.15) -> OrbitSpec:
    # stub: calcule bbox -> orbit (à venir)
    return OrbitSpec(radius=2.0, height=0.5, fov_deg=50.0)
