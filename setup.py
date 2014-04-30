#!/usr/bin/env python
# Copyright (c) 2013 Antoine Musso
# Copyright (c) Wikimedia Foundation Inc.
#
# Licensed under the GPL Version 2.0
# See LICENSE for details.

from setuptools import setup, find_packages

setup(
    name='gerritclone',
    version='0.1',
    packages=find_packages(),

    # scripts=['git-gerritclone'],
    entry_points={
        'console_scripts': [
            'gerritclone = gerritclone.cmd:main',
            'git-gerritclone = gerritclone.cmd:main',
        ],
    },

    # PyPI metadata
    author='Antoine Musso, Wikimedia Foundation Inc.',
    author_email='hashar@free.fr',
    description=('Helper to easily clone a repository from Gerrit '
                 'installations'),
    license='GPL v2.0',
    keywords='gerrit clone project git',

)
