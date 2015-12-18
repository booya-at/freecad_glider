import os
try:
    import FreeCADGui as Gui
    import FreeCAD
except ImportError:
    print("module not loaded with freecad")

import glider_metadata
Dir = os.path.dirname(glider_metadata.__file__)

Gui.addIconPath(Dir + "/icons")


class gliderWorkbench(Workbench):
    """probe workbench object"""
    MenuText = "glider"
    ToolTip = "glider workbench"
    Icon = "glider_workbench.svg"
    toolbox = [
        "CreateGlider",
        "Gl2d_Import",
        "Shape_Tool",
        "Arc_Tool",
        "Aoa_Tool",
        "Airfoil_Tool",
        "AirfoilMergeTool",
        "Ballooning_Tool",
        "BallooningMergeTool",
        "Line_Tool",
        "Gl2d_Export",
        "Cell_Tool"]

    productionbox = [
        "Pattern_Tool",
        "Panel_Tool",
        "Polars_Tool"
        ]


    def GetClassName(self):
        return "Gui::PythonWorkbench"

    def Initialize(self):
        import tools

        Gui.addCommand('CreateGlider', tools.CreateGlider())
        Gui.addCommand('Shape_Tool', tools.Shape_Tool())
        Gui.addCommand('Airfoil_Tool', tools.Airfoil_Tool())
        Gui.addCommand('Arc_Tool', tools.Arc_Tool())
        Gui.addCommand("Aoa_Tool", tools.Aoa_Tool())
        Gui.addCommand("Ballooning_Tool", tools.Ballooning_Tool())
        Gui.addCommand("Line_Tool", tools.Line_Tool())
        Gui.addCommand("Gl2d_Import", tools.Gl2d_Import())
        Gui.addCommand("Gl2d_Export", tools.Gl2d_Export())
        Gui.addCommand("AirfoilMergeTool", tools.AirfoilMergeTool())
        Gui.addCommand("BallooningMergeTool", tools.BallooningMergeTool())

        Gui.addCommand("Pattern_Tool", tools.Pattern_Tool())
        Gui.addCommand("Panel_Tool", tools.Panel_Tool())
        Gui.addCommand("Polars_Tool", tools.Polars_Tool())
        Gui.addCommand("Cell_Tool", tools.Cell_Tool())

        self.appendToolbar("Tools", self.toolbox)
        self.appendMenu("Tools", self.toolbox)
        self.appendToolbar("Production", self.productionbox)
        self.appendMenu("Production", self.productionbox)

    def Activated(self):
        pass

    def Deactivated(self):
        pass


try:
    from tools import Panel_Tool

except ImportError:
    pass

Gui.addWorkbench(gliderWorkbench())