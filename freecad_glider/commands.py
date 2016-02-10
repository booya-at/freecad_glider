import tools
import FreeCAD


def getActiveGlider():
    obj = FreeCAD.ActiveDocument.ActiveObject
    if hasattr(obj, "GliderInstance"):
        return obj


def getParametricGlider():
    return getActiveGlider().ParametricGlider


def getGlider():
    return getActiveGlider().GliderInstance

createGlider = tools.CreateGlider.create_glider
