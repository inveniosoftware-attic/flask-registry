# -*- coding: utf-8 -*-
#
# This file is part of Flask-Registry
# Copyright (C) 2013, 2014, 2015 CERN.
#
# Flask-Registry is free software; you can redistribute it and/or
# modify it under the terms of the Revised BSD License; see LICENSE
# file for more details.

from __future__ import absolute_import

from .helpers import FlaskTestCase
from flask.ext.registry import (Registry, RegistryBase,
                                PkgResourcesDirDiscoveryRegistry,
                                ImportPathRegistry, EntryPointRegistry)


class TestPkgResourcesDiscoveryRegistry(FlaskTestCase):

    def test_registration(self):
        Registry(app=self.app)

        self.app.extensions['registry'].update(
            pathns=ImportPathRegistry(initial=['tests']))
        self.app.extensions['registry'].update(
            myns=PkgResourcesDirDiscoveryRegistry('resources',
                                                  app=self.app,
                                                  registry_namespace='pathns'))

        self.assertEquals(1, len(self.app.extensions['registry']['myns']))

    def test_missing_folder(self):
        Registry(app=self.app)

        self.app.extensions['registry'].update(
            pathns=ImportPathRegistry(initial=['tests']))
        self.app.extensions['registry'].update(
            myns=PkgResourcesDirDiscoveryRegistry('non_existing_folder',
                                                  app=self.app,
                                                  registry_namespace='pathns'))

        self.assertEquals(0, len(self.app.extensions['registry']['myns']))


class TestEntryPointRegistry(FlaskTestCase):
    def test_regsitration(self):
        Registry(app=self.app)

        self.app.extensions['registry']['myns'] = \
            EntryPointRegistry('flask_registry.test_entry')

        self.assertEqual(len(self.app.extensions['registry']['myns']), 1)
        assert 'testcase' in self.app.extensions['registry']['myns']

    def test_load(self):
        Registry(app=self.app)

        self.app.extensions['registry']['myns'] = \
            EntryPointRegistry('flask_registry.test_entry', load=True)

        self.assertEqual(len(self.app.extensions['registry']['myns']), 1)
        assert RegistryBase == \
            self.app.extensions['registry']['myns']['testcase'][0]
