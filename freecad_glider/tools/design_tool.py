from __future__ import division

from PySide import QtGui, QtCore
import numpy as np
import FreeCAD as App

from ._tools import BaseTool, input_field, text_field
from .pivy_primitives_new_new import coin, Line, Marker, Container, vector3D

print("reloaded")
# idea: draw lines between ribs and fill the panels with color
# only straight lines, no curves

# 1: draw shape(ribs, outline) + switcher front and back
# 2: event handler to pin to raster
# 3: line creation, selection
# 4: panels filling (color) + leading edge
# 5: delete  ?
# 6: editing ?

class DesignTool(BaseTool):
    def __init__(self, obj):
        BaseTool.__init__(self, obj, widget_name="DesignTool")
        self.cpcs = []
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
        _shape = self.ParametricGlider.shape.get_shape()
        front = list(map(vector3D, _shape.front))
        back = list(map(vector3D, _shape.back))
        ribs = zip(front, back)

        self.shape += Line(front)
        self.shape += Line(back)
        self.shape += Line([back[0], front[0]])
        self.shape += Line([back[-1], front[-1]])
        self.shape += list(map(Line, ribs))

    def draw_panels(self):
        pass
