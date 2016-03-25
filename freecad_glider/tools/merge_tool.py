from __future__ import division

import numpy
from pivy import coin

from openglider.vector.spline import Bezier


from ._tools import BaseTool
from .pivy_primitives import Line, ControlPointContainer, vector3D


def refresh():
    pass


class BaseMergeTool(BaseTool):
    def __init__(self, obj):
        super(BaseMergeTool, self).__init__(obj)
        self.bezier_curve = Bezier([[0, 0], [1, 1]])
        self.bezier_cpc = ControlPointContainer(self.bezier_curve.controlpoints, self.view)
        self.shape = coin.SoSeparator()
        self.grid = coin.SoSeparator()
        self.coords = coin.SoSeparator()
        self.expl_curve = Line([])

        _shape = self.ParametricGlider.shape.get_half_shape()
        self.ribs = _shape.ribs
        self.front = _shape.front
        self.back = _shape.back

        self.bezier_cpc.on_drag.append(self.update_spline)
        self.setup_widget()
        self.setup_pivy()

        # add the spline controls

    def setup_pivy(self):
        self.task_separator.addChild(self.bezier_cpc)
        self.task_separator.addChild(self.shape)
        self.task_separator.addChild(self.expl_curve.object)
        self.task_separator.addChild(self.coords)
        self.task_separator.addChild(self.grid)
        self.draw_shape()

    def draw_shape(self):
        self.shape.removeAllChildren()
        self.shape.addChild(Line(self.front, color="grey").object)
        self.shape.addChild(Line(self.back, color="grey").object)
        for rib in self.ribs:
            self.shape.addChild(Line(rib, color="grey").object)

    def update_num_control_points(self, numpoints):
        self.bezier_curve.numpoints = numpoints
        self.bezier_cpc.control_points[-1].constraint = lambda pos: [self.ParametricGlider.shape.span, pos[1], pos[2]]

    def update_spline(self):
        pass

    def accept(self):
        self.bezier_cpc.remove_callbacks()
        self.update_view_glider()
        super(BaseMergeTool, self).accept()

    def reject(self):
        self.bezier_cpc.remove_callbacks()
        super(BaseMergeTool, self).reject()

    def grid_points(self, grid_x, grid_y):
        return [[x, y] for y in grid_y for x in grid_x]

    def update_grid(self, grid_x, grid_y):
        self.grid.removeAllChildren()
        x_points_lower = [[x, grid_y[0], 0] for x in grid_x]
        x_points_upper = [[x, grid_y[-1], 0] for x in grid_x]
        y_points_lower = [[grid_x[0], y, 0] for y in grid_y]
        y_points_upper = [[grid_x[-1], y, 0] for y in grid_y]
        for l in zip(x_points_lower, x_points_upper):
            self.grid.addChild(Line(l, color="grey").object)
        for l in zip(y_points_lower, y_points_upper):
            self.grid.addChild(Line(l, color="grey").object)


class AirfoilMergeTool(BaseMergeTool):
    def __init__(self, obj):
        super(AirfoilMergeTool, self).__init__(obj)
        self.scal = numpy.array([1, 0.2])
        self.x_grid = [i[0] for i in self.front if i[0] >= 0]
        self.set_end_points()
        self.bezier_curve = self.ParametricGlider.profile_merge_curve
        self.bezier_curve = Bezier([self.scal * i for i in self.bezier_curve.controlpoints])
        self.bezier_cpc.control_pos = vector3D(self.bezier_curve.controlpoints)
        self.fix_end_points()

    def set_end_points(self):
        self.ParametricGlider.profile_merge_curve.controlpoints[0][0] = 0
        self.ParametricGlider.profile_merge_curve.controlpoints[-1][0] = self.ParametricGlider.shape.span

    def update_spline(self):
        self.bezier_curve.controlpoints = [point[:2] for point in self.bezier_cpc.control_pos]
        self.expl_curve.update(self.bezier_curve.get_sequence(40))
        y_grid = range(int(max([c[1] / self.scal[1] for c in self.bezier_curve.get_sequence(10)])) + 2)
        y_grid = [i * self.scal[1] for i in y_grid]
        self.update_grid(self.x_grid, y_grid)

    def fix_end_points(self):
        def y_constraint(pos):
            return [pos[0], (pos[1] > 0) * pos[1], pos[2]]

        def c1(pos):
            pos = y_constraint(pos)
            return [0, pos[1], pos[2]]

        def c2(pos):
            pos = y_constraint(pos)
            return [self.ParametricGlider.shape.span, pos[1], pos[2]]

        for i, cp in enumerate(self.bezier_cpc.control_points):
            if i == 0:
                cp.constraint = c1
            elif i == len(self.bezier_cpc.control_points) - 1:
                cp.constraint = c2
            else:
                cp.constraint = y_constraint
        self.update_spline()

    def accept(self):
        self.ParametricGlider.profile_merge_curve.controlpoints = [cp / self.scal for cp in self.bezier_curve.controlpoints]
        super(AirfoilMergeTool, self).accept()


class BallooningMergeTool(BaseMergeTool):
    def __init__(self, obj):
        super(BallooningMergeTool, self).__init__(obj)
        self.scal = numpy.array([1, 0.2])
        self.x_grid = [i[0] for i in self.front if i[0] >= 0]
        self.set_end_points()
        self.bezier_curve = self.ParametricGlider.ballooning_merge_curve
        self.bezier_curve = Bezier([self.scal * i for i in self.bezier_curve.controlpoints])
        self.bezier_cpc.control_pos = vector3D(self.bezier_curve.controlpoints)
        self.fix_end_points()

    def set_end_points(self):
        self.ParametricGlider.ballooning_merge_curve.controlpoints[0][0] = 0
        self.ParametricGlider.ballooning_merge_curve.controlpoints[-1][0] = self.ParametricGlider.shape.span

    def update_spline(self):
        self.bezier_curve.controlpoints = [point[:2] for point in self.bezier_cpc.control_pos]
        self.expl_curve.update(self.bezier_curve.get_sequence(40))
        y_grid = range(int(max([c[1] / self.scal[1] for c in self.bezier_curve.get_sequence(10)])) + 2)
        y_grid = [i * self.scal[1] for i in y_grid]
        self.update_grid(self.x_grid, y_grid)

    def fix_end_points(self):
        def y_constraint(pos):
            return [pos[0], (pos[1] > 0) * pos[1], pos[2]]

        def c1(pos):
            pos = y_constraint(pos)
            return [0, pos[1], pos[2]]

        def c2(pos):
            pos = y_constraint(pos)
            return [self.ParametricGlider.shape.span, pos[1], pos[2]]

        for i, cp in enumerate(self.bezier_cpc.control_points):
            if i == 0:
                cp.constraint = c1
            elif i == len(self.bezier_cpc.control_points) - 1:
                cp.constraint = c2
            else:
                cp.constraint = y_constraint
        self.update_spline()

    def accept(self):
        self.ParametricGlider.ballooning_merge_curve.controlpoints = [cp / self.scal for cp in self.bezier_curve.controlpoints]
        super(BallooningMergeTool, self).accept()
