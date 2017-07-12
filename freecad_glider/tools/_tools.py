from __future__ import division

from copy import deepcopy

from PySide import QtGui
from pivy import coin
import FreeCADGui as Gui
import FreeCAD as App
from openglider.jsonify import dump, load
from openglider.vector.spline import BernsteinBase, BSplineBase
from openglider.glider import ParametricGlider

# as long as this isn't part of std pivy:
def SoGroup__iadd__(self, other):
    if not isinstance(other, list):
        raise(AttributeError("rhs must be list"))
    for other_i in other:
        self.addChild(other_i)
    return self


def SoGroup_getByName(self, name):
    for child in self:
        if name == child.getName():
            return child
    return None


coin.SoGroup.__iadd__ = SoGroup__iadd__
coin.SoGroup.getByName = SoGroup_getByName


def hex_to_rgb(hex_string):
    try:
        value = hex_string.split('#')[1]
        lv = len(value)
        return tuple(int(value[i:i + lv // 3], 16) / 256. for i in range(0, lv, lv // 3))
    except IndexError:
        return (.7, .7, .7)

def rgb_to_hex(color_tuple):
    assert(all(0 <= i <= 1 for i in color_tuple))
    c = tuple(int(i * 255) for i in color_tuple)
    return '#%02x%02x%02x' % c


def refresh():
    pass

text_field = QtGui.QFormLayout.LabelRole
input_field = QtGui.QFormLayout.FieldRole


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
        if self.spline_objects:
            base = self.spline_objects[0].basefactory
            if base.__class__ == BernsteinBase.__class__:
                return "Bezier"
            else:
                return "BSpline_" + str(base.degree)
        else:
            return "Bezier"

    def set_spline_type(self, *args):
        for spline in self.spline_objects:
            spline.change_base(self.spline_types[self.currentText()][0])
        self.update_function()


class BaseTool(object):
    hide = True
    widget_name = "Unnamed"
    turn = True

    def __init__(self, obj):
        self.obj = obj
        self.parametric_glider = deepcopy(self.obj.Proxy.getParametricGlider())
        self._vis_object = []
        for obj in App.ActiveDocument.Objects:
            try:
                if obj.ViewObject.Visibility:
                    obj.ViewObject.Visibility = False
                    self._vis_object += [obj]
            except Exception:
                pass
        self.obj.ViewObject.Visibility = not self.hide
        self.view = Gui.ActiveDocument.ActiveView
        Gui.Selection.clearSelection()
        if self.turn:
            self.view.viewTop()

        # disable the rotation function
        # first get the widget where the scene ives in

        # form is the widget that appears in the task panel
        self.form = []

        self.base_widget = QtGui.QWidget()
        self.form.append(self.base_widget)
        self.layout = QtGui.QFormLayout(self.base_widget)
        self.base_widget.setWindowTitle(self.widget_name)

        # scene container
        self.task_separator = coin.SoSeparator()
        self.task_separator.setName("task_seperator")
        self.scene.addChild(self.task_separator)

    def update_view_glider(self):  # rename
        # 1: update parametric-glider and get the glider_instance
        self.obj.Proxy.setParametricGlider(self.parametric_glider)
        # 2: draw the glider for all visible objects
        self.obj.Proxy.drawGlider()

    def accept(self):
        for obj in self._vis_object:
            obj.ViewObject.Visibility = True
        self.scene.removeChild(self.task_separator)
        Gui.Control.closeDialog()

    def reject(self):
        for obj in self._vis_object:
            obj.ViewObject.Visibility = True
        self.scene.removeChild(self.task_separator)
        Gui.Control.closeDialog()

    def setup_widget(self):
        pass

    def add_pivy(self):
        pass

    @property
    def scene(self):
        return self.view.getSceneGraph()

    @property
    def nav_bak(self):
        return self.view.getNavigationType()
