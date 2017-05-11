#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages
import os


def get_locals(filename):
    l = {}
    with open(filename, 'r') as f:
        code = compile(f.read(), filename, 'exec')
        exec(code, {}, l)
    return l


metadata = get_locals(os.path.join('scorify', '_metadata.py'))

setup(
    name="scorify",
    version=metadata['version'],
    author=metadata['author'],
    author_email=metadata['author_email'],
    license=metadata['license'],
    url=metadata['url'],
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'score_data = scorify.scripts.score_data:main'
        ]}
    )
