import pymel.core as pm
import maya.cmds as cmds
from PySide2 import QtWidgets
from PySide2 import QtCore
import maya.OpenMayaUI as omu
from shiboken2 import wrapInstance
import sys
import subprocess
import os
import time
from os import listdir
from os.path import isfile


#need to parent window to maya main window
def maya_main_window():
    ptr = omu.MQtUtil.mainWindow()
    return wrapInstance(long(ptr), QtWidgets.QWidget)

#extension of Qdialog Class
class ShdExpDialog(QtWidgets.QDialog):
    
    def __init__(self, parent=maya_main_window()):
        QtWidgets.QDialog.__init__(self, parent)
        self.setWindowTitle("Shader Exporter")
        self.setFixedSize(600,300)
        self.create_layout()
        self.create_connections()
        
    def create_layout(self):
    	self.break_box = QtWidgets.QCheckBox("Break Connections")
    	self.break_box.setChecked(True)
    	self.checklist_layout = QtWidgets.QVBoxLayout()
    	self.shdList = self.analyze_shaders()
    	self.filePath = self.get_initial_path()
    	self.path_edit = QtWidgets.QLineEdit(self.filePath)
    	self.path_edit.setAlignment(QtCore.Qt.AlignLeft)
    	self.path_button = QtWidgets.QPushButton("...")
        self.export_button = QtWidgets.QPushButton("Export")
        self.cancel_button = QtWidgets.QPushButton("Cancel")
        button_layout = QtWidgets.QHBoxLayout()
        button_layout.addWidget(self.path_edit)
        button_layout.addWidget(self.path_button)
        button_layout.addWidget(self.export_button)
        button_layout.addWidget(self.cancel_button)
        main_layout = QtWidgets.QVBoxLayout()
        main_layout.addWidget(self.break_box)
        main_layout.addLayout(self.checklist_layout)
        main_layout.addLayout(button_layout)
        self.setLayout(main_layout)
    
    def get_shaders(self):
		rsMats = pm.ls(type = 'RedshiftMaterial', ro=False)
		rsVols = pm.ls(type = 'RedshiftVolume', ro=False)
		rsBlends = pm.ls(type = 'RedshiftMaterialBlender', ro=False)
		assetShaders = rsMats + rsVols + rsBlends

		if len(rsBlends) > 0:
		    blendHist = [b.listHistory() for b in rsBlends]
		    nodeHist = [node for lis in blendHist for node in lis if node.nodeType() == 'RedshiftMaterial' or node.nodeType() == 'RedshiftVolume']
		    assetShaders = [shader for shader in assetShaders if shader not in nodeHist]

		global checkList
		checkList = {}

		for s in assetShaders:
			checkbox = QtWidgets.QCheckBox(str(s))
			checkbox.setChecked(True)
			self.checklist_layout.addWidget(checkbox)
			checkList[s] = (checkbox)

		print(checkList)
		return assetShaders

	#rig will not export with shader, unless there are place3d nodes
    def break_connections(self, currShader):
    	l = pm.listConnections(currShader, plugs=0)
    	h = pm.listConnections(currShader, plugs=1)
    	self.con_dict = {}

    	if len(h) > 0:
	    	for i in range(len(h)):
	    		curr_node = l[i]
	    		if pm.PyNode(curr_node).nodeType() == 'transform':
	    			curr_attr = h[i]
	    			curr_cons = pm.listConnections(curr_attr, plugs=1)
	    			self.con_dict[curr_attr] = curr_cons[0]
	    			pm.disconnectAttr(curr_attr, curr_cons[0])

    #leave current file in an unaltered state by reattaching connections
    def reattach_connections(self, currShader):
	    print(currShader)
	    for k,v in self.con_dict.items():
			pm.connectAttr(k, v)

    def archive_files(self, currShader, currPath, currExport, *args):
	    if os.path.exists(currExport):
	        toMove = currPath+'\\Old\\'
	        if not os.path.exists(toMove):
	            os.mkdir(toMove)
	        print('Archiving previously exported '+str(currShader)+'.')
	        currSpecifier = os.path.getmtime(currExport)
	        currTime = time.strftime('_%Y_%m_%d_%H_%M_%S', time.localtime(currSpecifier))
	        newPath = toMove+str(currShader)+currTime+'.ma'
	        try:
	            pm.sysFile(currExport, rename=newPath)
	        except Exception as f:
	            print(f)

    def get_initial_path(self):
		path = os.path.abspath(pm.workspace(q=1, rd=1))
		path = os.path.join(path, 'Scenes')
		scn = os.path.abspath(pm.sceneName())
		suffix = scn.split('\\')

		if "O:\\Prod" in scn:
		    p = os.path.join(path, suffix[5], suffix[6], "Data")
		else:
		    p = os.path.join(path, suffix[9], suffix[10], "Data")
		return p

    def analyze_shaders(self):
		# gather shaders and proceed if shaders are found
		assetShaderList = self.get_shaders()

		if len(assetShaderList) > 0:
			pass
		else:
		    print("no valid shaders found")

    def create_connections(self):
        self.connect(self.export_button, QtCore.SIGNAL("clicked()"), self.export_shaders)
        self.connect(self.cancel_button, QtCore.SIGNAL("clicked()"), self.close_dialog)
        filePath = self.connect(self.path_button, QtCore.SIGNAL("clicked()"), self.update_path)

    def export_shaders(self):
		if not os.path.exists(self.filePath):
		    print("Invalid file path")
		 
		for k,v in checkList.items():
		    if v.checkState():

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
		        toExport = self.filePath+'\\'+k+'.ma'
		        print(toExport)

		        self.archive_files(k, self.filePath, toExport)
		        if self.break_box.checkState():
		        	self.break_connections(k)
		        try:
		            pm.exportSelected(toExport, typ="mayaAscii")
		            print(str(k)+" exported!")
		        except Exception as f:
		            print(f)
		        if self.break_box.checkState():
		        	self.reattach_connections(k)

		        pm.select(clear=True)
        
    def close_dialog(self):
        self.close()

    def update_path(self):
    	dir_path = QtWidgets.QFileDialog.getExistingDirectory(self, "Export to", self.path_edit.text())
    	print(dir_path)
    	self.path_edit.setText(dir_path)
    	self.filePath = dir_path
        

def gatherAndRun(*args):
    try:
        ui.close()
    except:
        pass
    dialog = ShdExpDialog()
    dialog.show()