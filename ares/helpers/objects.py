# Blade v13 — helpers.objects
# Data-first: pas de bpy.ops pour créer les data-blocks ; lier explicitement à la scène.
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
    """Lie un objet à une collection (ou à la scène active par défaut) si non déjà lié."""
    if obj is None:
        return False
    if collection is None:
        # collection racine de la scène active
        collection = bpy.context.scene.collection
    if obj.name not in collection.objects:
        collection.objects.link(obj)
    return True

def create_mesh_object(name="Object", verts=(), edges=(), faces=(), collection=None):
    """
    Crée un objet MESH depuis des données (verts, edges, faces) puis le lie à la collection.
    - verts: iterable[(x,y,z)]
    - edges: iterable[(i,j)]
    - faces: iterable[(i,j,k,...)]

    Retourne l'objet créé.
    """
    mesh = bpy.data.meshes.new(name + "_Mesh")
    mesh.from_pydata(list(verts), list(edges), list(faces))
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    link_object(obj, collection=collection)
    return obj
