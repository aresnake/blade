import sys
from pathlib import Path

def test_primitives_cube_preview(tmp_path=None):
    root = Path(r'D:\V13\workspace_v13')
    sys.path.insert(0, str(root))

    import bpy
    from ares.modules.gen import primitives as gen

    # Sujet: cube data-first + matériau
    obj = gen.make_cube(name='TestCube', size=1.2)

    # Preview TT 1s @24fps
    out = gen.quick_preview_turntable(obj, seconds=1, fps=24, radius=2.5, samples=8)
    p = Path(out)
    assert p.exists(), f"preview not created: {p}"
    assert p.stat().st_size > 0, "preview is empty"
