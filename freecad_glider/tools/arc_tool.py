from pivy import coin
from PySide import QtGui

from ._tools import BaseTool, text_field, input_field, spline_select
from .pivy_primitives import Line, ControlPointContainer, vector3D, vector2D


def refresh():
    pass


class ArcTool(BaseTool):
    hide = True
    widget_name = "ArcTool"

    def __init__(self, obj):
        """adds a symmetric spline to the scene"""
        super(ArcTool, self).__init__(obj)

        controlpoints = list(map(vector3D, self.ParametricGlider.arc.curve.controlpoints))
        self.arc_cpc = ControlPointContainer(controlpoints, self.view)
        self.Qnum_arc = QtGui.QSpinBox(self.base_widget)
        self.spline_select = spline_select(
            [self.ParametricGlider.arc.curve], self.update_spline_type, self.base_widget)
        self.shape = coin.SoSeparator()
        self.task_separator.addChild(self.shape)

        self.setup_widget()
        self.setup_pivy()

    def setup_widget(self):

        self.Qnum_arc.setMaximum(5)
        self.Qnum_arc.setMinimum(2)
        self.Qnum_arc.setValue(len(self.ParametricGlider.arc.curve.controlpoints))
        self.ParametricGlider.arc.curve.numpoints = self.Qnum_arc.value()

        self.layout.setWidget(0, text_field, QtGui.QLabel("arc num_points"))
        self.layout.setWidget(0, input_field, self.Qnum_arc)
        self.layout.setWidget(1, text_field, QtGui.QLabel("bspline type"))
        self.layout.setWidget(1, input_field, self.spline_select)

        self.Qnum_arc.valueChanged.connect(self.update_num)

    def setup_pivy(self):
        self.arc_cpc.on_drag.append(self.update_spline)
        self.arc_cpc.drag_release.append(self.update_real_arc)
        self.task_separator.addChild(self.arc_cpc)

        self.update_spline()
        self.update_real_arc()
        self.update_num()

    # def set_edit(self, *arg):
    #     self.arc_cpc.set_edit_mode(self.view)

    def update_spline(self):
        self.shape.removeAllChildren()
        self.ParametricGlider.arc.curve.controlpoints = [vector2D(i) for i in self.arc_cpc.control_pos]
        self.shape.addChild(Line(self.ParametricGlider.arc.curve.get_sequence(num=30), color="grey").object)

    def update_spline_type(self):
        self.arc_cpc.control_pos = self.ParametricGlider.arc.curve.controlpoints
        self.update_spline()

    def get_arc_positions(self):
        return self.ParametricGlider.arc.get_arc_positions(self.ParametricGlider.shape.rib_x_values)

    def update_real_arc(self):
        self.shape.addChild(Line(self.get_arc_positions(), color="red", width=2).object)

    def update_num(self, *arg):
        self.ParametricGlider.arc.curve.numpoints = self.Qnum_arc.value()
        self.arc_cpc.control_pos = self.ParametricGlider.arc.curve.controlpoints
        self.update_spline()

    def accept(self):
        self.obj.ParametricGlider = self.ParametricGlider
        self.ParametricGlider.get_glider_3d(self.obj.GliderInstance)
        self.arc_cpc.remove_callbacks()
        super(ArcTool, self).accept()
        self.update_view_glider()

    def reject(self):
        self.arc_cpc.remove_callbacks()
        super(ArcTool, self).reject()
