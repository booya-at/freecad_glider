import FreeCAD
import FreeCAD as App
import FreeCADGui as Gui

from ._glider import OGGlider, OGGliderVP
from ._tools import BaseTool, export_2d, import_2d
from .airfoil_tool import AirfoilTool
from .shape_tool import ShapeTool
from .arc_tool import ArcTool
from .aoa_tool import AoaTool, ZrotTool
from .ballooning_tool import BallooningTool
from .line_tool import LineTool
from .merge_tool import AirfoilMergeTool, BallooningMergeTool
from .panel_methode import PanelTool, polars
from .cell_tool import CellTool
import openglider


#   -import export                                          -?
#   -construction (shape, arc, lines, aoa, ...)             -blue
#   -simulation                                             -yellow
#   -optimisation                                           -red


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
        return BaseTool(obj)


class CellCommand(BaseCommand):
    def tool(self, obj):
        return CellTool(obj)

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
            export_2d(obj)


class Gl2dImport(BaseCommand):
    def GetResources(self):
        return {'Pixmap': 'gl2d_import.svg',
                'MenuText': 'import 2D',
                'ToolTip': 'import 2D'}

    def Activated(self):
        obj = self.glider_obj
        if obj:
            import_2d(obj)


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


class CreateGlider(BaseCommand):
    @staticmethod
    def create_glider():
        a = FreeCAD.ActiveDocument.addObject("App::FeaturePython", "Glider")
        OGGlider(a)
        vp = OGGliderVP(a.ViewObject)
        vp.updateData()
        FreeCAD.ActiveDocument.recompute()
        Gui.SendMsgToActiveView("ViewFit")

    def GetResources(self):
        return {'Pixmap': "new_glider.svg",
                'MenuText': 'glider',
                'ToolTip': 'glider'}

    @property
    def glider_obj(self):
        return True

    def Activated(self):
        self.create_glider()


class ShapeCommand(BaseCommand):
    def GetResources(self):
        return {'Pixmap': 'shape_command.svg',
                'MenuText': 'shape',
                'ToolTip': 'shape'}

    def tool(self, obj):
        return ShapeTool(obj)


class ArcCommand(BaseCommand):
    def GetResources(self):
        return {'Pixmap': 'arc_command.svg',
                'MenuText': 'arc',
                'ToolTip': 'arc'}

    def tool(self, obj):
        return ArcTool(obj)


class AoaCommand(BaseCommand):
    def GetResources(self):
        return {'Pixmap': 'aoa_command.svg',
                'MenuText': 'aoa',
                'ToolTip': 'aoa'}

    def tool(self, obj):
        return AoaTool(obj)


class ZrotCommand(BaseCommand):
    def GetResources(self):
        return {'Pixmap': 'z_rot_command.svg',
                'MenuText': 'zrot',
                'ToolTip': 'zrot'}

    def tool(self, obj):
        return ZrotTool(obj)


class AirfoilCommand(BaseCommand):
    def GetResources(self):
        return {'Pixmap': 'airfoil_command.svg',
                'MenuText': 'airfoil',
                'ToolTip': 'airfoil'}

    def tool(self, obj):
        return AirfoilTool(obj)


class AirfoilMergeCommand(BaseCommand):
    def GetResources(self):
        return {'Pixmap': 'airfoil_merge_command.svg',
                'MenuText': 'airfoil merge',
                'ToolTip': 'airfoil merge'}

    def tool(self, obj):
        return AirfoilMergeTool(obj)


class BallooningCommand(BaseCommand):
    def GetResources(self):
        return {'Pixmap': 'ballooning_command.svg',
                'MenuText': 'ballooning',
                'ToolTip': 'ballooning'}

    def tool(self, obj):
        return BallooningTool(obj)


class BallooningMergCommand(BaseCommand):
    def GetResources(self):
        return {'Pixmap': 'ballooning_merge_command.svg',
                'MenuText': 'ballooning merge',
                'ToolTip': 'ballooning merge'}

    def tool(self, obj):
        return BallooningMergeTool(obj)


class LineCommand(BaseCommand):
    def GetResources(self):
        return {'Pixmap': 'line_command.svg',
                'MenuText': 'lines',
                'ToolTip': 'lines'}

    def tool(self, obj):
        return LineTool(obj)


def check_glider(obj):
    if ("GliderInstance" in obj.PropertiesList and
            "ParametricGlider" in obj.PropertiesList):
        return True
    else:
        return False


class PanelCommand(BaseCommand):
    def GetResources(self):
        return {'Pixmap': 'panel_methode.svg',
                'MenuText': 'panelmethode', 
                'ToolTip': 'panelmethode'}

    def tool(self, obj):
        return PanelTool(obj)

class PolarsCommand(BaseCommand):
    def GetResources(self):
        return {'Pixmap': 'polar.svg', 'MenuText': 'polars', 'ToolTip': 'polars'}

    def tool(self, obj):
        return polars(obj)