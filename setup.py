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
        version="0.2",
        description="A simple ordered tree implementation",
        author="Nullcube Pty Ltd",
        author_email="aldo@nullcube.com",
        license="MIT",
        url="http://www.nullcube.com",
        download_url="http://dev.nullcube.com/download/tinytree-0.2.tar.gz",
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
