from __future__ import division

from PySide import QtGui, QtCore
import numpy as np
import FreeCAD as App

from ._tools import BaseTool, input_field, text_field
from .pivy_primitives_new_new import coin, Line, Marker, Container, vector3D


# idea: draw lines between ribs and fill the panels with color
# only straight lines, no curves
# later create some helpers to generate parametric cuts

# 1: draw shape(only half!, ribs, outline) + switcher front and back
# 2: event handler to pin to raster 
# 3: line creation, selection
# 4: panels filling (color) + leading edge
# 5: delete  ?
# 6: editing ?

class DesignTool(BaseTool):
    def __init__(self, obj):
        BaseTool.__init__(self, obj, widget_name="DesignTool")
        self.cpcs = []
        _shape = self.ParametricGlider.shape.get_shape()
        self.front = list(map(vector3D, _shape.front))
        self.back = list(map(vector3D, _shape.back))
        self.ribs = zip(self.front, self.back)
        self.setup_widget()
        self.setup_pivy()

    def setup_widget(self):
        """set up the qt stuff"""
        self.Qtoggle_side = QtGui.QPushButton("show lower side")
        self.layout.setWidget(0, input_field, self.Qtoggle_side)

    def setup_pivy(self):
        """set up the scene"""
        self.shape = coin.SoSeparator()
        self.task_separator += self.shape
        self.draw_shape()

    def draw_shape(self):
        """ draws the shape of the glider"""
        self.shape += Line(self.front)
        self.shape += Line(self.back)
        self.shape += Line([self.back[0], self.front[0]])
        self.shape += Line([self.back[-1], self.front[-1]])
        self.shape += list(map(Line, self.ribs))

    def draw_panels(self):
        pass


class CutPoint(Marker):
    # this point should prevent jumping of the cutlines
    # no rib changes are possible
    def __init__(self, points):
        Marker.__init__(self, points, True)


class CutLine(Line):
    def __init__(self, point1, point2):
        super(CutLine, self).__init__([point1.pos, point2.pos], dynamic=True)
        self.point1 = point1
        self.point2 = point2
        self.point1.on_drag.append(self.update_Line)
        self.point2.on_drag.append(self.update_Line)
        self.drawstyle.lineWidth = 1.
        self.target_length = 1.
        self.line_type = "default"
        self.layer = ""

    def update_Line(self):
        self.points = [self.point1.pos, self.point2.pos]

    def drag(self, mouse_coords, fact=1.):
        self.point1.drag(mouse_coords, fact)
        self.point2.drag(mouse_coords, fact)

    @property
    def drag_objects(self):
        return [self.point1, self.point2]

    @property
    def points(self):
        return self.data.point.getValues()

    @points.setter
    def points(self, points):
        p = [[pi[0], pi[1], pi[2] - 0.001] for pi in points]
        self.data.point.setValue(0, 0, 0)
        self.data.point.setValues(0, len(p), p)

    def check_dependency(self):
        if self.marker1._delete or self.marker2._delete:
            self.delete()
