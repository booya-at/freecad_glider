from ._glider import OGBaseObject, OGGliderVP

from openglider.airfoil.profile_2d import Profile2D
import numpy as np
import copy

class BaseFeature(OGBaseObject):
    def __init__(self, obj, parent):
        self.obj = obj
        obj.addProperty("App::PropertyLink", "parent", "not yet", "docs")
        obj.parent = parent
        super(BaseFeature, self).__init__(obj)

    def getGliderInstance(self):
        return copy.deepcopy(self.obj.parent.Proxy.getGliderInstance())

    def setGliderInstance(self, obj):
        self.obj.parent.Proxy.setGliderInstance(obj)

    def getParametricGlider(self, obj):
        return self.obj.parent.getParametricGlider()

    def getParametricGlider(self):
        return self.obj.parent.Proxy.getParametricGlider()

    def setParametricGlider(self, obj):
        self.obj.parent.Proxy.setParametricGlider(obj)

    def  onDocumentRestored(self, obj):
        self.obj = obj
        obj.ViewObject.Proxy._updateData(obj.ViewObject)


    def __getstate__(self):
        return None

    def __setstate__(self, state):
        return None


class RibFeature(BaseFeature):
    def __init__(self, obj, parent):
        super(RibFeature, self).__init__(obj, parent)
        obj.addProperty("App::PropertyIntegerList", "ribs", "not yet", "docs")
        obj.addProperty("App::PropertyInteger", "airfoil", "not yet", "docs")

    def getGliderInstance(self):
        glider = copy.deepcopy(self.obj.parent.Proxy.getGliderInstance())
        airfoil = self.obj.parent.Proxy.getParametricGlider().profiles[self.obj.airfoil]
        print(airfoil)
        # for rib in glider.ribs:
        #     print(dir(rib.profile_2d = Profile2D(airfoil)))
        return glider

    def execute(self, fp, *args):
        print("execute")


class CellFeature(BaseFeature):
    def __init__(self, obj, parent):
        super(CellFeature, self).__init__(obj, parent)
        obj.addProperty("App::PropertyIntegerList", "ribs", "not yet", "docs")
        obj.addProperty("App::PropertyInteger", "airfoil", "not yet", "docs")

    def getGliderInstance(self):
        glider = copy.deepcopy(self.obj.parent.Proxy.getGliderInstance())
        airfoil = self.obj.parent.Proxy.getParametricGlider().profiles[self.obj.airfoil]
        print(airfoil)
        # for rib in glider.ribs:
        #     print(dir(rib.profile_2d = Profile2D(airfoil)))
        return glider

    def execute(self, fp, *args):
        print("execute")


class SharkFeature(BaseFeature):
    def __init__(self, obj, parent):
        super(SharkFeature, self).__init__(obj, parent)
        obj.addProperty("App::PropertyIntegerList", "ribs", "not yet", "docs")
        obj.addProperty("App::PropertyFloat", "x1", "shark-nose", "distance")
        obj.addProperty("App::PropertyFloat", "x2", "shark-nose", "distance")
        obj.addProperty("App::PropertyFloat", "x3", "shark-nose", "distance")
        obj.addProperty("App::PropertyFloat", "y_add", "shark-nose", "amount")
        obj.addProperty("App::PropertyInteger", "type", "not yet", "0-> linear, 1->quadratic")
        obj.x1 = 0.1
        obj.x2 = 0.11
        obj.x3 = 0.5
        obj.y_add = 0.1

    def apply(self, airfoil_data, x1, x2, x3, y_add):
        data = []
        for x, y in copy.copy(airfoil_data):
            if y < 0:
                if x > x1 and x < x2:
                    y -= y_add * (x - x1) / (x2 - x1)  # here any function
                elif x > x2 and x < x3:
                    y -= y_add * (x3 - x) / (x3 - x2)  # here another function
            data.append([x, y])
        return np.array(data)

    def getGliderInstance(self):
        x1, x2, x3, y_add =  self.obj.x1, self.obj.x2, self.obj.x3, self.obj.y_add
        from openglider.airfoil.profile_2d import Profile2D
        glider = copy.deepcopy(self.obj.parent.Proxy.getGliderInstance())
        for rib in glider.ribs:
            rib.profile_2d = Profile2D(self.apply(rib.profile_2d._data, x1, x2, x3, y_add))
        return glider

    def execute(self, fp, *args):
        self.obj.ViewObject.Proxy.updateData()