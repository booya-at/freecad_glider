from setuptools import setup
from freecad.freecad_glider import __version__

setup(name='freecad-glider',
      version=str(__version__),
      packages=['freecad',
                'freecad.freecad_glider',
        'freecad.freecad_glider.tools'],
      maintainer="looooo",
      maintainer_email="sppedflyer@gmail.com",
      url="https://github.com/booya/freecad_glider",
      description="FreeCAD wb for Openglider",
      install_requires=['openglider'],
include_package_data=True)
