import FreeCAD
import FreeCAD as App
import FreeCADGui as Gui
from PySide import QtGui

try:
    from importlib import reload
except ImportError:
    App.Console.PrintError("this is python2\n")
    App.Console.PrintWarning("there is a newer version (python3)\n")
    App.Console.PrintMessage("try to motivate dev to port to python3\n")

from . import _glider as glider
from . import _tools as tools
from . import airfoil_tool as airfoil_tool
from . import shape_tool as shape_tool
from . import arc_tool as arc_tool
from . import aoa_tool as aoa_tool
from . import ballooning_tool as ballooning_tool
from . import line_tool as line_tool
from . import merge_tool as merge_tool
from . import panel_method as pm
from . import cell_tool as cell_tool
from . import design_tool as design_tool
import openglider


#   -import export                                          -?
#   -construction (shape, arc, lines, aoa, ...)             -blue
#   -simulation                                             -yellow
#   -optimisation                                           -red


# Commands-------------------------------------------------------------

class BaseCommand(object):
    def __init__(self):
        pass

    def GetResources(self):
        return {'Pixmap': '.svg', 'MenuText': 'Text', 'ToolTip': 'Text'}

    def IsActive(self):
        if FreeCAD.ActiveDocument is None:
            return False
        elif not self.glider_obj:
            return False
        else:
            return True

    def Activated(self):
        Gui.Control.showDialog(self.tool(self.glider_obj))
    
    @property
    def glider_obj(self):
        obj = Gui.Selection.getSelection()
        if len(obj) > 0:
            obj = obj[0]
            if check_glider(obj):
                return obj
        return None

    def tool(self, obj):
        return tools.BaseTool(obj)


class CellCommand(BaseCommand):
    def tool(self, obj):
        return cell_tool.CellTool(obj)

    def GetResources(self):
        return {'Pixmap': 'cell_command.svg',
                'MenuText': 'edit cells',
                'ToolTip': 'edit cells'}


class Gl2dExport(BaseCommand):
    def GetResources(self):
        return {'Pixmap': 'gl2d_export.svg',
                'MenuText': 'export 2D',
                'ToolTip': 'export 2D'}

    def Activated(self):
        obj = self.glider_obj
        if obj:
            tools.export_2d(obj)


class CreateGlider(BaseCommand):
    def GetResources(self):
        return {'Pixmap': 'new_glider.svg',
                'MenuText': 'create glider',
                'ToolTip': 'create glider'}

    @staticmethod
    def create_glider(import_path=None, parametric_glider=None):
        glider_object = FreeCAD.ActiveDocument.addObject("App::FeaturePython", "Glider")
        glider.OGGlider(glider_object, import_path=import_path, parametric_glider=parametric_glider)
        vp = glider.OGGliderVP(glider_object.ViewObject)
        vp.updateData()
        FreeCAD.ActiveDocument.recompute()
        Gui.SendMsgToActiveView("ViewFit")
        return glider_object

    @property
    def glider_obj(self):
        return True

    def Activated(self):
        CreateGlider.create_glider()


class PatternCommand(BaseCommand):
    def GetResources(self):
        return {'Pixmap': 'pattern_command.svg',
                'MenuText': 'unwrap glider',
                'ToolTip': 'unwrap glider'}

    def Activated(self):
        proceed = False
        obj = Gui.Selection.getSelection()
        if len(obj) > 0:
            obj = obj[0]
            if check_glider(obj):
                proceed = True
        if proceed:
            import openglider.plots
            import Part
            unwrapper = openglider.plots.PlotMaker(obj.GliderInstance)
            unwrapper.unwrap()

            areas = unwrapper.get_all_parts().group_materials()

            for material_name, draw_area in areas.items():
                pattern_doc = FreeCAD.newDocument("plots_{}".format(material_name))
                draw_area.rasterize()
                draw_area.scale(1000)
                for i, part in enumerate(draw_area.parts):
                    grp = pattern_doc.addObject("App::DocumentObjectGroup", part.name)
                    layer_dict = part.layers
                    for layer in layer_dict:
                        for j, line in enumerate(layer_dict[layer]):
                            obj = FreeCAD.ActiveDocument.addObject("Part::Feature", layer + str(j))
                            obj.Shape = Part.makePolygon(map(App.Vector, line))
                            grp.addObject(obj)

                    pattern_doc.recompute()

    @staticmethod
    def fcvec(vec):
        return FreeCAD.Vector(vec[0], vec[1], 0.)


class ImportGlider(BaseCommand):
    @staticmethod
    def create_glider_with_dialog():
        file_name = QtGui.QFileDialog.getOpenFileName(
            parent=None,
            caption="import glider",
            directory='~')
        if not file_name[0] == "":
            file_name = file_name[0]
            file_type = file_name.split(".")[1]
            if file_type == "json":
                CreateGlider.create_glider(import_path=file_name)
            elif file_type == "ods":
                par_glider = openglider.glider.ParametricGlider.import_ods(file_name)
                CreateGlider.create_glider(parametric_glider=par_glider)

    def GetResources(self):
        return {'Pixmap': 'import_glider.svg',
                'MenuText': 'import glider',
                'ToolTip': 'import glider'}

    @property
    def glider_obj(self):
        return True

    def Activated(self):
        self.create_glider_with_dialog()


class ShapeCommand(BaseCommand):
    def GetResources(self):
        return {'Pixmap': 'shape_command.svg',
                'MenuText': 'shape',
                'ToolTip': 'shape'}

    def tool(self, obj):
        return shape_tool.ShapeTool(obj)


class ArcCommand(BaseCommand):
    def GetResources(self):
        return {'Pixmap': 'arc_command.svg',
                'MenuText': 'arc',
                'ToolTip': 'arc'}

    def tool(self, obj):
        return arc_tool.ArcTool(obj)


class AoaCommand(BaseCommand):
    def GetResources(self):
        return {'Pixmap': 'aoa_command.svg',
                'MenuText': 'aoa',
                'ToolTip': 'aoa'}

    def tool(self, obj):
        return aoa_tool.AoaTool(obj)


class ZrotCommand(BaseCommand):
    def GetResources(self):
        return {'Pixmap': 'z_rot_command.svg',
                'MenuText': 'zrot',
                'ToolTip': 'zrot'}

    def tool(self, obj):
        return aoa_tool.ZrotTool(obj)


class AirfoilCommand(BaseCommand):
    def GetResources(self):
        return {'Pixmap': 'airfoil_command.svg',
                'MenuText': 'airfoil',
                'ToolTip': 'airfoil'}

    def tool(self, obj):
        return airfoil_tool.AirfoilTool(obj)


class AirfoilMergeCommand(BaseCommand):
    def GetResources(self):
        return {'Pixmap': 'airfoil_merge_command.svg',
                'MenuText': 'airfoil merge',
                'ToolTip': 'airfoil merge'}

    def tool(self, obj):
        return merge_tool.AirfoilMergeTool(obj)


class BallooningCommand(BaseCommand):
    def GetResources(self):
        return {'Pixmap': 'ballooning_command.svg',
                'MenuText': 'ballooning',
                'ToolTip': 'ballooning'}

    def tool(self, obj):
        return ballooning_tool.BallooningTool(obj)


class BallooningMergCommand(BaseCommand):
    def GetResources(self):
        return {'Pixmap': 'ballooning_merge_command.svg',
                'MenuText': 'ballooning merge',
                'ToolTip': 'ballooning merge'}

    def tool(self, obj):
        return merge_tool.BallooningMergeTool(obj)


class LineCommand(BaseCommand):
    def GetResources(self):
        return {'Pixmap': 'line_command.svg',
                'MenuText': 'lines',
                'ToolTip': 'lines'}

    def tool(self, obj):
        return line_tool.LineTool(obj)


def check_glider(obj):
    if ("GliderInstance" in obj.PropertiesList and
            "ParametricGlider" in obj.PropertiesList):
        return True
    else:
        return False


class PanelCommand(BaseCommand):
    def GetResources(self):
        return {'Pixmap': 'panel_method.svg',
                'MenuText': 'panelmethode', 
                'ToolTip': 'panelmethode'}

    def tool(self, obj):
        return pm.PanelTool(obj)

class PolarsCommand(BaseCommand):
    def GetResources(self):
        return {'Pixmap': 'polar.svg', 'MenuText': 'polars', 'ToolTip': 'polars'}

    def tool(self, obj):
        return pm.polars(obj)


class CutCommand(BaseCommand):
    def GetResources(self):
        return {'Pixmap': 'cut_command.svg', 'MenuText': 'Design', 'ToolTip': 'Design'}

    def tool(self, obj):
        return design_tool.DesignTool(obj)

class ColorCommand(BaseCommand):
    def GetResources(self):
        return {'Pixmap': 'design_command.svg', 'MenuText': 'Design', 'ToolTip': 'Colors'}

    def tool(self, obj):
        return design_tool.DesignTool(obj)


class RefreshCommand():
    def GetResources(self):
        return {'Pixmap': 'refresh_command.svg', 'MenuText': 'Refresh', 'ToolTip': 'Refresh'}

    def IsActive(self):
        return True

    def Activated(self):
        mods = [glider, tools, airfoil_tool, shape_tool, arc_tool, aoa_tool]
        mods += [ballooning_tool, line_tool, merge_tool, pm, cell_tool, design_tool]
        for mod in mods:
            reload(mod)
            try:
                mod.refresh()
            except AttributeError:
                App.Console.PrintWarning(str(mod) + " has no refresh function implemented\n")
        App.Console.PrintLog("RELOADED GLIDER WORKBENCH\n")
