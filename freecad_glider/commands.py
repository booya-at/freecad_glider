import tools
import FreeCAD


def getActiveGlider():
    obj = FreeCAD.ActiveDocument.ActiveObject
    if hasattr(obj, "glider_instance"):
        return obj


def getParametricGlider():
    return getActiveGlider().glider_2d


def getGlider():
    return getActiveGlider().glider_instance

createGlider = tools.CreateGlider.create_glider
