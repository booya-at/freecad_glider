from __future__ import division
import os
import numpy as np

from pivy import coin
import FreeCAD as App

from openglider.jsonify import load, dumps, loads
from openglider import mesh
from pivy_primitives_new_new import Line

importpath = os.path.join(os.path.dirname(__file__), '..', 'demokite.ods')


class OGBaseObject(object):
    def __init__(self, obj):
        obj.Proxy = self

    def execute(self, fp):
        pass


class OGBaseVP(object):
    def __init__(self, obj):
        obj.Proxy = self

    def attach(self, vobj):
        pass

    def updateData(self, fp, prop):
        pass

    def getDisplayModes(self, obj):
        mod = ["out"]
        return(mod)

    def __getstate__(self):
        return None

    def __setstate__(self, state):
        return None


class OGGlider(OGBaseObject):
    def __init__(self, obj):
        obj.addProperty("App::PropertyPythonObject",
                        "glider_instance", "object",
                        "glider_instance", 2)
        obj.addProperty("App::PropertyPythonObject",
                        "glider_2d", "object",
                        "parametric glider", 2)
        with open(os.path.dirname(__file__) + "/../glider2d.json", "r") as importfile:
            obj.glider_2d = load(importfile)["data"]
        obj.glider_instance = obj.glider_2d.get_glider_3d()
        obj.Proxy = self
        self.obj = obj
        super(OGGlider, self).__init__(obj)

    def __getstate__(self):
        out = {
            "glider_2d": dumps(self.obj.glider_2d),
            "name": self.obj.Name}
        return out

    def __setstate__(self, state):
        self.obj = App.ActiveDocument.getObject(state["name"])
        self.obj.addProperty("App::PropertyPythonObject",
                        "glider_instance", "object",
                        "glider_instance", 2)
        self.obj.addProperty("App::PropertyPythonObject",
                        "glider_2d", "object",
                        "parametric glider", 2)
        self.obj.glider_2d = loads(state["glider_2d"])["data"]
        self.obj.glider_instance = self.obj.glider_2d.get_glider_3d()
        return None

class OGGliderVP(OGBaseVP):
    def __init__(self, view_obj):
        view_obj.addProperty("App::PropertyInteger",
                             "num_ribs", "accuracy",
                             "num_ribs")
        view_obj.addProperty("App::PropertyInteger",
                             "profile_num", "accuracy",
                             "profile_num")
        view_obj.addProperty("App::PropertyInteger",
                             "line_num", "accuracy",
                             "line_num")
        view_obj.addProperty("App::PropertyBool",
                             "hull", "visuals",
                             "hull = True")
        view_obj.addProperty("App::PropertyBool",
                             "panels", "visuals",
                             "show panels")
        view_obj.addProperty("App::PropertyBool",
                             "half_glider", "visuals",
                             "show only one half")
        view_obj.addProperty("App::PropertyBool",
                             "ribs", "visuals",
                             "show ribs")
        view_obj.num_ribs = 0
        view_obj.profile_num = 20
        view_obj.line_num = 5
        view_obj.hull = True
        view_obj.ribs = True
        view_obj.half_glider = True
        view_obj.panels =False
        super(OGGliderVP, self).__init__(view_obj)

    def attach(self, view_obj):
        self.vis_glider = coin.SoSeparator()
        self.vis_lines = coin.SoSeparator()
        self.material = coin.SoMaterial()
        self.seperator = coin.SoSeparator()
        self.view_obj = view_obj
        self.glider_instance = view_obj.Object.glider_instance
        self.material.diffuseColor = (.7, .7, .7)
        self.seperator.addChild(self.vis_glider)
        self.seperator.addChild(self.vis_lines)
        self.seperator.addChild(self.material)
        view_obj.addDisplayMode(self.seperator, 'out')

    def updateData(self, fp=None, prop=None):
        if hasattr(self, "view_obj"):
            if prop in ["num_ribs", "profile_num", "hull", "panels",
                        "half_glider", "ribs", None]:
                if hasattr(self.view_obj, "profile_num"):
                    numpoints = self.view_obj.profile_num
                    numpoints = max(numpoints, 5)  # lower limit
                    self.update_glider(midribs=self.view_obj.num_ribs,
                                       profile_numpoints=numpoints,
                                       hull=self.view_obj.hull,
                                       panels=self.view_obj.panels,
                                       half=self.view_obj.half_glider,
                                       ribs=self.view_obj.ribs)
            if prop in ["line_num", "half_glider", None]:
                if hasattr(self.view_obj, "line_num"):
                    self.update_lines(self.view_obj.line_num,
                                      half=self.view_obj.half_glider)

    def update_glider(self, midribs=0, profile_numpoints=20,
                      hull=True, panels=False, half=False, ribs=False):
        self.vis_glider.removeAllChildren()
        if not half:
            glider = self.glider_instance.copy_complete()
        else:
            glider = self.glider_instance.copy()
        draw_glider(glider, self.vis_glider, midribs, profile_numpoints, hull, panels, half, ribs)


    def update_lines(self, num=3, half=False):
        self.vis_lines.removeAllChildren()
        for line in self.glider_instance.lineset.lines:
            points = line.get_line_points(numpoints=num)
            if not half:
                self.vis_lines.addChild(Line([[i[0], -i[1], i[2]] for i in points], dynamic=False))
            self.vis_lines.addChild(Line(points, dynamic=False))

    def onChanged(self, vp, prop):
        print("onChanged")
        self.updateData(vp, prop)

    def getIcon(self):
        return "new_glider.svg"

    def __getstate__(self):
        return None

    def __setstate__(self, state):
        self.updateData()
        return None


def hex_to_rgb(hex_string):
    try:
        value = hex_string.split('#')[1]
        lv = len(value)
        return tuple(int(value[i:i + lv // 3], 16) / 256. for i in range(0, lv, lv // 3))
    except IndexError:
        return (.7, .7, .7)


def draw_glider(glider, vis_glider, midribs=0, profile_numpoints=20,
                hull=True, panels=False, half=False, ribs=False):
    """draw the glider to the visglider seperator"""

    glider.profile_numpoints = profile_numpoints
    count = 0
    if hull:
        if panels:
            for cell in glider.cells:
                count += 1
                for panel in cell.panels:
                    m = panel.get_mesh(cell, midribs + 1)
                    verts = m.vertices.tolist()
                    tris = m.polygons
                    tris_coin = []
                    for tri in tris:
                        tris_coin += tri
                        tris_coin.append(-1)
                    panel_sep = coin.SoSeparator()
                    panel_face = coin.SoIndexedFaceSet()
                    panel_verts = coin.SoVertexProperty()
                    panel_material = coin.SoMaterial()
                    shape_hint = coin.SoShapeHints()
                    shape_hint.vertexOrdering = coin.SoShapeHints.COUNTERCLOCKWISE
                    shape_hint.creaseAngle = np.pi
                    panel_verts.vertex.setValues(0, len(verts), verts)
                    panel_face.coordIndex.setValues(0, len(tris_coin), list(tris_coin))
                    if panel.material_code:
                        panel_material.diffuseColor = hex_to_rgb(panel.material_code)

                    panel_verts.materialBinding = coin.SoMaterialBinding.PER_VERTEX_INDEXED
                    panel_sep.addChild(panel_material)
                    panel_sep.addChild(shape_hint)
                    panel_sep.addChild(panel_verts)
                    panel_sep.addChild(panel_face)
                    vis_glider.addChild(panel_sep)

        elif midribs == 0:
            vertexproperty = coin.SoVertexProperty()
            msh = coin.SoQuadMesh()
            ribs = glider.ribs
            flat_coords = [i for rib in ribs for i in rib.profile_3d.data]
            vertexproperty.vertex.setValues(0, len(flat_coords), flat_coords)
            msh.verticesPerRow = len(ribs[0].profile_3d.data)
            msh.verticesPerColumn = len(ribs)
            msh.vertexProperty = vertexproperty
            vis_glider.addChild(msh)
            vis_glider.addChild(vertexproperty)
        else:
            for cell in glider.cells:
                sep = coin.SoSeparator()
                vertexproperty = coin.SoVertexProperty()
                msh = coin.SoQuadMesh()
                ribs = [cell.midrib(pos / (midribs + 1))
                        for pos in range(midribs + 2)]
                flat_coords = [i for rib in ribs for i in rib]
                vertexproperty.vertex.setValues(0,
                                                len(flat_coords),
                                                flat_coords)
                msh.verticesPerRow = len(ribs[0])
                msh.verticesPerColumn = len(ribs)
                msh.vertexProperty = vertexproperty
                sep.addChild(vertexproperty)
                sep.addChild(msh)
                vis_glider.addChild(sep)
    if ribs:  # show ribs
        msh = mesh.Mesh()
        for rib in glider.ribs:
            if not rib.profile_2d.has_zero_thickness:
                msh += mesh.Mesh.from_rib(rib)
        if msh.vertices is not None:
            verts = list(msh.vertices)
            polygons = []
            for i in msh.polygons:
                polygons += i
                polygons.append(-1)

            rib_sep = coin.SoSeparator()
            vis_glider.addChild(rib_sep)
            vertex_property = coin.SoVertexProperty()
            face_set = coin.SoIndexedFaceSet()

            shape_hint = coin.SoShapeHints()
            shape_hint.vertexOrdering = coin.SoShapeHints.COUNTERCLOCKWISE

            material = coin.SoMaterial()
            material.diffuseColor = (.0, .0, .7)
            rib_sep.addChild(material)

            vertex_property.vertex.setValues(0, len(verts), verts)
            face_set.coordIndex.setValues(0, len(polygons), list(polygons))
            rib_sep.addChild(shape_hint)
            rib_sep.addChild(vertex_property)
            rib_sep.addChild(face_set)


        msh = mesh.Mesh()
        for cell in glider.cells:
            for diagonal in cell.diagonals:
                msh += mesh.Mesh.from_diagonal(diagonal, cell, insert_points=4)
            if msh.vertices is not None:
                verts = list(msh.vertices)
                polygons = []
                for i in msh.polygons:
                    polygons += i
                    polygons.append(-1)

                diagonal_sep = coin.SoSeparator()
                vis_glider.addChild(diagonal_sep)
                vertex_property = coin.SoVertexProperty()
                face_set = coin.SoIndexedFaceSet()

                shape_hint = coin.SoShapeHints()
                shape_hint.vertexOrdering = coin.SoShapeHints.COUNTERCLOCKWISE

                material = coin.SoMaterial()
                material.diffuseColor = (.7, .0, .0)
                diagonal_sep.addChild(material)
                vertex_property.vertex.setValues(0, len(verts), verts)
                face_set.coordIndex.setValues(0, len(polygons), list(polygons))
                diagonal_sep.addChild(shape_hint)
                diagonal_sep.addChild(vertex_property)
                diagonal_sep.addChild(face_set)
