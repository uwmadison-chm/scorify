#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages
import sys
from os import path

SETUP_REQUIRES = ["setuptools >= 30.3.0"]
SETUP_REQUIRES += ["wheel"] if "bdist_wheel" in sys.argv else []


def get_locals(filename):
    local_vars = {}
    exec(open(filename, "r").read(), {}, local_vars)
    return local_vars


info = get_locals(path.join("scorify", "info.py"))

setup(
    name="scorify",
    setup_requires=SETUP_REQUIRES,
    version=info["version"],
    packages=find_packages(),
)
