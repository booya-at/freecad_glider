from ._glider import OGBaseObject, OGGliderVP


class BaseFeature(OGBaseObject):
    def __init__(self, obj, parent):
        self.obj = obj
        obj.addProperty("App::PropertyLink", "parent", "parent", "parent")
        obj.parent = parent
        super(BaseFeature, self).__init__(obj)

    def getGliderInstance(self):
        return self.obj.parent.Proxy.getGliderInstance()

    def setGliderInstance(self, obj):
        self.obj.parent.Proxy.setGliderInstance(obj)

    def getParametricGlider(self):
        return self.obj.parent.Proxy.getParametricGlider()

    def setParametricGlider(self, obj):
        self.obj.parent.Proxy.setParametricGlider(obj)

    def  onDocumentRestored(self, obj):
        self.obj = obj
        obj.ViewObject.Proxy._updateData(obj.ViewObject)


    def __getstate__(self):
        return None

    def __setstate__(self, state):
        return None