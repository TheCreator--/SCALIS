from setuptools import setup, Extension

setup(name='convolution_surface', version='1.0',  \
      ext_modules=[Extension('convolution_surface', ['convolution_surface_module.cpp'])])