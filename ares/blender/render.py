from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class RenderPreset:
    res_x: int = 1280
    res_y: int = 720
    fps: int = 25
    samples: int = 64
    codec: str = "H264"

class AresRenderError(RuntimeError):
    ...

def render_turntable(obj, preset: RenderPreset | None = None, seconds: int = 8) -> Path:
    # stub: implémentation à venir
    raise NotImplementedError("render_turntable stub")
