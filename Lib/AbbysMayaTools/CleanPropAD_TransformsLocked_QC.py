# Prop ADs have Locked Transforms

#2022-07-20 Abby Cohn
#QC tool to check if prop AD references have locked transforms and unlocks them if they do

#imports
import pymel.core as pm

def check_func(*args):

    adList = []
    ads = pm.ls(type='assemblyReference')

    for a in ads:
        if 'Props|' in a.longName():
            curr_locked = [a.translateX.isLocked(),
                 a.translateY.isLocked(),
                 a.translateZ.isLocked(),
                 a.rotateX.isLocked(),
                 a.rotateY.isLocked(),
                 a.rotateZ.isLocked(),
                 a.scaleX.isLocked(),
                 a.scaleY.isLocked(),
                 a.scaleZ.isLocked()]
            if len(set(curr_locked)) > 1 or curr_locked[0] == True:
                adList.append(a)
    if adList:
        print(adList)
        return(adList)
    return True


def fix_func(*args):

    checked = check_func()
    if checked != True:
        for a in checked:
            try:
                a.translateX.unlock()
                a.translateY.unlock()
                a.translateZ.unlock()
                a.rotateX.unlock()
                a.rotateY.unlock()
                a.rotateZ.unlock()
                a.scaleX.unlock()
                a.scaleY.unlock()
                a.scaleZ.unlock()
            except Exception as f:
                print(f)
