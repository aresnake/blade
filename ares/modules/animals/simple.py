"""
Blade v13 — animals.simple
- "Low-poly dog" composé de cubes, sans bpy.ops (data-first).
"""
from ares.helpers import assign_material, create_cube, ensure_material


def _cube(name, size, loc):
    obj = create_cube(name=name, size=size)
    obj.location = loc
    return obj

def create_lowpoly_dog(root_name="Dog"):
    # corps, tête, pattes, queue (cubes)
    body = _cube(root_name+"_Body", size=1.2, loc=(0,0,0.6))
    head = _cube(root_name+"_Head", size=0.6, loc=(0.7,0,1.1))
    legFL = _cube(root_name+"_LegFL", size=0.25, loc=(0.35, 0.25, 0.25))
    legFR = _cube(root_name+"_LegFR", size=0.25, loc=(0.35,-0.25, 0.25))
    legBL = _cube(root_name+"_LegBL", size=0.25, loc=(-0.35, 0.25, 0.25))
    legBR = _cube(root_name+"_LegBR", size=0.25, loc=(-0.35,-0.25, 0.25))
    tail  = _cube(root_name+"_Tail",  size=0.15, loc=(-0.7,0,1.0))

    # parent simple (head/legs/tail parentés au body)
    for o in (head, legFL, legFR, legBL, legBR, tail):
        o.parent = body

    # mat simple
    mat = ensure_material("Dog_Mat")
    for o in (body, head, legFL, legFR, legBL, legBR, tail):
        assign_material(o, mat, 0)

    return body  # racine
