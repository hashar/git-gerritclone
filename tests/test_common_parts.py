#!/usr/bin/env python
#
# Copyright (c) 2013 Antoine Musso
# Copyright (c) Wikimedia Foundation Inc.
#
# Licensed under the GPL Version 2.0
# See LICENSE for details.
#

import os
import shutil
import tempfile
import unittest

import gerritclone.cmd

TEST_BASE = tempfile.mkdtemp(prefix='gerritclone-test-')


class testCommonParts(unittest.TestCase):

    def setUp(self):
        shutil.rmtree(TEST_BASE)
        dirs = (
            'mediawiki/extensions/VisualEditor',
            'operations/tools',
        )
        for dir in dirs:
            os.makedirs(os.path.join(TEST_BASE, dir))
        os.chdir(TEST_BASE)

    def test_foobar(self):
        res = gerritclone.cmd.common_part(
            'operations/tools/subproject',
            TEST_BASE
        )
        assert res == ''

        os.chdir('operations/tools')
        res = gerritclone.cmd.common_part(
            'operations/tools/subproject',
            TEST_BASE
        )
        assert res == '/operations/tools'
