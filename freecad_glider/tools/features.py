from ._glider import OGBaseObject, OGGliderVP

from openglider.airfoil.profile_2d import Profile2D
from openglider.glider.rib import SingleSkinRib
import numpy as np
import copy

class BaseFeature(OGBaseObject):
    def __init__(self, obj, parent):
        self.obj = obj
        obj.addProperty('App::PropertyLink', 'parent', 'not yet', 'docs')
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
        '''adds stuff and returns changed copy'''
        return copy.deepcopy(self.obj.parent.Proxy.getGliderInstance())

    def getParametricGlider(self):
        '''returns top level parametric glider'''
        return self.obj.parent.Proxy.getParametricGlider()

    def setParametricGlider(self, obj):
        '''sets the top-level glider2d and recomputes the glider3d'''
        self.obj.parent.Proxy.setParametricGlider(obj)

    def getRoot(self):
        '''return the root freecad obj'''
        return self.obj.parent.Proxy.getRoot()

    def onDocumentRestored(self, obj):
        self.obj = obj
        self.obj.parent.Proxy.onDocumentRestored(self.obj.parent)
        self.obj.ViewObject.Proxy.addProperties(self.obj.ViewObject)
        if not self.obj.ViewObject.Visibility:
            self.obj.ViewObject.Proxy.recompute = True
        else:
            self.obj.ViewObject.Proxy.recompute = True
            self.obj.ViewObject.Proxy.updateData(prop='Visibility')

    def __getstate__(self):
        return None

    def __setstate__(self, state):
        return None

    def execute(self, fp):
        self.drawGlider()

class RibFeature(BaseFeature):
    def __init__(self, obj, parent):
        super(RibFeature, self).__init__(obj, parent)
        obj.addProperty('App::PropertyIntegerList', 'ribs', 'not yet', 'docs')
        obj.addProperty('App::PropertyInteger', 'airfoil', 'not yet', 'docs')

    def getGliderInstance(self):
        glider = copy.deepcopy(self.obj.parent.Proxy.getGliderInstance())
        airfoil = self.obj.parent.Proxy.getParametricGlider().profiles[self.obj.airfoil]
        for i, rib in enumerate(glider.ribs):
            if i in self.obj.ribs:
                rib.profile_2d = airfoil
        return glider


class BallooningFeature(BaseFeature):
    def __init__(self, obj, parent):
        super(BallooningFeature, self).__init__(obj, parent)
        obj.addProperty('App::PropertyIntegerList', 'cells', 'not yet', 'docs')
        obj.addProperty('App::PropertyInteger', 'ballooning', 'not yet', 'docs')

    def getGliderInstance(self):
        glider = copy.deepcopy(self.obj.parent.Proxy.getGliderInstance())
        ballooning = self.obj.parent.Proxy.getParametricGlider().balloonings[self.obj.ballooning]
        for i, cell in enumerate(glider.cells):
            if i in self.obj.cells:
                cell.ballooning = ballooning
        return glider


class SharkFeature(BaseFeature):
    def __init__(self, obj, parent):
        super(SharkFeature, self).__init__(obj, parent)
        obj.addProperty('App::PropertyIntegerList', 'ribs', 'not yet', 'docs')
        obj.addProperty('App::PropertyFloat', 'x1', 'shark-nose', 'distance')
        obj.addProperty('App::PropertyFloat', 'x2', 'shark-nose', 'distance')
        obj.addProperty('App::PropertyFloat', 'x3', 'shark-nose', 'distance')
        obj.addProperty('App::PropertyFloat', 'y_add', 'shark-nose', 'amount')
        obj.addProperty('App::PropertyInteger', 'type', 'not yet', '0-> linear, 1->quadratic')
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


class SingleSkinRibFeature(BaseFeature):
    def __init__(self, obj, parent):
        super(SingleSkinRibFeature, self).__init__(obj, parent)
        obj.addProperty('App::PropertyIntegerList',
                        'ribs', 'not yet', 'docs')
        self.add_properties()

    def getGliderInstance(self):
        glider = copy.deepcopy(self.obj.parent.Proxy.getGliderInstance())
        new_ribs = []
        self.add_properties()

        single_skin_par = {'att_dist': self.obj.att_dist,
                           'height': self.obj.height,
                           'num_points': self.obj.num_points,
                           'le_gap': self.obj.le_gap,
                           'te_gap': self.obj.te_gap,
                           'double_first': self.obj.double_first}

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

    def add_properties(self):
        if not hasattr(self.obj, 'height'):
            obj.addProperty('App::PropertyFloat', 'height', 
                            'not yet', 'docs').height = 0.5
        if not hasattr(self.obj, 'att_dist'):
            obj.addProperty('App::PropertyFloat', 'att_dist', 
                        'not yet', 'docs').att_dist = 0.1
        if not hasattr(self.obj, 'num_points'):
            obj.addProperty('App::PropertyInteger', 'num_points', 
                        'accuracy', 'number of points').num_points = 20
        if not hasattr(self.obj, 'le_gap'):
            self.obj.addProperty('App::PropertyBool', 'le_gap', 
                                 'not_yet', 'should the leading edge match the rib').le_gap = True
        if not hasattr(self.obj, 'te_gap'):
            self.obj.addProperty('App::PropertyBool', 'te_gap', 
                                 'not_yet', 'should the leading edge match the rib').te_gap = True
        if not hasattr(self.obj, 'double_first'):
            self.obj.addProperty('App::PropertyBool', 'double_first',
                'not yet', 'this is for double a lines').double_first = False


class FlapFeature(BaseFeature):
    def __init__(self, obj, parent):
        super(FlapFeature, self).__init__(obj, parent)
        self.add_properties()


    def add_properties(self):
        if not hasattr(self.obj, 'flap_begin'):
            self.obj.addProperty('App::PropertyFloat', 'flap_begin',
                'flap', 'where should the flapping effect start')
            self.obj.flap_begin = 0.95
        if not hasattr(self.obj, 'flap_amount'):
            self.obj.addProperty('App::PropertyFloat', 'flap_amount', 'flap', 'how much flapping')
            self.obj.flap_amount = 0.0

    def getGliderInstance(self):
        glider = copy.deepcopy(self.obj.parent.Proxy.getGliderInstance())
        new_ribs = []
        self.add_properties()

        for i, rib in enumerate(glider.ribs):
            rib.profile_2d.set_flap(self.obj.flap_begin, self.obj.flap_amount)
        return glider