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
        self.drag_separator = coin.SoSeparator()
        self.event_separator = Container()
        lines = self.cuts_to_lines()
        self.event_separator += list(CutLine.point_set)
        self.drag_separator += self.event_separator
        self.drag_separator += lines
        self.task_separator += self.drag_separator
        self.event_separator.register(self.view)

    def cuts_to_lines(self):
        # left = inner rib
        # right = outer rib
        line_list = []
        CutLine.point_set = set()
        for cut in self.ParametricGlider.elements["cuts"]:
            for cell_nr in cut["cells"]:
                l = CutLine(CutPoint(cell_nr, cut["left"], self.ParametricGlider), 
                            CutPoint(cell_nr + 1, cut["right"], self.ParametricGlider))
                line_list.append(l)
        for l in line_list:
            l.replace_points_by_set()
            l.setup_visuals()
        return line_list

    def accept(self):
        super(DesignTool, self).accept()
        self.event_separator.unregister()

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

    def draw_panels(self):
        pass

class CutPoint(Marker):
    def __init__(self, rib_nr, rib_pos, ParametricGlider=None):
        super(CutPoint, self).__init__([[0, 0, 0]], True)
        self.ParametricGlider = ParametricGlider
        self.rib_nr = rib_nr
        self.rib_pos = rib_pos
        self.lines = []
        point = self.get_2D()
        self.x_value = point[0]
        tmp_rib = self.rib_nr - self.ParametricGlider.shape.has_center_cell
        self.max= self.ParametricGlider.shape[tmp_rib, 1.][1]
        self.min= self.ParametricGlider.shape[tmp_rib, 0.][1]
        print("max", self.min)
        print("min", self.max)
        self.points = [point]
  
    def get_2D(self):
        rib_nr = self.rib_nr - self.ParametricGlider.shape.has_center_cell
        return self.ParametricGlider.shape[rib_nr, self.rib_pos] + [0]
    
    def __eq__(self, other):
        if self.rib_nr == other.rib_nr:
            if round(self.rib_pos, 2) == round(other.rib_pos, 2):
                return True

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
    point_set = set()
    def __init__(self, point1, point2):
        super(CutLine, self).__init__([point1.get_2D(), point2.get_2D()], dynamic=False)
        self.point1 = point1
        CutLine.point_set.add(point1)
        self.point2 = point2
        CutLine.point_set.add(point2)

    def setup_visuals(self):
        self.point1.lines.append(self)
        self.point2.lines.append(self)
        self.point1.on_drag.append(self.update_Line)
        self.point2.on_drag.append(self.update_Line)
        
    def replace_points_by_set(self):
        # this has to be done once for every line (before the parent Line is initialized)
        self.point1 = self.point1.replace_by_set(CutLine.point_set)
        self.point2 = self.point2.replace_by_set(CutLine.point_set)

    def update_Line(self):
        self.points = [self.point1.pos, self.point2.pos]

    # def drag(self, mouse_coords, fact=1.):
    #     self.point1.drag(mouse_coords, fact)
    #     self.point2.drag(mouse_coords, fact)

    # @property
    # def drag_objects(self):
    #     return [self.point1, self.point2]

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
