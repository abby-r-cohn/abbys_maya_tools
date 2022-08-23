import pymel.core as pm
import sys
sys.path.append(r'\\nickwest\nick\anim\Tools\ArtistCode\AbbyCohn\Lib')

import AbbysMayaTools
import AbbysMayaTools.Redshift_ShaderExporter as se
import AbbysMayaTools.Redshift_CustomAOV_Helper as aov
import AbbysMayaTools.FollowAttribute_Helper as follow
import AbbysMayaTools.SequenceLooper as loop
import AbbysMayaTools.CleanPropAD_TransformsLocked_QC as adUnlock
import AbbysMayaTools.Check_HasNoMaterialAssigned_QC as noMat
import AbbysMayaTools.Check_HasMultipleShapeNodes_QC as mShape

#Abby's Maya Toolbox

#2022-08-09 Abby Cohn

#Toolbox to hold custom tools and QC checks

#Creating User Interface
def createUI(*args):
	if pm.window("AbbysMayaTools",exists=1):
		pm.deleteUI("AbbysMayaTools")
	AbbysMayaTools = pm.window("AbbysMayaTools",w=300,h=100,s=1,nde=1, t="Abby's Maya Tools")
	pm.rowColumnLayout(numberOfColumns=1,adj=1)
	pm.text(align='center',h=50, l = "\tAbby's Maya Tools")
	seLaunch = pm.button(label="Redshift Shader Exporter", ann='Tool to help export and archive multiple redsift shaders from a single file.', command=se.gatherAndRun)
	aovLaunch = pm.button(label="Redshift AOV Helper", ann='Select Shading engines of networks to add AOVs to before running. Tool will add in custom note and attr.', command=aov.gatherAndRun)
	followLaunch = pm.button(label="Follow Attribute Helper", ann='Tool will help add in a transform space "Follow" toggle to a ctrl.', command=follow.createUI)
	loopLaunch = pm.button(label="Sequence Looper", ann='Select file texture node or proxy instance to loop.', command=loop.loop)
	adUnlockLaunch = pm.button(label="Clean ADs With Locked Transforms", ann='Tool will identify and unlock ADs that have any locked transforms.', command=adUnlock.fix_func)
	noMatLaunch = pm.button(label="Find Objects with no Mat Assigned", ann='Identify objects with no material assigned.', command=noMat.check_func)
	mShapeLaunch = pm.button(label="Find Objects with Multiple Shape Nodes", ann='Identify objects with multiple shape nodes.', command=mShape.check_func)

	pm.showWindow(AbbysMayaTools)

createUI()
