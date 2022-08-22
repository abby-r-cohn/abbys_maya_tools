import maya.cmds as cmds
import pymel.core as pm

# 2022-07-31 Abby Cohn 
# Create Follow Attribute

#This script allows the user to create a follow (transform space) attribute on a Ctrl of their choosing.
#The list of possible transform spaces include Master, COG, Transform, and World.

#Button Command to Create Follow Attribute
def makeFollowAttr(*args):
    
    global currCtrl
    currCtrl = pm.textField("AddAttributeTo", q=True, tx=True)
    currCtrl = pm.PyNode(currCtrl)
    global masterCtrl
    masterCtrl = pm.textField("Master", q=True, tx=True)
    COG_Ctrl = pm.textField("COG", q=True, tx=True)
    transformCtrl = pm.textField("Transform", q=True, tx=True)
    
    if not currCtrl:
        print("No control chosen.")

    global enums
    enums = {}
    if str(masterCtrl):
        enums["Master"] = pm.PyNode(masterCtrl)
    if str(COG_Ctrl):
        enums["COG"] = pm.PyNode(COG_Ctrl)
    if str(transformCtrl):
        enums["Transform"] = pm.PyNode(transformCtrl)
    if worldAttr.getValue():
        enums["World"] = True

    try:
        currCtrl.addAttr('Follow', attributeType='enum', en=enums.keys(),
                keyable=True, writable=True, readable=True)
    except Exception as f:
        print(f)
    print("code continuing!")

#adding constraints to Ctrl Group
def addConstraints(*args):

    toConstrain = pm.textField("ToConstrain", q=True, tx=True)

    if not toConstrain:
        print("No group to constrain chosen.")

    toConstrain = pm.PyNode(toConstrain)
    drivers = enums.values()
    global constraints
    #dictionary of ctrls & their constraints
    constraints = {}

    for d in drivers:
        if d != True and "COG" in str(d):
            COG_relatives = (d.listRelatives(children=True, noIntermediate = True))
            COG_null = [x for x in COG_relatives if "COG_Null" in str(x)]
            COG_null = COG_null[0]
            currCon = [pm.parentConstraint(COG_null, toConstrain, mo=1), 
                pm.scaleConstraint(COG_null, toConstrain, mo=1)]
            constraints[d] = currCon
        elif d != True:
            currCon = [pm.parentConstraint(d, toConstrain, mo=1), 
                pm.scaleConstraint(d, toConstrain, mo=1)]
            constraints[d] = currCon

#set driven keys on constraints
def setKeys(*args):
    driver = currCtrl.Follow

    if not driver:
        print("Follow attribute not yet created.")

    enumsList = driver.getEnums()

    weights = []

    for ctrl,cons in constraints.items(): 
        for c in cons:
            c = pm.PyNode(c)
            currWeights = c.getWeightAliasList()
            if currWeights not in weights:
                weights.append(c.getWeightAliasList())

    for e, i in enumsList.items():
        currName = str(e)
        currCtrl.setAttr('Follow', i)
        if "World" in currName:
            for w in weights:
                for k in w:
                    pm.setDrivenKeyframe(k, cd = driver, v=0, dv=i)
        elif "COG" in currName:
            for w in weights:
                for k in w:
                    if "COG" in str(k):
                        pm.setDrivenKeyframe(k, cd = driver, v=1, dv=i)
                    else:
                        pm.setDrivenKeyframe(k, cd = driver, v=0, dv=i)
        elif "Transform" in currName:
            for w in weights:
                for k in w:
                    if "Transform" in str(k):
                        pm.setDrivenKeyframe(k, cd = driver, v=1, dv=i)
                    else:
                        pm.setDrivenKeyframe(k, cd = driver, v=0, dv=i)
        elif "Master" in currName:
            for w in weights:
                for k in w:
                    if str(pm.PyNode(masterCtrl)) in str(k):
                        pm.setDrivenKeyframe(k, cd = driver, v=1, dv=i)
                    else:
                        pm.setDrivenKeyframe(k, cd = driver, v=0, dv=i)
        else:
            print"All enum names not found."


#Creating User Interface
def createUI(*args):

    if pm.window("Create_Follow",exists=1):
                pm.deleteUI("Create_Follow")
    Add_Follow_Attr = pm.window("Create_Follow",w=300,h=150,s=1,nde=1, t='Create Follow Attributes')
    pm.rowColumnLayout(numberOfColumns=1,adj=1)

    pm.text(align='center',h=120, l = "\tCREATE FOLLOW ATTRIBUTES.\n\
        1. Drag and drop the control you would like to add this attribute to.\n\
        2. Drag and drop items from outliner to desired enum fields.\n\
        3. If left blank, the specific enum will not be created.\n\
        4. Click the button to create the attribute.\n\
        5. Next, drag and drop the ctrl group you'd like to add constraints to.\n\
        6. Click the button to add constraints. \n\
        7. Finally, click the button to set the keys!")

    pm.text(label="Add Attribute To:", align='left')
    pm.textField('AddAttributeTo')
    pm.text(label="Master:", align='left')
    pm.textField('Master')
    pm.text(label="COG:", align='left')
    pm.textField('COG')
    pm.text(label="Transform:", align='left')
    pm.textField('Transform')
    global worldAttr
    worldAttr = pm.checkBox(v=1, l='World', h=20)
    pm.button(label="Create Follow Attribute", w=150, h=30, command=makeFollowAttr)
    pm.text(label="To Constrain:", align='left')
    pm.textField('ToConstrain')
    pm.button(label="Add Constraints", w=150, h=30, command=addConstraints)
    pm.button(label="Set Keys", w=150, h=30, command=setKeys)

    pm.showWindow(Add_Follow_Attr)
