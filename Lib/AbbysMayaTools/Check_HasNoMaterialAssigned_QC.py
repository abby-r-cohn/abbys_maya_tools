#Find Meshes with no Materials Assigned

#2022-07-20 Abby Cohn
#QC tool to check if objects in Geometry group have no material assigned

#imports
import pymel.core as pm

def check_func(*args):
    
    geometryMeshes = []
    noMats = []

    meshes = pm.ls(type = 'mesh', noIntermediate = True)

    for m in meshes:
        name = m.longName().split("|")
        if "Geometry" in name and "RsProxy" not in name:
            geometryMeshes.append(m)

    for gm in geometryMeshes:
        shadingEngine = pm.listConnections(gm, type = 'shadingEngine')
        if not shadingEngine:
            noMats.append(gm)
                 
    if noMats:
        print(noMats)
        return noMats
