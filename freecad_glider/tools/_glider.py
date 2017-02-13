from __future__ import division
import os
import numpy as np

import openglider.glider
from pivy import coin
import FreeCAD as App
import FreeCAD

from openglider import jsonify
from openglider import mesh
from . import pivy_primitives_new_new as prim

importpath = os.path.join(os.path.dirname(__file__), '..', 'demokite.ods')


# a list of all deafault parameters
preference_table = {"default_show_half_glider": (bool, True),
                    "default_show_panels": (bool, False),
                    "default_num_prof_points": (int, 20),
                    "default_num_cell_points": (int, 0),
                    "default_num_line_points": (int, 2),
                    "default_num_hole_points": (int, 10)}


def get_parameter(name):
    glider_defaults = App.ParamGet("User parameter:BaseApp/Preferences/Mod/glider")
    if preference_table[name][0] == bool:
        return glider_defaults.GetBool(name, preference_table[name][1])
    elif preference_table[name][0] == int:
        return glider_defaults.GetInt(name, preference_table[name][1])


def refresh():
    print("reloading")
    reload(coin)
    reload(jsonify)
    reload(mesh)
    reload(prim)


def mesh_sep(mesh, color, draw_lines=True):
    vertices, polygons_grouped, _ = mesh.get_indexed()
    polygons = sum(polygons_grouped.values(), [])
    _vertices = [list(v) for v in vertices]
    _polygons = []
    _lines = []
    for i in polygons:
        _polygons += i
        _lines += i
        _lines.append(i[0])
        _polygons.append(-1)
        _lines.append(-1)

    sep = coin.SoSeparator()
    vertex_property = coin.SoVertexProperty()
    face_set = coin.SoIndexedFaceSet()
    shape_hint = coin.SoShapeHints()
    shape_hint.vertexOrdering = coin.SoShapeHints.COUNTERCLOCKWISE
    shape_hint.creaseAngle = np.pi / 3
    face_mat = coin.SoMaterial()
    face_mat.diffuseColor = color
    vertex_property.vertex.setValues(0, len(_vertices), _vertices)
    face_set.coordIndex.setValues(0, len(_polygons), list(_polygons))
    vertex_property.materialBinding = coin.SoMaterialBinding.PER_VERTEX_INDEXED
    sep += shape_hint, vertex_property, face_mat, face_set

    if draw_lines:
        line_set = coin.SoIndexedLineSet()
        line_set.coordIndex.setValues(0, len(_lines), list(_lines))
        line_mat = coin.SoMaterial()
        line_mat.diffuseColor = (.0, .0, .0)
        sep += line_mat, line_set
    return sep


class OGBaseObject(object):
    def __init__(self, obj):
        obj.Proxy = self
        self.obj = obj

    def execute(self, fp):
        pass


class OGBaseVP(object):
    def __init__(self, obj):
        obj.Proxy = self
        self.view_obj = obj
        self.obj = obj.Object

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
    def __init__(self, parametric_glider):
        obj = FreeCAD.ActiveDocument.addObject("App::FeaturePython", "Glider")
        self.obj = obj
        obj.addProperty("App::PropertyPythonObject",
                        "GliderInstance", "object",
                        "GliderInstance", 2)
        obj.addProperty("App::PropertyPythonObject",
                        "ParametricGlider", "object",
                        "ParametricGlider", 2)

        obj.ParametricGlider = parametric_glider
        #obj.GliderInstance = obj.ParametricGlider.get_glider_3d()
        obj.Proxy = self
        super(OGGlider, self).__init__(obj)

    @classmethod
    def load(cls, import_path):
        if import_path.endswith(".json"):
            with open(import_path, "r") as importfile:
                glider = jsonify.load(importfile)["data"]
        elif import_path.endswith(".ods"):
            glider = openglider.glider.ParametricGlider.import_ods(import_path)
        else:
            raise ValueError()

        return cls(glider)

    def __getstate__(self):
        out = {
            "ParametricGlider": jsonify.dumps(self.obj.ParametricGlider),
            "name": self.obj.Name}
        return out

    def __setstate__(self, state):
        self.obj = App.ActiveDocument.getObject(state["name"])
        self.obj.addProperty("App::PropertyPythonObject",
                             "GliderInstance", "object",
                             "GliderInstance", 2)
        self.obj.addProperty("App::PropertyPythonObject",
                             "ParametricGlider", "object",
                             "parametric glider", 2)
        self.obj.ParametricGlider = jsonify.loads(state["ParametricGlider"])["data"]
        #self.obj.GliderInstance = self.obj.ParametricGlider.get_glider_3d()
        return None


class OGGliderVP(OGBaseVP):
    def __init__(self, view_obj):
        view_obj.addProperty("App::PropertyBool",
                             "ribs", "visuals",
                             "show ribs")
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
                             "draw_mesh", "visuals",
                             "draw lines of the mesh")
        view_obj.addProperty("App::PropertyInteger",
                             "hole_num", "visuals",
                             "number of hole vertices")

        self.set_defaults(view_obj)
        super(OGGliderVP, self).__init__(view_obj)

    def set_defaults(self, view_obj):
        view_obj.num_ribs = get_parameter("default_num_cell_points")
        view_obj.profile_num = get_parameter("default_num_prof_points")
        view_obj.line_num = get_parameter("default_num_line_points")
        view_obj.hull = True
        view_obj.ribs = True
        view_obj.half_glider = get_parameter("default_show_half_glider")
        view_obj.panels = get_parameter("default_show_panels")
        view_obj.draw_mesh = False
        view_obj.hole_num = get_parameter("default_num_hole_points")

    def attach(self, view_obj):
        self.vis_lines = coin.SoSeparator()
        self.vis_panels = coin.SoSeparator()
        self.vis_ribs = coin.SoSeparator()
        self.material = coin.SoMaterial()
        self.seperator = coin.SoSeparator()
        self.view_obj = view_obj
        self.update_glider(view_obj)
        self.material.diffuseColor = (.7, .7, .7)
        self.seperator.addChild(self.vis_lines)
        self.seperator.addChild(self.vis_panels)
        self.seperator.addChild(self.vis_ribs)

        pick_style = coin.SoPickStyle()
        pick_style.style.setValue(coin.SoPickStyle.BOUNDING_BOX)
        self.seperator.addChild(pick_style)

        view_obj.addDisplayMode(self.seperator, 'out')

    def update_glider(self, view_obj):
        view_obj.Object.ParametricGlider.num_profile = view_obj.profile_num
        glider = view_obj.Object.ParametricGlider.get_glider_3d()
        if not view_obj.half_glider:
            self.glider = glider.copy_complete()
        else:
            self.glider = glider.copy()

    def updateData(self, prop="all", *args):
        self.onChanged(self.view_obj, prop)

    def onChanged(self, view_obj, prop):
        if not hasattr(view_obj, "half_glider") or not hasattr(view_obj, "ribs"):
            print(prop)
            return  # the viewprovider isn't set up at this moment
                    # but calls already the update function

        if not hasattr(self, "glider"):
            self.update_glider(self.view_obj)

        #self.seperator.removeAllChildren()
        # pick_style = coin.SoPickStyle()
        # pick_style.style.setValue(coin.SoPickStyle.BOUNDING_BOX)
        # self.seperator.addChild(pick_style)

        if prop in ["profile_num", "half_glider", "all"]:
            self.update_all(view_obj)

        elif prop == "num_ribs":
            self.vis_panels.removeAllChildren()

        elif prop == "hole_num":
            self.vis_ribs.removeAllChildren()

        # show ribs
        if view_obj.ribs:
            if len(self.vis_ribs) == 0:
                self.update_ribs()
            if self.vis_ribs not in self.seperator:
                self.seperator.addChild(self.vis_ribs)
        else:
            self.seperator.removeChild(self.vis_ribs)

        # show panels
        if view_obj.panels:
            if len(self.vis_panels) == 0:
                self.update_panels(view_obj.num_ribs)
            if self.vis_panels not in self.seperator:
                self.seperator.addChild(self.vis_panels)
        else:
            self.seperator.removeChild(self.vis_panels)

        if prop in ["line_num", "all"]:
            self.update_lines(view_obj.line_num)
            #self.seperator.addChild(self.vis_lines)

    def update_all(self, view_obj):
        print("jojo, update all", view_obj.line_num)
        self.update_glider(view_obj)
        self.update_panels(view_obj.num_ribs)
        self.update_ribs()
        self.update_diagonals()
        self.update_lines(view_obj.line_num)

    def update_panels(self, midribs=0, draw_mesh=False):
        self.vis_panels.removeAllChildren()
        for cell in self.glider.cells:
            for panel in cell.panels:
                m = panel.get_mesh(cell, midribs, with_numpy=True)
                color = (.3, .3, .3)
                if panel.material_code:
                    color = hex_to_rgb(panel.material_code)
                self.vis_panels.addChild(mesh_sep(m,  color, draw_mesh))

    def update_ribs(self):
        self.vis_ribs.removeAllChildren()
        msh = mesh.Mesh()
        for rib in self.glider.ribs:
            if not rib.profile_2d.has_zero_thickness:
                msh += mesh.Mesh.from_rib(rib, self.view_obj.hole_num, mesh_option="QYqazip")
        if msh.vertices is not None:
            self.vis_ribs.addChild(mesh_sep(msh, (.3, .3, .3), self.view_obj.draw_mesh))

    def update_diagonals(self):
        msh = mesh.Mesh()
        for cell in self.glider.cells:
            for diagonal in cell.diagonals:
                msh += mesh.Mesh.from_diagonal(diagonal, cell, insert_points=4)

            for strap in cell.straps:
                msh += mesh.Mesh.from_diagonal(strap, cell, insert_points=4)

            if msh.vertices is not None:
                self.vis_ribs.addChild(mesh_sep(msh, (.3, .3, .3), self.view_obj.draw_mesh))

    def update_lines(self, num=3):
        self.vis_lines.removeAllChildren()
        pick_style = coin.SoPickStyle()
        pick_style.style.setValue(coin.SoPickStyle.BOUNDING_BOX)
        self.vis_lines.addChild(pick_style)
        self.glider.lineset.recalc()
        for line in self.glider.lineset.lines:
            points = line.get_line_points(numpoints=num)
            self.vis_lines += (prim.Line(points, dynamic=False))
        print(len(self.vis_lines))
        #self.seperator.addChild(self.vis_lines)

    def getIcon(self):
        return "new_glider.svg"

    def __getstate__(self):
        return None

    def __setstate__(self, state):
        # self.updateData()
        return None


def hex_to_rgb(hex_string):
    try:
        value = hex_string.split('#')[1]
        lv = len(value)
        return tuple(int(value[i:i + lv // 3], 16) / 256. for i in range(0, lv, lv // 3))
    except IndexError:
        return (.7, .7, .7)


def draw_glider(glider, vis_glider, midribs=0, profile_numpoints=20,
                hull=True, panels=False, ribs=False,
                draw_mesh=False, hole_num=10):
    """draw the glider to the visglider seperator"""
    glider.profile_numpoints = profile_numpoints
    count = 0
    if hull:
        if panels:
            for cell in glider.cells:
                count += 1
                for panel in cell.panels:
                    m = panel.get_mesh(cell, midribs, with_numpy=True)
                    color = (.3, .3, .3)
                    if panel.material_code:
                        color = hex_to_rgb(panel.material_code)
                    vis_glider += mesh_sep(m,  color, draw_mesh)

        elif midribs == 0:
            vertexproperty = coin.SoVertexProperty()
            msh = coin.SoQuadMesh()
            _ribs = glider.ribs
            flat_coords = [i for rib in _ribs for i in rib.profile_3d.data]
            vertexproperty.vertex.setValues(0, len(flat_coords), flat_coords)
            msh.verticesPerRow = len(_ribs[0].profile_3d.data)
            msh.verticesPerColumn = len(_ribs)
            msh.vertexProperty = vertexproperty
            vis_glider += msh, vertexproperty
        else:
            for cell in glider.cells:
                sep = coin.SoSeparator()
                vertexproperty = coin.SoVertexProperty()
                msh = coin.SoQuadMesh()
                m = cell.get_mesh(midribs, with_numpy=True)
                color = (.8, .8, .8)
                vis_glider += mesh_sep(m,  color, draw_mesh)

    if ribs:  # show ribs
        msh = mesh.Mesh()
        for rib in glider.ribs:
            if not rib.profile_2d.has_zero_thickness:
                msh += mesh.Mesh.from_rib(rib, hole_num, mesh_option="QYqazip")
        if msh.vertices is not None:
            vis_glider += mesh_sep(msh, (.3, .3, .3), draw_mesh)


        msh = mesh.Mesh()
        for cell in glider.cells:
            for diagonal in cell.diagonals:
                msh += mesh.Mesh.from_diagonal(diagonal, cell, insert_points=4)

            for strap in cell.straps:
                msh += mesh.Mesh.from_diagonal(strap, cell, insert_points=4)

            if msh.vertices is not None:
                vis_glider += mesh_sep(msh, (.3, .3, .3), draw_mesh)

        _strap_verts = []
        _strap_lines = []
        _strap_count = 0
        # for cell in glider.cells:
        #     for i, strap in enumerate(cell.straps):
        #         _strap_verts += strap.get_3d(cell)
        #         _strap_lines += [_strap_count * 2, _strap_count * 2 + 1, -1]
        #         _strap_count += 1
        # strap_sep = coin.SoSeparator()
        # vis_glider += strap_sep
        # strap_material = coin.SoMaterial()
        # strap_material.diffuseColor = (0., 0., 0.)
        # strap_verts = coin.SoVertexProperty()
        # strap_set = coin.SoIndexedLineSet()
        # strap_verts.vertex.setValues(0, len(_strap_verts), _strap_verts)
        # strap_set.coordIndex.setValues(0, len(_strap_lines), _strap_lines)
        #
        # strap_sep += strap_material, strap_verts, strap_set
