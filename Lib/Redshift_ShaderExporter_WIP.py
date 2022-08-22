import subprocess
import os
import time
from os import listdir
from os.path import isfile
import pymel.core as pm
import maya.cmds as cmds

# 2021-07-17 Abby Cohn 
# Shader Exporter

# This tool allows the user to export shaders from a scene to a directory of their choosing.
# Code finds all shaders in the scene & UI is created with shaders listed.
# File path is default root/Data, but can be updated by the user.
# "Export" button will export every checked shader to the chosen directory.
# If file already exists in directory, the old files will be archived in an "Old" folder. 

path = os.path.abspath(pm.workspace(q=1, rd=1))
path = os.path.join(path, 'Scenes')
scn = os.path.abspath(pm.sceneName())
suffix = scn.split('\\')
if "O:\\Prod" in scn:
    filePath = os.path.join(path, suffix[5], suffix[6], "Data")
else:
    filePath = os.path.join(path, suffix[9], suffix[10], "Data")
checkList = {}

# get asset shader list
# if shaders are connected to rsMatBlender, the blend is listed as the the primary shader in the network
def getShaders():
    rsMats = pm.ls(type = 'RedshiftMaterial', ro=False)
    rsVols = pm.ls(type = 'RedshiftVolume', ro=False)
    rsBlends = pm.ls(type = 'RedshiftMaterialBlender', ro=False)
    assetShaders = rsMats + rsVols + rsBlends

    if len(rsBlends) > 0:
        blendHist = [b.listHistory() for b in rsBlends]
        nodeHist = [node for lis in blendHist for node in lis if node.nodeType() == 'RedshiftMaterial' or node.nodeType() == 'RedshiftVolume']
        assetShaders = [shader for shader in assetShaders if shader not in nodeHist]

    return assetShaders

# button command for file path text field
# fills field with selected path
def selectFilePath(*args):
    global filePath
    filePath = cmds.textFieldButtonGrp('fileText', q=True, text=True)
    filePath = cmds.fileDialog2(dialogStyle=2, fileMode=2, startingDirectory=filePath)
    filePath = os.path.abspath(filePath[0])
    cmds.textFieldButtonGrp('fileText', edit=1, text=str(filePath), bc = selectFilePath)
    cmds.setParent('..')
    
# archive old shader files to prevent loss of previous work    
def archiveFiles(currShader, currPath, currExport):
    if os.path.exists(currExport):
        toMove = currPath+'\\Old\\'
        if not os.path.exists(toMove):
            os.mkdir(toMove)
        print('Archiving previously exported '+str(currShader)+'.')
        currSpecifier = os.path.getmtime(currExport)
        currTime = time.strftime('_%Y_%m_%d_%H_%M_%S', time.localtime(currSpecifier))
        newPath = toMove+str(currShader)+currTime+'.ma'
        try:
            cmds.sysFile(currExport, rename=newPath)
        except Exception as f:
            print(f)
        
# invoked when user presses export button
# gather all checked shaders and export to individual .ma files
def exportShaders(*args):
     global filePath
     filePath = cmds.textFieldButtonGrp('fileText', q=True, text=True)
     if not os.path.exists(filePath):
         print("Invalid file path")
         
     for k,v in checkList.items():
            if pm.checkBox(v,q=1,v=1):

                pm.select(clear=True)
                sg = pm.listConnections(k, t='shadingEngine')
                if (len(sg) == 0):
                    downstreamNodes = ((pm.hyperShade(ldn = k)))
                    sg = [i for i in downstreamNodes if pm.objectType(i) == 'shadingEngine']
                    try:
                        sg = sg[0]
                    except Exception as fe:
                        print(fe)
                        print("No shading engine found.")
                else:
                    sg = sg[0]

                k.select(ne=True)
                pm.select(sg, add=True, ne=True)
                toExport = filePath+'\\'+k+'.ma'

                archiveFiles(k, filePath, toExport)
                    
                try:
                    cmds.file(toExport, es=1, typ="mayaAscii", op="v=0")
                    print(str(k)+" exported!")
                except Exception as f:
                    print(f)

                pm.select(clear=True)

# create User Interface
def createUI(shaderList):
    interfaceName = 'ShaderExporter'

    if cmds.window(interfaceName, exists=True):
        cmds.deleteUI(interfaceName)

    win = cmds.window(interfaceName, w=500, title="TREK Shader Exporter", bgc=[.25,.25,.25])
    scroll = cmds.scrollLayout(childResizable=True)
    row = cmds.rowColumnLayout(numberOfColumns=1, bgc=[.25,.25,.25], adj=1)
    
    cmds.text(align='center',h=120, l = "\tSHADER EXPORTER\n\
    - Deselecting the shader will remove it from the export queue.\n\
    - Select your file path.\n\
    - Export! :)")

    for shader in shaderList:
        checkList[shader] = (pm.checkBox(v=1, l=str(shader), h=20))

    cmds.separator(h=30, style='none')
    row2 = cmds.rowColumnLayout(numberOfColumns=3, bgc=[.25,.25,.25], adj=1)
    fileText = cmds.textFieldButtonGrp('fileText', adj=2, cal=(1, "center"), cw2=(10, 150), fileName=filePath, label='Directory', 
                                        buttonLabel='...', buttonCommand=selectFilePath)
    cmds.button(label="Export", align="center", command=exportShaders)
    cmds.setParent("..")
    
    cmds.showWindow()

# gather shaders and proceed if shaders are found
assetShaderList = getShaders()
if len(assetShaderList) > 0:
    createUI(assetShaderList)
else:
    print("no valid shaders found")
    

