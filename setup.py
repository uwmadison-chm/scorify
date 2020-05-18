#!/usr/bin/env python
# -*- coding: utf-8 -*-

SETUP_REQUIRES = ['setuptools >= 30.3.0']
SETUP_REQUIRES += ['wheel'] if 'bdist_wheel' in sys.argv else []

from setuptools import setup, find_packages
from pathlib import Path

def get_locals(filename):
    l = {}
    exec(open(filename, 'r').read(), {}, l)
    return l


info = get_locals(Path('scorify/info.py'))

setup(
    name="scorify",
    setup_requires=SETUP_REQUIRES,
    version=info['version'],
    packages=find_packages()
)
