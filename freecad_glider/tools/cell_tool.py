from __future__ import division
from PySide import QtCore, QtGui
from _tools import base_tool, text_field, input_field

from table import base_table_widget, base_table


# 1 cell tool:
#   new cell (empty, copy)
#   delete cell
#   list cell (selection)
#   diagonals
#   vectors_straps

# 2 apply tool
#   table which applies the different cells to the glider

class cell_tool(base_tool):
    def __init__(self, obj):
        super(cell_tool, self).__init__(obj, hide=False, turn=False)
        self.diagonals_table = diagonals_table()
        self.diagonals_button = QtGui.QPushButton("diagonals")
        self.diagonals_button.clicked.connect(self.diagonals_table.show)
        self.layout.setWidget(0, input_field, self.diagonals_button)

        self.vector_table = vector_table()
        self.vector_button = QtGui.QPushButton("vector strap")
        self.vector_button.clicked.connect(self.vector_table.show)
        self.layout.setWidget(1, input_field, self.vector_button)

    def accept(self):
        super(cell_tool, self).accept()
        self.diagonals_table.hide()
        self.vector_table.hide()
        del self.diagonals_table
        del self.vector_table

    def reject(self):
        super(cell_tool, self).reject()
        self.diagonals_table.hide()
        self.vector_table.hide()
        del self.diagonals_table
        del self.vector_table


class diagonals_table(base_table_widget):
    def __init__(self):
        super(diagonals_table, self).__init__(name="diagonals")
        self.table.setRowCount(10)
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(["left", "right", "size-left", "size-right", "pos-left", "pos-right"])

class vector_table(base_table_widget):
    def __init__(self):
        super(vector_table, self).__init__(name="vector straps")
        self.table.setRowCount(10)
        self.table.setColumnCount(2)
        self.table.setHorizontalHeaderLabels(["left", "right"])


