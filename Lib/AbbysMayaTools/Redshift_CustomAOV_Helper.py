import pymel.core as pm
import maya.cmds as cmds

#2021-06-24 Abby Cohn 
#AOV Helper

#This script allows user to add custom AOVs to the networks of all shading groups selected. 
#Custom AOV Trigger will be created or updated with new enums if it already exists.

#   - user must select all shading groups they want to add AOVs to
#   - there must be a transform control in the scene for the CustomAOVTrigger
#   ***if using this in a set section, it's best to have props in locator representation, 
#      so there is only 1 transform present
#   - if it doesn't look like the AOV nodes have been added, graph each shader to check
#   - the code will throw an error if: a selected shading network already has an AOV node or 
#     no shading groups are selected

#WHAT CODE IS DOING
        #1. create rsStoreColorToAOV node & name it "ShaderName_Lights"
        #2. create rsStoreColorToAOV input that has the same name and connect emisson color 
        #   or file to input (the code should recognize both)
        #3. connect rs shader as beauty and connect rsStoreColorToAOV to rs Surface Shader on SG
        #4. stores list of new AOVs and will create a CustomAOVTrigger on the transform with them 
        #5. if CustomAOVTrigger already exists, the new AOVs will be added to the enum list

#sets emission with either the texture or color if there is no texture input
def setEmission(currShader, currNode, *args):
    emiss = currShader.emission_color
    emissList = emiss.listConnections()
    e = len(emissList)
    
    if e >= 1: 
        try:
            pm.connectAttr((emissList[0].outColor), (currNode.aov_input_list[0].input), f=1)
        except Exception as f:
            print(f)
    else:
        rgb = pm.getAttr(emiss)
        try:
            pm.setAttr((currNode.aov_input_list[0]+'.input'), (rgb))
        except Exception as f:
            print(f)

#creates node, name, and connects emission input        
def createAOV(shadingGroup, *args):
    n = str(shadingGroup)
    n = n.replace('SG', '')

    rsMat = shadingGroup.rsSurfaceShader
    surfaceList = rsMat.listConnections()

    for c in shadingGroup.listConnections():
        if pm.nodeType(c) == 'RedshiftStoreColorToAOV':
            print("CustomAOV already exists for this shader")
            return None
    #if there is no viewportShader there is nothing connected to rsSurfaceShader, 
    #so we grab the SurfaceShader
    if len(surfaceList) < 1:
        rsMat = shadingGroup.surfaceShader
        surfaceList = rsMat.listConnections()
    if len(surfaceList) < 1:
        print("No shaders found")
        return None

    rsSurface = surfaceList[0]

    #create the rsStoreColorToAOV
    try:
        newNode = pm.shadingNode('RedshiftStoreColorToAOV', name = n+"Lights", asTexture = True)
        pm.connectAttr((rsSurface.outColor), (newNode.beauty_input), f=1)
        pm.setAttr((newNode.aov_input_list[0]+'.name'), (n+"Lights"))
        setEmission(rsSurface, newNode)
        pm.connectAttr((newNode.outColor), (shadingGroup.rsSurfaceShader), f=1)
    except Exception as f:
        print(f)
        
    return (n+"Lights")

#loop over all SGs
def createAllAOVs(*args):
    if len(SGs) > 0:
        for shadingGroup in SGs:
            newName = createAOV(shadingGroup)
            if newName is not None:
                AOV_List.append(newName)
    else:
        print("No shading groups seleced")

#adding to custom attr that already exists
def addToCustomAttr(assetNode, attr, newList):
    enums = pm.attributeQuery(attr, node=str(assetNode), listEnum=True)[0]
    enums = enums.split(":")

    #check list for duplicates
    combinedList = list(set(enums+newList))
    pm.deleteAttr(str(assetNode)+'.'+attr)
    pm.addAttr(niceName='CustomAOVTrigger', longName='CustomAOVTrigger', 
                attributeType='enum', en=combinedList, keyable=False)

#add to custom AOVTrigger
def addToCustomAOVTrigger(*args):
    curves = pm.ls(type = 'nurbsCurve')

    for c in curves:
        c_string = str(c)
        if '_Transform' in c_string:
            assetTransform = c
            break
        else:
            continue

    if '_Transform' in c_string:
        print("Transform Found, Adding AOVs")
    else:
        print("No Transform Found")

    assetTransform = assetTransform.replace('Shape', '')
    pm.select(assetTransform)

    if pm.hasAttr(pm.PyNode(assetTransform), 'CustomAOVTrigger', checkShape=True):
        try:
            addToCustomAttr(assetTransform, 'CustomAOVTrigger', AOV_List)
        except Exception as f:
            print(f)
    else:
        print("no CustomAOVTrigger found, creating one")

        try:
            pm.addAttr(niceName='CustomAOVTrigger', longName='CustomAOVTrigger', 
                        attributeType='enum', en=AOV_List, keyable=False)
        except Exception as f:
            print(f)


#Gather Shading Groups
def gatherAndRun(*args):
    global SGs
    SGs = pm.selected()
    global AOV_List
    AOV_List = []

    createAllAOVs()

    if len(AOV_List) > 0:
        addToCustomAOVTrigger()
    else:
        print("No new AOVs")

