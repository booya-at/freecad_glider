import os
try:
    import FreeCADGui as Gui
    import FreeCAD
except ImportError:
    print("module not loaded with freecad")

import glider_metadata
Dir = os.path.dirname(glider_metadata.__file__)

Gui.addIconPath(Dir + "/icons")


class gliderWorkbench(Gui.Workbench):
    """probe workbench object"""
    MenuText = "glider"
    ToolTip = "glider workbench"
    Icon = "glider_workbench.svg"
    toolbox = [
        "CreateGlider",
        "Gl2dImport",
        "ShapeCommand",
        "ArcCommand",
        "AoaCommand",
        "ZrotCommand",
        "AirfoilCommand",
        "AirfoilMergeCommand",
        "BallooningCommand",
        "BallooningMergeCommand",
        "CellCommand",
        "LineCommand",
        "Gl2dExport"]

    productionbox = [
        "PatternCommand",
        "PanelCommand",
        "PolarsCommand"
        ]


    def GetClassName(self):
        return "Gui::PythonWorkbench"

    def Initialize(self):
        import tools

        Gui.addCommand('CreateGlider', tools.CreateGlider())
        Gui.addCommand('ShapeCommand', tools.ShapeCommand())
        Gui.addCommand('AirfoilCommand', tools.AirfoilCommand())
        Gui.addCommand('ArcCommand', tools.ArcCommand())
        Gui.addCommand("AoaCommand", tools.AoaCommand())
        Gui.addCommand("BallooningCommand", tools.BallooningCommand())
        Gui.addCommand("LineCommand", tools.LineCommand())
        Gui.addCommand("Gl2dImport", tools.Gl2dImport())
        Gui.addCommand("Gl2dExport", tools.Gl2dExport())
        Gui.addCommand("AirfoilMergeCommand", tools.AirfoilMergeCommand())
        Gui.addCommand("BallooningMergeCommand", tools.BallooningMergCommand())
        Gui.addCommand("CellCommand", tools.CellCommand())
        Gui.addCommand("ZrotCommand", tools.ZrotCommand())

        Gui.addCommand("PatternCommand", tools.PatternCommand())
        Gui.addCommand("PanelCommand", tools.PanelCommand())
        Gui.addCommand("PolarsCommand", tools.PolarsCommand())

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