from freecad_dist import fc_install         # custom freecad install
from distutils.core import setup

import glider_gui

setup(cmdclass={'install': fc_install},
      install_requires=["OpenGlider"],     
      name='freecad_glider',
      version=glider_gui.__version__,
      description='gui for openglider in freecad',
      url='http://github.com/hiaselhans/OpenGlider',
      author='booya',
      license='LGPL2',
      packages=["glider_gui", "glider_gui/tools", "glider_gui/icons"],
      package_data = {"": ["*.svg", "*.json"]})

