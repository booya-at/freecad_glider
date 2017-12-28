import os
try:
    import FreeCADGui as Gui
    import FreeCAD
except ImportError:
    print('module not loaded with freecad')


from pivy import coin

try:
    sep1 = coin.SoSeparator()
    sep2 = coin.SoSeparator()
    sep1 += sep2
except TypeError:
    class newSeparator(coin.SoSeparator):
        def __iadd__(self, other):
            #if isinstance(other, coin.SoSeparator):
            #    self.addChild(other)
            #else:

            for child in other:
                self.addChild(child)
            return self

    coin.SoSeparator = newSeparator

Dir = os.path.abspath(os.path.dirname(__file__))
Gui.addIconPath(os.path.join(Dir, 'icons'))


class gliderWorkbench(Gui.Workbench):
    MenuText = 'glider'
    ToolTip = 'glider workbench'
    Icon = 'glider_workbench.svg'
    toolBox = [
        'CreateGlider',
        'ImportGlider',
        'ShapeCommand',
        'ArcCommand',
        'AoaCommand',
        'ZrotCommand',
        'AirfoilCommand',
        'AirfoilMergeCommand',
        'BallooningCommand',
        'BallooningMergeCommand',
        'CellCommand',
        'LineCommand',
        'CutCommand',
        'ColorCommand',
        'Gl2dExport']

    featureBox = [
        'GliderRibFeatureCommand',
        'GliderBallooningFeatureCommand',
        'GliderSharkFeatureCommand',
        'GliderSingleSkinRibFeatureCommand',
        'GliderHoleFeatureCommand',
        'GliderFlapFeatureCommand']

    productionBox = [
        'PatternCommand',
        'PanelCommand',
        'PolarsCommand']

    devBox = [
        'RefreshCommand']

    def GetClassName(self):
        return 'Gui::PythonWorkbench'

    def Initialize(self):
        from . import tools
        global Dir

        Gui.addCommand('CreateGlider', tools.CreateGlider())
        Gui.addCommand('ShapeCommand', tools.ShapeCommand())
        Gui.addCommand('AirfoilCommand', tools.AirfoilCommand())
        Gui.addCommand('ArcCommand', tools.ArcCommand())
        Gui.addCommand('AoaCommand', tools.AoaCommand())
        Gui.addCommand('BallooningCommand', tools.BallooningCommand())
        Gui.addCommand('LineCommand', tools.LineCommand())

        Gui.addCommand('ImportGlider', tools.ImportGlider())
        Gui.addCommand('Gl2dExport', tools.Gl2dExport())
        Gui.addCommand('AirfoilMergeCommand', tools.AirfoilMergeCommand())
        Gui.addCommand('BallooningMergeCommand', tools.BallooningMergCommand())
        Gui.addCommand('CellCommand', tools.CellCommand())
        Gui.addCommand('ZrotCommand', tools.ZrotCommand())
        Gui.addCommand('CutCommand', tools.CutCommand())
        Gui.addCommand('ColorCommand', tools.ColorCommand())

        Gui.addCommand('PatternCommand', tools.PatternCommand())
        Gui.addCommand('PanelCommand', tools.PanelCommand())
        Gui.addCommand('PolarsCommand', tools.PolarsCommand())

        Gui.addCommand('GliderRibFeatureCommand', tools.GliderRibFeatureCommand())
        Gui.addCommand('GliderBallooningFeatureCommand', tools.GliderBallooningFeatureCommand())
        Gui.addCommand('GliderSharkFeatureCommand', tools.GliderSharkFeatureCommand())
        Gui.addCommand('GliderSingleSkinRibFeatureCommand', tools.GliderSingleSkinRibFeatureCommand())
        Gui.addCommand('GliderHoleFeatureCommand', tools.GliderHoleFeatureCommand())
        Gui.addCommand('GliderFlapFeatureCommand', tools.GliderFlapFeatureCommand())

        Gui.addCommand('RefreshCommand', tools.RefreshCommand())

        self.appendToolbar('GliderTools', self.toolBox)
        self.appendToolbar('Production', self.productionBox)
        self.appendToolbar('Feature', self.featureBox)
        self.appendToolbar('Develop', self.devBox)

        self.appendMenu('GliderTools', self.toolBox)
        self.appendMenu('Production', self.productionBox)
        self.appendMenu('Feature', self.featureBox)

        Gui.addPreferencePage(Dir + '/ui/preferences.ui', 'Display')

    def Activated(self):
        pass

    def Deactivated(self):
        pass

Gui.addWorkbench(gliderWorkbench())