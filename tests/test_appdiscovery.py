# -*- coding: utf-8 -*-
##
## This file is part of Flask-Registry
## Copyright (C) 2013 CERN.
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
from flask_registry import (Registry, ExtensionRegistry, PackageRegistry,
                            ConfigurationRegistry, ImportPathRegistry,
                            BlueprintAutoDiscoveryRegistry)


class TestExtensionRegistry(FlaskTestCase):

    def test_registration(self):
        Registry(app=self.app)

        self.app.config['EXTENSIONS'] = ['tests.mockext']

        assert 'MOCKEXT' not in self.app.config

        self.app.extensions['registry']['extensions'] = \
            ExtensionRegistry(self.app)

        assert self.app.config['MOCKEXT']

        self.assertRaises(
            NotImplementedError,
            self.app.extensions['registry']['extensions'].unregister)


class TestPackageRegistry(FlaskTestCase):
    def test_registration(self):
        Registry(app=self.app)

        self.app.config['PACKAGES'] = ['tests.*']

        self.app.extensions['registry']['packages'] = \
            PackageRegistry(self.app)

        self.assertEqual(
            len(self.app.extensions['registry']['packages']),
            13
        )


class TestConfigurationRegistry(FlaskTestCase):
    def test_registration(self):
        Registry(app=self.app)

        initial_app_config_id = id(self.app.config)

        self.app.config['PACKAGES'] = ['tests']
        self.app.config['USER_CFG'] = True

        self.app.extensions['registry']['packages'] = \
            PackageRegistry(self.app)

        assert 'DEFAULT_CFG' not in self.app.config

        self.app.extensions['registry']['config'] = \
            ConfigurationRegistry(self.app)

        assert self.app.config['USER_CFG']
        assert self.app.config['DEFAULT_CFG']
        assert len(self.app.config['PACKAGES']) == 1

        self.assertRaises(
            NotImplementedError,
            self.app.extensions['registry']['config'].unregister
        )

        assert initial_app_config_id == id(self.app.config)


class TestBlueprintAutoDiscoveryRegistry(FlaskTestCase):
    def test_registration(self):
        Registry(app=self.app)

        self.app.extensions['registry']['packages'] = \
            ImportPathRegistry(initial=['tests'])

        self.app.extensions['registry']['blueprints'] = \
            BlueprintAutoDiscoveryRegistry(app=self.app)

        self.assertEqual(
            len(self.app.extensions['registry']['blueprints']),
            3
        )

    def test_import_error(self):
        Registry(app=self.app)

        self.app.extensions['registry']['packages'] = \
            ImportPathRegistry(initial=['flask_registry'])

        self.app.extensions['registry']['blueprints'] = \
            BlueprintAutoDiscoveryRegistry(app=self.app)

        self.assertEqual(
            len(self.app.extensions['registry']['blueprints']),
            0
        )

    def test_syntax_error(self):
        Registry(app=self.app)

        self.app.extensions['registry']['packages'] = \
            ImportPathRegistry(initial=['tests'])

        self.assertRaises(
            SyntaxError,
            BlueprintAutoDiscoveryRegistry,
            app=self.app,
            module_name='syntaxerror_views'
        )

        self.app.extensions['registry'].update(
            blueprints=BlueprintAutoDiscoveryRegistry(
                app=self.app,
                module_name='syntaxerror_views',
                silent=True))

        self.assertEqual(
            len(self.app.extensions['registry']['blueprints']),
            0
        )
