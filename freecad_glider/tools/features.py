from ._glider import OGBaseObject, OGGliderVP

from openglider.airfoil.profile_2d import Profile2D
from openglider.glider.rib import SingleSkinRib
import numpy as np
import copy

class BaseFeature(OGBaseObject):
    def __init__(self, obj, parent):
        self.obj = obj
        obj.addProperty("App::PropertyLink", "parent", "not yet", "docs")
        obj.parent = parent
        super(BaseFeature, self).__init__(obj)

    def drawGlider(self, call_parent=True):
        if not self.obj.ViewObject.Visibility:
            self.obj.ViewObject.Proxy.recompute = True
            if call_parent:
                self.obj.parent.Proxy.drawGlider()
        else:
            self.obj.ViewObject.Proxy.recompute = True
            self.obj.ViewObject.Proxy.updateData()
            if call_parent:
                self.obj.parent.Proxy.drawGlider()

    def getGliderInstance(self):
        """adds stuff and returns changed copy"""
        return copy.deepcopy(self.obj.parent.Proxy.getGliderInstance())

    def getParametricGlider(self):
        """returns top level parametric glider"""
        return self.obj.parent.Proxy.getParametricGlider()

    def setParametricGlider(self, obj):
        """sets the top-level glider2d and recomputes the glider3d"""
        self.obj.parent.Proxy.setParametricGlider(obj)

    def getRoot(self):
        """return the root freecad obj"""
        return self.obj.parent.Proxy.getRoot()

    def onDocumentRestored(self, obj):
        self.obj = obj
        self.obj.parent.Proxy.onDocumentRestored(self.obj.parent)
        if not self.obj.ViewObject.Visibility:
            self.obj.ViewObject.Proxy.recompute = True
        else:
            self.obj.ViewObject.Proxy.recompute = True
            self.obj.ViewObject.Proxy.updateData(prop="Visibility")

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
        for i, rib in enumerate(glider.ribs):
            if i in self.obj.ribs:
                rib.profile_2d = airfoil
        return glider

    def execute(self, fp):
        self.drawGlider()


class BallooningFeature(BaseFeature):
    def __init__(self, obj, parent):
        super(BallooningFeature, self).__init__(obj, parent)
        obj.addProperty("App::PropertyIntegerList", "cells", "not yet", "docs")
        obj.addProperty("App::PropertyInteger", "ballooning", "not yet", "docs")

    def getGliderInstance(self):
        glider = copy.deepcopy(self.obj.parent.Proxy.getGliderInstance())
        ballooning = self.obj.parent.Proxy.getParametricGlider().balloonings[self.obj.ballooning]
        for i, cell in enumerate(glider.cells):
            if i in self.obj.cells:
                cell.ballooning = ballooning
        return glider

    def execute(self, fp):
        self.drawGlider()


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
        for rib in enumerate(glider.ribs):
            rib.profile_2d = Profile2D(self.apply(rib.profile_2d._data, x1, x2, x3, y_add))
        return glider

    def execute(self, fp, *args):
        self.obj.ViewObject.Proxy.updateData()


class SingleSkinRibFeature(BaseFeature):
    def __init__(self, obj, parent):
        super(SingleSkinRibFeature, self).__init__(obj, parent)
        obj.addProperty("App::PropertyIntegerList", "ribs", "not yet", "docs")
        obj.addProperty("App::PropertyFloat", "height", "not yet", "docs").height = 0.5
        obj.addProperty("App::PropertyFloat", "att_dist", "not yet", "docs").att_dist = 0.1
        obj.addProperty("App::PropertyInteger", "num_points", "accuracy", "number of points").num_points = 20

    def getGliderInstance(self):
        glider = copy.deepcopy(self.obj.parent.Proxy.getGliderInstance())
        new_ribs = []
        single_skin_par = {"att_dist": self.obj.att_dist, 
                           "height": self.obj.height,
                           "num_points": self.obj.num_points}

        for i, rib in enumerate(glider.ribs):
            if i in self.obj.ribs:
                if not isinstance(rib, SingleSkinRib):
                    new_ribs.append(SingleSkinRib.from_rib(rib, single_skin_par))
                else:
                    rib.single_skin_par = single_skin_par
                    new_ribs.append(rib)
            else:
                new_ribs.append(rib)
        glider.replace_ribs(new_ribs)
        return glider

    def execute(self, fp):
        self.drawGlider()