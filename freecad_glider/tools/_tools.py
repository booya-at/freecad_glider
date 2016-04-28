from __future__ import division

from copy import deepcopy

from PySide import QtGui, QtCore
from pivy import coin
import FreeCADGui as Gui
from openglider.jsonify import dump, load
from openglider.vector.spline import BernsteinBase, BSplineBase
from openglider.glider import ParametricGlider


def refresh():
    pass

# from openglider.glider.parametric import Glider2D


text_field = QtGui.QFormLayout.LabelRole
input_field = QtGui.QFormLayout.FieldRole

# TODO:
#   -merge-tool
#       -airfoil
#       -ballooning
#       -aoa                xx
#       -zrot
#   -airfoil-tool
#   -ballooning-tool
#   -attachmentpoint-tool
#   -line-tool
#   -inlet-tool
#   -design-tool
#   -minirips-tool
#   -etc...


def export_2d(glider):
    filename = QtGui.QFileDialog.getSaveFileName(
        parent=None,
        caption="export glider",
        directory='~')
    if filename[0] != "":
        with open(filename[0], 'w') as exportfile:
            dump(glider.ParametricGlider, exportfile)


def import_2d(glider):
    file_name = QtGui.QFileDialog.getOpenFileName(
        parent=None,
        caption="import glider",
        directory='~')
    if file_name[0] != "":
        file_name = file_name[0]
        file_type = file_name.split(".")[1]
        if file_type == "json":
            with open(file_name, 'r') as importfile:
                glider.ParametricGlider = load(importfile)["data"]
                glider.ParametricGlider.get_glider_3d(glider.GliderInstance)
                glider.ViewObject.Proxy.updateData()
        elif file_type == "ods":
            glider.ParametricGlider = ParametricGlider.import_ods(file_name)
            glider.ParametricGlider.get_glider_3d(glider.GliderInstance)
            glider.ViewObject.Proxy.updateData()


class spline_select(QtGui.QComboBox):
    spline_types = {
        "Bezier": (BernsteinBase, 0),
        "BSpline_2": (BSplineBase(2), 1),
        "BSpline_3": (BSplineBase(3), 2)
    }

    def __init__(self, spline_objects, update_function, parent=None):
        super(spline_select, self).__init__(parent)
        self.update_function = update_function
        self.spline_objects = spline_objects    # list of splines
        for key in ["Bezier", "BSpline_2", "BSpline_3"]:
            self.addItem(key)
        self.setCurrentIndex(self.spline_types[self.current_spline_type][1])
        self.currentIndexChanged.connect(self.set_spline_type)

    @property
    def current_spline_type(self):
        base = self.spline_objects[0].basefactory
        if base.__class__ == BernsteinBase.__class__:
            return "Bezier"
        else:
            return "BSpline_" + str(base.degree)

    def set_spline_type(self, *args):
        for spline in self.spline_objects:
            spline.change_base(self.spline_types[self.currentText()][0])
        self.update_function()


class BaseTool(object):
    def __init__(self, obj, widget_name="BaseWidget", hide=False, turn=True):
        self.obj = obj
        self.ParametricGlider = deepcopy(self.obj.ParametricGlider)
        self.obj.ViewObject.Visibility = not hide
        scene = Gui.ActiveDocument.ActiveView.getSceneGraph()
        self._views = Gui.createViewer(2)
        self.view = self._views.getViewer(0)
        self._views.getViewer(1).getSoRenderManager().getSceneGraph().addChild(scene)
        Gui.Selection.clearSelection()
        if turn:
            self._views.viewTop()

        # self.view.setNavigationType('Gui::TouchpadNavigationStyle')
        # disable the rotation function
        # first get the widget where the scene ives in

        # form is the widget that appears in the task panel
        self.form = []

        self.base_widget = QtGui.QWidget()
        self.form.append(self.base_widget)
        self.layout = QtGui.QFormLayout(self.base_widget)
        self.base_widget.setWindowTitle(widget_name)

        # scene container
        self.task_separator = coin.SoSeparator()
        self.task_separator.setName("task_seperator")
        self.scene.addChild(self.task_separator)

    def update_view_glider(self):  # rename
        self.obj.ParametricGlider = self.ParametricGlider
        self.ParametricGlider.get_glider_3d(self.obj.GliderInstance)
        self.obj.ViewObject.Proxy.updateData()

    def accept(self):
        self.obj.ViewObject.Visibility = True
        self.scene.removeChild(self.task_separator)
        Gui.Control.closeDialog()
        self._views.close()

    def reject(self):
        self.obj.ViewObject.Visibility = True
        self.scene.removeChild(self.task_separator)
        Gui.Control.closeDialog()
        self._views.close()

    def setup_widget(self):
        pass

    def add_pivy(self):
        pass

    @property
    def scene(self):
        return self.view.getSoRenderManager().getSceneGraph()

    @property
    def nav_bak(self):
        return self.view.getNavigationType()
