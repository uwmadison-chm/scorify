#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages
import os

setup(
    name="scorify",
    version='0.9.1',
    packages=['scorify'],
    description = ('Library for scoring questionnaires'),
    author='Nate Vack',
    author_email='njvack@wisc.edu',
    license='MIT',
    url=url,
    entry_points={
        'console_scripts': [
            'score_data = scorify.scripts.score_data:main'
        ]
    },
    install_requires=[
        'docopt',
        'schema',
        'xlrd',
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
)
