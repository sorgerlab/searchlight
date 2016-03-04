from setuptools import setup
from distutils.extension import Extension
from Cython.Distutils import build_ext
import numpy as np

setup(
    name="searchlight",
    ext_modules=[
        Extension('searchlight',
                  sources=['searchlight.pyx'],
                  libraries=["m"],
                  extra_compile_args=["-ffast-math", "-fopenmp"],
                  extra_link_args=["-fopenmp", "-liomp5"],
                  )
        ],
    cmdclass={'build_ext': build_ext},
    include_dirs=[np.get_include()],
)
