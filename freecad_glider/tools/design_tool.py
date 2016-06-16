from __future__ import division

from PySide import QtGui, QtCore
import numpy as np
import FreeCAD as App

from ._tools import BaseTool, input_field, text_field
from .pivy_primitives_new_new import coin, Line, Marker, Container, vector3D


def refresh():
    pass


# idea: draw lines between ribs and fill the panels with color
# only straight lines, no curves
# later create some helpers to generate parametric cuts

# TODO

# switch upper lower      x
# add new line            
# save to dict            x
# set cut type
# q set position
# delete                  x


class DesignTool(BaseTool):
    def __init__(self, obj):
        super(DesignTool, self).__init__(obj, widget_name="DesignTool")
        self.side = "upper"

        # get 2d shape properties
        _shape = self.ParametricGlider.shape.get_shape()
        self.front = list(map(vector3D, _shape.front))
        self.back = list(map(vector3D, _shape.back))
        self.ribs = zip(self.front, self.back)
        CutLine.cuts_to_lines(self.ParametricGlider)

        # setup the GUI
        self.setup_widget()
        self.setup_pivy()

    def setup_widget(self):
        """set up the qt stuff"""
        self.Qtoggle_side = QtGui.QPushButton("show lower side")
        self.layout.setWidget(0, input_field, self.Qtoggle_side)

        self.tool_widget = QtGui.QWidget()
        self.tool_widget.setWindowTitle("object properties")
        self.tool_layout = QtGui.QFormLayout(self.tool_widget)
        self.form.append(self.tool_widget)

        self.Qcut_type = QtGui.QComboBox()
        self.Qcut_type.addItem("folded")
        self.Qcut_type.addItem("orthogonal")

        self.tool_layout.setWidget(0, text_field, QtGui.QLabel("cut type"))
        self.tool_layout.setWidget(0, input_field, self.Qcut_type)

        self.QPointPos = QtGui.QDoubleSpinBox()
        self.QPointPos.setMinimum(0)
        self.QPointPos.setMaximum(1)
        self.QPointPos.setSingleStep(0.01)

        self.tool_layout.setWidget(1, text_field, QtGui.QLabel("point position"))
        self.tool_layout.setWidget(1, input_field, self.QPointPos)


        # event handlers
        self.Qtoggle_side.clicked.connect(self.toggle_side)

    def setup_pivy(self):
        """set up the scene"""
        self.shape = coin.SoSeparator()
        self.task_separator += self.shape
        self.draw_shape()
        self.drag_separator = coin.SoSeparator()
        self.event_separator = Container()
        self.event_separator.register(self.view)
        self.toggle_side()
        # self.event_separator += list(CutLine.upper_point_set)
        # self.event_separator += CutLine.upper_line_list
        # self.drag_separator += self.event_separator
        # self.task_separator += self.drag_separator

    def accept(self):
        self.event_separator.unregister()
        self.ParametricGlider.elements["cuts"] = CutLine.get_cut_dict()
        self.ParametricGlider.get_glider_3d(self.obj.GliderInstance)
        self.obj.ParametricGlider = self.ParametricGlider
        super(DesignTool, self).accept()
        self.obj.ViewObject.Proxy.updateData()


    def reject(self):
        super(DesignTool, self).reject()
        self.event_separator.unregister()

    def draw_shape(self):
        """ draws the shape of the glider"""
        self.shape += Line(self.front)
        self.shape += Line(self.back)
        self.shape += Line([self.back[0], self.front[0]])
        self.shape += Line([self.back[-1], self.front[-1]])
        self.shape += list(map(Line, self.ribs))

    def toggle_side(self):
        self.event_separator.Select(None)
        self.event_separator.unregister()
        self.drag_separator.removeAllChildren()
        self.event_separator = Container()
        if self.side == "upper":
            self.side = "lower"
            self.Qtoggle_side.setText("show upper side")
            self.event_separator += list(CutLine.lower_point_set)
            self.event_separator += CutLine.lower_line_list
        elif self.side == "lower":
            self.side = "upper"
            self.Qtoggle_side.setText("show lower side")
            self.event_separator += list(CutLine.upper_point_set)
            self.event_separator += CutLine.upper_line_list
        self.drag_separator += self.event_separator
        self.task_separator += self.drag_separator
        self.event_separator.register(self.view)


class CutPoint(Marker):
    def __init__(self, rib_nr, rib_pos, ParametricGlider=None):
        super(CutPoint, self).__init__([[0, 0, 0]], True)
        self.marker.markerIndex = coin.SoMarkerSet.CROSS_7_7
        self.ParametricGlider = ParametricGlider
        self.rib_nr = rib_nr
        self.rib_pos = rib_pos
        self.lines = []
        point = self.get_2D()
        self.x_value = point[0]
        tmp_rib = self.rib_nr - self.ParametricGlider.shape.has_center_cell
        self.max= self.ParametricGlider.shape[tmp_rib, 1.][1]
        self.min= self.ParametricGlider.shape[tmp_rib, 0.][1]
        self.points = [point]
  
    def get_2D(self):
        rib_nr = self.rib_nr - self.ParametricGlider.shape.has_center_cell
        return self.ParametricGlider.shape[rib_nr, abs(self.rib_pos)] + [0]

    def get_rib_pos(self):
        rib_nr = self.rib_nr - self.ParametricGlider.shape.has_center_cell
        if rib_nr < 0:
            rib_nr = self.rib_nr
        rib = self.ParametricGlider.shape.ribs[rib_nr]
        chord = rib[0][1] - rib[1][1]
        sign = ((self.rib_pos >= 0) * 2 - 1)
        return round(sign * (abs(rib[0][1]- self.pos[1])) / chord, 3)
    
    def __eq__(self, other):
        if isinstance(other, CutPoint):
            if self.rib_nr == other.rib_nr:
                if round(self.rib_pos, 3) == round(other.rib_pos, 3):
                    return True
        return False

    def __hash__(self):
        return (hash(self.rib_nr) ^ hash(round(self.rib_pos, 2)))
        
    def replace_by_set(self, point_set):
        for point in point_set:
            if point == self:
                return point
        return false

    @property
    def pos(self):
        return [self.x_value, self.points[0][1], 0]

    @pos.setter
    def pos(self, pos):
        self.points = [self.x_value, pos[1], 0]

    def drag(self, mouse_coords, fact=1.):
        if self.enabled:
            pts = self.points
            for i, pt in enumerate(pts):
                pt[0] = self._tmp_points[i][0]
                y = mouse_coords[1] * fact + self._tmp_points[i][1]
                if y > self.min:
                    pt[1] = self.min
                elif y < self.max:
                    pt[1] = self.max
                else:
                    pt[1] = y
                pt[2] = self._tmp_points[i][2]
            self.points = pts
            for i in self.on_drag:
                i()


class CutLine(Line):
    upper_point_set = set()
    lower_point_set = set()
    upper_line_list = []
    lower_line_list = []
    def __init__(self, point1, point2, cut_type):
        super(CutLine, self).__init__([point1.get_2D(), point2.get_2D()], dynamic=True)
        self.point1 = point1
        self.point2 = point2
        self.ParametricGlider = self.point1.ParametricGlider
        self.cut_type = cut_type
        if self.is_upper:
            CutLine.upper_point_set.add(point1)
            CutLine.upper_point_set.add(point2)
            CutLine.upper_line_list.append(self)
        else:
            CutLine.lower_point_set.add(point1)
            CutLine.lower_point_set.add(point2)
            CutLine.lower_line_list.append(self)

    def setup_visuals(self):
        self.point1.lines.append(self)
        self.point2.lines.append(self)
        self.point1.on_drag.append(self.update_Line)
        self.point2.on_drag.append(self.update_Line)
        
    def replace_points_by_set(self):
        # this has to be done once for every line (before the parent Line is initialized)
        if self.is_upper:
            self.point1 = self.point1.replace_by_set(CutLine.upper_point_set)
            self.point2 = self.point2.replace_by_set(CutLine.upper_point_set)
        else:
            self.point1 = self.point1.replace_by_set(CutLine.lower_point_set)
            self.point2 = self.point2.replace_by_set(CutLine.lower_point_set)

    def update_Line(self):
        self.points = [self.point1.pos, self.point2.pos]

    @property
    def is_upper(self):
        return self.point1.rib_pos < 0 and self.point2.rib_pos < 0

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

    @classmethod
    def cuts_to_lines(cls, ParametricGlider):
        # left = inner rib
        # right = outer rib
        CutLine.upper_point_set = set()
        CutLine.lower_point_set = set()
        CutLine.upper_line_list = []
        CutLine.lower_line_list = []
        for cut in ParametricGlider.elements["cuts"]:
            for cell_nr in cut["cells"]:
                CutLine(CutPoint(cell_nr, cut["left"], ParametricGlider), 
                        CutPoint(cell_nr + 1, cut["right"], ParametricGlider),
                        cut["type"])
        for l in cls.upper_line_list:
            l.replace_points_by_set()
            l.setup_visuals()
        for l in cls.lower_line_list:
            l.replace_points_by_set()
            l.setup_visuals()

    def get_dict(self):
        return {
            "cells": [self.point1.rib_nr],
            "left": self.point1.get_rib_pos(),
            "right" : self.point2.get_rib_pos(),
            "type" : self.cut_type
        }

    @classmethod
    def get_cut_dict(cls):
        cuts = [line.get_dict() for line in cls.upper_line_list + cls.lower_line_list]
        cuts = sorted(cuts, key=lambda x: x["right"])
        sorted_cuts = [cuts[0]]
        for cut in cuts[1:]:
            for key in ["type", "left", "right"]:
                if cut[key] != sorted_cuts[-1][key]:
                    sorted_cuts.append(cut)
                    break
            else:
                sorted_cuts[-1]["cells"].append(cut["cells"][0])
        return sorted_cuts

    def check_dependency(self): 
        if self.point1._delete or self.point2._delete:
            self.delete()

    def delete(self):
        if self.is_upper:
            CutLine.upper_line_list.remove(self)
        else:
            CutLine.lower_line_list.remove(self)
        super(CutLine, self).delete()