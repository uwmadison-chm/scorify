#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages
import os

from xlrd.info import *

setup(
    name="scorify",
    version=version,
    packages=['scorify'],
    description = ('Library for scoring questionnaires'),
    author=author,
    author_email=author_email,
    license=licence,
    url=url,
    entry_points={
        'console_scripts': [
            'score_data = scorify.scripts.score_data:main'
        ]
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
)
