from distutils.core import setup

long_description = """
A tiny tree implementation for Python.

Features
========

    * Simple
    * Functional
    * Well-tested

TinyTree requires Python 2.5 or newer.
"""

setup(
        name="tinytree",
        version="0.2.1",
        description="A simple ordered tree implementation",
        long_description=long_description,
        author="Aldo Cortesi",
        author_email="aldo@corte.si",
        license="MIT",
        url="https://github.com/cortesi/tinytree",
        py_modules = ["tinytree"],
        classifiers = [
            "Intended Audience :: Developers",
            "License :: OSI Approved :: MIT License",
            "Development Status :: 4 - Beta",
            "Programming Language :: Python",
            "Operating System :: OS Independent",
            "Topic :: Other/Nonlisted Topic",
            "Topic :: Software Development :: Libraries",
        ]
    )
