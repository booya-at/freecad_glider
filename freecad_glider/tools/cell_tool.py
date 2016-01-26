from __future__ import division
from PySide import QtGui

from ._tools import base_tool, input_field
from ._glider import draw_glider
from .table import base_table_widget


class cell_tool(base_tool):
    def __init__(self, obj):
        super(cell_tool, self).__init__(obj, hide=True, turn=False)
        self.diagonals_table = diagonals_table()
        self.diagonals_table.get_from_glider_2d(self.glider_2d)
        self.diagonals_button = QtGui.QPushButton("diagonals")
        self.diagonals_button.clicked.connect(self.diagonals_table.show)
        self.layout.setWidget(0, input_field, self.diagonals_button)

        self.vector_table = vector_table()
        self.vector_table.get_from_glider_2d(self.glider_2d)
        self.vector_button = QtGui.QPushButton("vector strap")
        self.vector_button.clicked.connect(self.vector_table.show)
        self.layout.setWidget(1, input_field, self.vector_button)

        self.update_button = QtGui.QPushButton("update glider")
        self.update_button.clicked.connect(self.update_glider)
        self.layout.setWidget(2, input_field, self.update_button)
        draw_glider(self.glider_2d.get_glider_3d(), self.task_separator, hull=False, ribs=True)

    def update_glider(self):
        self.task_separator.removeAllChildren()
        self.apply_elements()
        draw_glider(self.glider_2d.get_glider_3d(), self.task_separator, hull=False, ribs=True)

    def apply_elements(self):
        self.diagonals_table.apply_to_glider(self.glider_2d)
        self.vector_table.apply_to_glider(self.glider_2d)

    def accept(self):
        super(cell_tool, self).accept()
        self.diagonals_table.hide()
        self.vector_table.hide()
        del self.diagonals_table
        del self.vector_table
        self.update_view_glider()

    def reject(self):
        super(cell_tool, self).reject()
        self.diagonals_table.hide()
        self.vector_table.hide()
        del self.diagonals_table
        del self.vector_table


def number_input(number):
    return QtGui.QTableWidgetItem(str(number))


class diagonals_table(base_table_widget):
    def __init__(self):
        super(diagonals_table, self).__init__(name="diagonals")
        self.table.setRowCount(10)
        self.table.setColumnCount(9)
        self.table.setHorizontalHeaderLabels([
            "right\nfront",
            "rf\nheight",
            "right\nback",
            "rb\nheight",
            "left\nback",
            "lb\nheight",
            "left\nfront",
            "lf\nheight",
            "ribs"])

    def get_from_glider_2d(self, glider_2d):
        if "diagonals" in glider_2d.elements:
            diags = glider_2d.elements["diagonals"]
            for row, element in enumerate(diags):
                entries = list(
                    element["right_front"] +
                    element["right_back"] +
                    element["left_back"] +
                    element["left_front"])
                entries.append(element["cells"])
                self.table.setRow(row, entries)

    def apply_to_glider(self, glider_2d):
        num_rows = self.table.rowCount()
        # remove all diagonals from the glide_2d
        glider_2d.elements["diagonals"] = []
        for n_row in range(num_rows):
            row = self.get_row(n_row)
            if row:
                diagonal = {}
                diagonal["right_front"] = (row[0], row[1])
                diagonal["right_back"] = (row[2], row[3])
                diagonal["left_back"] = (row[4], row[5])
                diagonal["left_front"] = (row[6], row[7])
                diagonal["cells"] = row[-1]
                glider_2d.elements["diagonals"].append(diagonal)

    def get_row(self, n_row):
        str_row = [self.table.item(n_row, i).text() for i in range(9) if self.table.item(n_row, i)]
        str_row = [item for item in str_row if item != ""]
        if len(str_row) != 9:
            print("something wrong with row " + str(n_row))
            return None
        try:
            return list(map(float, str_row[:-1]) + [map(int, str_row[-1].split(","))])
        except TypeError:
            print("something wrong with row " + str(n_row))
            return None


class vector_table(base_table_widget):
    def __init__(self):
        super(vector_table, self).__init__(name="vector straps")
        self.table.setRowCount(10)
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["left", "right", "ribs"])

    def get_from_glider_2d(self, glider_2d):
        if "straps" in glider_2d.elements:
            straps = glider_2d.elements["straps"]
            for row, element in enumerate(straps):
                entries = [element["right"], element["left"]]
                entries.append(element["cells"])
                self.table.setRow(row, entries)

    def apply_to_glider(self, glider_2d):
        num_rows = self.table.rowCount()
        # remove all diagonals from the glide_2d
        glider_2d.elements["straps"] = []
        for n_row in range(num_rows):
            row = self.get_row(n_row)
            if row:
                strap = {}
                strap["right"] = row[0]
                strap["left"] = row[1]
                strap["cells"] = row[2]
                glider_2d.elements["straps"].append(strap)

    def get_row(self, n_row):
        str_row = [self.table.item(n_row, i).text() for i in range(3) if self.table.item(n_row, i)]

        print(str_row)
        str_row = [item for item in str_row if item != ""]
        if len(str_row) != 3:
            print("something wrong with row " + str(n_row))
            return None
        try:
            return list(map(float, str_row[:-1]) + [map(int, str_row[-1].split(","))])
        except TypeError:
            print("something wrong with row " + str(n_row))
            return None
