#!/usr/bin/env python
# -*- coding: utf-8 -*-

from distutils.core import setup, Command
import os


class PyTest(Command):
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        import sys
        import subprocess
        errno = subprocess.call([sys.executable, 'runtests.py'])
        raise SystemExit(errno)


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
    packages=['scorify'],
    cmdclass={'test': PyTest},
    entry_points={
        'console_scripts': [
            'score_data = scorify.scripts.score_data:main'
        ]}
    )
