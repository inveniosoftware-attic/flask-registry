# -*- coding: utf-8 -*-
#
# This file is part of Flask-Registry
# Copyright (C) 2014, 2016 CERN.
#
# Flask-Registry is free software; you can redistribute it and/or
# modify it under the terms of the Revised BSD License; see LICENSE
# file for more details.

from __future__ import absolute_import

import sys
from unittest import TestCase

import six

from flask_registry.utils import depends, resolve_dependencies, uses


class TestUtils(TestCase):
    """
    Tests for the main registry class
    """
    def test_line(self):
        def A():
            pass

        @depends('A')
        def B():
            pass

        @uses('A')
        @uses('B')
        def C():
            pass

        plugins = {'A': A, 'B': B, 'C': C}

        output = list(resolve_dependencies(plugins))
        self.assertEqual(output[0][1], A)
        self.assertEqual(output[1][1], B)
        self.assertEqual(output[2][1], C)

    def test_depends(self):
        def A():
            pass

        # soft cycle
        @uses('A', 'C')
        def B():
            pass

        @depends('A')
        @depends('B')
        def C():
            pass

        plugins = {'A': A, 'B': B, 'C': C}

        output = list(resolve_dependencies(plugins))
        self.assertEqual(output[0][1], A)
        self.assertEqual(output[1][1], B)
        self.assertEqual(output[2][1], C)

    def test_cycle(self):
        @depends('C')
        def A():
            pass

        @depends('A')
        def B():
            pass

        @depends('B')
        def C():
            pass

        plugins = {'A': A, 'B': B, 'C': C}

        self.assertRaises(Exception, lambda x: list(resolve_dependencies(x)),
                          plugins)
