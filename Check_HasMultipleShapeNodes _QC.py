#Find Meshes with Multiple Shape Nodes

#2022-07-20 Abby Cohn
#QC tool to check if objects in Geometry group have multiple shape nodes

#imports
import pymel.core as pm

# Required
__desc__ = 'Find Meshes with Multiple Shape Nodes'

# Required Functions
def fix_func(*args):
    pass

def check_func(*args):
    try:
        geometryMeshes = []
        multipleShapes = []

        meshes = pm.ls(type = 'mesh', noIntermediate = True)

        for m in meshes:
            name = m.longName().split("|")
            if "Geometry" in name and "RsProxy" not in name:
                geometryMeshes.append(m)

        for gm in geometryMeshes:
            gm_transform = gm.listRelatives(parent=True)[0]
            gm_shape_list = (gm_transform.listRelatives(children=True))
            if len(gm_shape_list) > 1:
                multipleShapes.append(gm_transform)

        print(multipleShapes)

    except Exception as f:
        print(f)

check_func()
