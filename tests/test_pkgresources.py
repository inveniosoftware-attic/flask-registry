# -*- coding: utf-8 -*-
##
## This file is part of Flask-Registry
## Copyright (C) 2013, 2014 CERN.
##
## Flask-Registry is free software; you can redistribute it and/or
## modify it under the terms of the GNU General Public License as
## published by the Free Software Foundation; either version 2 of the
## License, or (at your option) any later version.
##
## Flask-Registry is distributed in the hope that it will be useful, but
## WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
## General Public License for more details.
##
## You should have received a copy of the GNU General Public License
## along with Flask-Registry; if not, write to the Free Software Foundation,
## Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307, USA.
##
## In applying this licence, CERN does not waive the privileges and immunities
## granted to it by virtue of its status as an Intergovernmental Organization
## or submit itself to any jurisdiction.

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
