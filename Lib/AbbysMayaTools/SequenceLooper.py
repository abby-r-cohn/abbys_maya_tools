import pymel.core as pm
import os
import subprocess

#2022-080-04 Abby Cohn
#Maya Sequence Looper

#Loop Image and RsProxy sequences easily

#user must select node they want to loop, either proxy mesh instance or file texture node
#sequence may start at zero or 1 and sequence will be set up to begin at 0 on the timeline

def defineSource(sel, *args):
	sel = sel[0]
	nodeSource = pm.nodeType(sel)
	if nodeSource == "file":
		return getImageFiles(sel)
	elif nodeSource == "transform":
		return getProxyFiles(sel)
	else:
		print("Incorrect source")

def getImageFiles(toLoop, *args):

	if not toLoop:
		print("No file node selected")

	#set use image sequence to ON if not already in use
	if not toLoop.getAttr("useFrameExtension"):
		toLoop.setAttr("useFrameExtension", 1)

	#gather files
	seqFile = toLoop.getAttr("fileTextureName")
	path = str(seqFile)
	path = os.path.dirname(os.path.abspath(path))
	files = [f for f in os.listdir(path) if not os.path.isdir(f)]
	return files, toLoop

def getProxyFiles(proxyGeo, *args):

	proxyGeo = pm.PyNode(proxyGeo)
	shape = (proxyGeo.listRelatives()[0])
	shapeNode = pm.PyNode(shape)
	shapeConnects = shapeNode.listConnections()
	inMesh = [i for i in shapeConnects if i.nodeType() == "RedshiftProxyMesh"]
	if not inMesh:
		print("No Proxy node connected")

	inMesh = inMesh[0]

	#set use proxy sequence to ON if not already in use
	if not inMesh.getAttr("useFrameExtension"):
		inMesh.setAttr("useFrameExtension", 1)

	#gather files
	seqFile = inMesh.getAttr("fileName")
	path = str(seqFile)
	path = os.path.dirname(os.path.abspath(path))
	files = [f for f in os.listdir(path) if not os.path.isdir(f)]
	return files, inMesh


#get highest number in sequnece
def editExpression(theFiles, seq, *args):
	frameList = []
	highest = 0
	for currFile in theFiles:
		i = currFile.split(".")
		currNum = i[-2]
		currNumUnicode = unicode(currNum, 'utf-8')
		if currNumUnicode.isnumeric():
			frameList.append(int(currNumUnicode))

	highest = max(frameList)
	lowest = min(frameList)
	imageNum = seq.frameExtension
	imageCons = imageNum.listConnections()
	if lowest == 0:
	    toAdd = 1
	elif lowest == 1:
	    toAdd = 0
	else:
	    print ("Sequence must start at 0 or 1")
	
	if len(imageCons) > 0:
	    imageExp = imageCons[0]
	    currExp = imageExp.getExpression()
	    try:
	    	imageExp.setExpression(str(imageNum)+ ' = (frame' + ' % (' + str(highest)
	    							+ "+" + str(toAdd) + ")) + " + str(lowest))
	    except Exception as f:
    		print(f)
	else:
		try:
			pm.expression(s = str(imageNum)+ ' = (frame' + ' % (' + str(highest)
							+ "+" + str(toAdd) + ")) + " + str(lowest))
		except Exception as f:
			print(f)

def loop(*args):
	currSequenceFiles = defineSource(pm.selected())
	editExpression(currSequenceFiles[0], currSequenceFiles[1])
