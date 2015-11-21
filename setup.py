from freecad_dist import fc_install         # custom freecad install
from setuptools import setup

import freecad_glider

setup(cmdclass={'install': fc_install},
      install_requires=["OpenGlider"],     
      name='freecad_glider',
      version=freecad_glider.__version__,
      description='gui for openglider in freecad',
      url='http://github.com/hiaselhans/OpenGlider',
      author='booya',
      license='LGPL2',
      packages=["freecad_glider", "freecad_glider/tools", "freecad_glider/icons"],
      package_data = {"": ["*.svg", "*.json"]})

