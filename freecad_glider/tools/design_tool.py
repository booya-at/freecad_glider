from __future__ import division

from PySide import QtGui, QtCore
import numpy as np
import FreeCAD as App

from ._tools import BaseTool, input_field, text_field
from .pivy_primitives_new_new import coin, Line, Marker, Container, vector3D


# idea: draw lines between ribs and fill the panels with color
# only straight lines, no curves

# 1: draw shape(ribs, outline) + switcher front and back
# 2: event handler to pin to raster
# 3: line creation, selection
# 4: panels filling (color) + leading edge
# 5: delete ?
# 6: editing ?

class DesignTool(BaseTool)
