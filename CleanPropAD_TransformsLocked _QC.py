# Prop ADs have Locked Transforms

#2022-07-20 Abby Cohn
#QC tool to check if prop AD referenced have locked transforms and unlocks them if they do

#imports
import pymel.core as pm

# Required
__desc__ = 'Prop ADs Have Locked Transforms'

# Required Functions
def check_func(*args):
    out = []
    for x in list(set([x.getTransform() for x in pm.ls(type='assemblyReference') if 'Props|' in x.longName()])):
        _ = [x.translateX.isLocked(),
             x.translateY.isLocked(),
             x.translateZ.isLocked(),
             x.rotateX.isLocked(),
             x.rotateY.isLocked(),
             x.rotateZ.isLocked(),
             x.scaleX.isLocked(),
             x.scaleY.isLocked(),
             x.scaleZ.isLocked()]
        if len(_) > 0:
            out.append(x)
    out = list(set(out))
    if out:
        print(out)
        return(out)
    return True


def fix_func(*args):
    result = check_func()
    if result != True:
        for x in result:
            try:
                x.translateX.unlock()
                x.translateY.unlock()
                x.translateZ.unlock()
                x.rotateX.unlock()
                x.rotateY.unlock()
                x.rotateZ.unlock()
                x.scaleX.unlock()
                x.scaleY.unlock()
                x.scaleZ.unlock()
            except Exception:
                pass
    return check_func()

#run this line to print out problem ADs
check_func()
#run both lines together to fix them!
fix_func()