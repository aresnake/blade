# Blade v13 — helpers.objects (patch: create_cube)
import bpy

def safe_set(obj, prop, value):
    try:
        if hasattr(obj, prop):
            setattr(obj, prop, value)
            return True
    except Exception:
        pass
    return False

def link_object(obj, collection=None):
    if obj is None:
        return False
    if collection is None:
        collection = bpy.context.scene.collection
    if obj.name not in collection.objects:
        collection.objects.link(obj)
    return True

def create_mesh_object(name="Object", verts=(), edges=(), faces=(), collection=None):
    mesh = bpy.data.meshes.new(name + "_Mesh")
    mesh.from_pydata(list(verts), list(edges), list(faces))
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    link_object(obj, collection=collection)
    return obj

def create_cube(name="Cube", size=1.0, collection=None):
    s = float(size) * 0.5
    v = [(-s,-s,-s), ( s,-s,-s), ( s, s,-s), (-s, s,-s),
         (-s,-s, s), ( s,-s, s), ( s, s, s), (-s, s, s)]
    f = [(0,1,2,3),(4,5,6,7),(0,1,5,4),(2,3,7,6),(1,2,6,5),(0,3,7,4)]
    return create_mesh_object(name=name, verts=v, edges=[], faces=f, collection=collection)
