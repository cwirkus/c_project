"""
setup.py — Build and install the fastmat C extension.

Usage:
    pip install .          # build + install
    pip install -e .       # editable install (dev mode)
    python setup.py build_ext --inplace   # build .pyd/.so in project root

Requirements:
    - Python 3.8+
    - A C compiler (gcc on Linux/macOS, MSVC or MinGW on Windows)
"""

from setuptools import setup, Extension

fastmat_ext = Extension(
    name="fastmat",
    sources=["src/fastmat.c"],
    extra_compile_args=["-O2"],   # optimise — same flag on gcc and clang
)

setup(
    name="fastmat",
    version="0.1.0",
    description="A C-based matrix computation backend for Python",
    author="Chris Wirkus",
    python_requires=">=3.8",
    ext_modules=[fastmat_ext],
)
