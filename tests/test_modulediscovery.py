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
from flask.ext.registry import Registry, ModuleDiscoveryRegistry, \
    ImportPathRegistry, RegistryProxy, RegistryError, \
    ModuleAutoDiscoveryRegistry, ModuleRegistry


class TestModuleDiscoveryRegistry(FlaskTestCase):
    def test_registration(self):
        Registry(app=self.app)

        self.app.extensions['registry'].update(
            pathns=ImportPathRegistry(initial=['flask_registry.*'])
        )

        self.assertEquals(3, len(self.app.extensions['registry']['pathns']))

        self.app.extensions['registry']['myns'] = \
            ModuleDiscoveryRegistry(
                'appdiscovery',
                registry_namespace='pathns')

        with self.app.app_context():
            self.app.extensions['registry']['myns'].discover()
            assert len(self.app.extensions['registry']['myns']) == 1
            from flask_registry.registries import appdiscovery
            assert self.app.extensions['registry']['myns'][0] == appdiscovery

        self.app.extensions['registry']['myns'].discover(app=self.app)

    def test_registration_noapp(self):
        Registry(app=self.app)

        self.app.extensions['registry']['myns'] = ModuleDiscoveryRegistry(
            'notimportant',
        )

        self.assertRaises(
            RegistryError,
            self.app.extensions['registry']['myns'].discover
        )

    def test_exclude(self):
        Registry(app=self.app)

        # Set exclude config
        self.app.config['PATH_NS_APPDISCOVERY_EXCLUDE'] = [
            'flask_registry.registries',
        ]

        self.app.extensions['registry'].update({
            'path.ns': ImportPathRegistry(initial=['flask_registry.*']),
            'myns': ModuleDiscoveryRegistry('appdiscovery',
                                            registry_namespace='path.ns')
        })

        with self.app.app_context():
            self.app.extensions['registry']['myns'].discover()
            assert len(self.app.extensions['registry']['myns']) == 0

    def test_missing_module(self):
        Registry(app=self.app)

        self.app.extensions['registry'].update(
            pathns=ImportPathRegistry(initial=['flask_registry.*']),
            myns=ModuleDiscoveryRegistry('some_non_existing_module',
                                         registry_namespace='pathns'))

        with self.app.app_context():
            self.app.extensions['registry']['myns'].discover()
            assert len(self.app.extensions['registry']['myns']) == 0

    def test_broken_module(self):
        Registry(app=self.app)

        self.app.extensions['registry'].update(
            pathns=ImportPathRegistry(initial=['tests']),
            myns=ModuleDiscoveryRegistry('broken_module',
                                         registry_namespace='pathns'))

        with self.app.app_context():
            self.assertRaises(ImportError,
                              self.app.extensions['registry']['myns'].discover)
            assert len(self.app.extensions['registry']['myns']) == 0

    def test_syntaxerror_module(self):
        Registry(app=self.app)

        self.app.extensions['registry'].update(
            pathns=ImportPathRegistry(initial=['tests']),
            myns=ModuleDiscoveryRegistry('syntaxerror_module',
                                         registry_namespace='pathns'))

        with self.app.app_context():
            self.assertRaises(
                SyntaxError,
                self.app.extensions['registry']['myns'].discover
            )
            assert len(self.app.extensions['registry']['myns']) == 0

        # Silence the error
        self.app.extensions['registry']['myns_silent'] = \
            ModuleDiscoveryRegistry('syntaxerror_module',
                                    registry_namespace='pathns',
                                    silent=True)

        with self.app.app_context():
            self.app.extensions['registry']['myns_silent'].discover()
            assert len(self.app.extensions['registry']['myns_silent']) == 0

    def test_modules_namespace(self):
        from flask_registry import registries
        Registry(app=self.app)

        self.app.extensions['registry']['pathns'] = ModuleRegistry()
        self.app.extensions['registry']['pathns'].register(registries)

        self.app.extensions['registry']['myns'] = \
            ModuleDiscoveryRegistry('appdiscovery',
                                    registry_namespace='pathns')

        with self.app.app_context():
            self.app.extensions['registry']['myns'].discover()
            assert len(self.app.extensions['registry']['myns']) == 1
            from flask_registry.registries import appdiscovery
            assert self.app.extensions['registry']['myns'][0] == appdiscovery

    def test_proxy_ns(self):
        Registry(app=self.app)

        proxy = RegistryProxy(
            'pathns',
            ImportPathRegistry,
            initial=['flask_registry.*']
        )

        with self.app.app_context():
            assert 'pathns' not in self.app.extensions['registry']

            self.app.extensions['registry']['myns'] = \
                ModuleDiscoveryRegistry('appdiscovery',
                                        registry_namespace=proxy)

            assert 'pathns' in self.app.extensions['registry']
            self.assertEqual(3, len(self.app.extensions['registry']['pathns']))

            self.app.extensions['registry']['myns'].discover()

            assert len(self.app.extensions['registry']['myns']) == 1
            from flask_registry.registries import appdiscovery
            assert self.app.extensions['registry']['myns'][0] == appdiscovery


class TestModuleAutoDiscoveryRegistry(FlaskTestCase):
    def test_registration(self):
        Registry(app=self.app)

        self.app.extensions['registry']['pathns'] = \
            ImportPathRegistry(initial=['flask_registry.*'])

        self.assertEqual(3, len(self.app.extensions['registry']['pathns']))

        self.app.extensions['registry']['myns'] = \
            ModuleAutoDiscoveryRegistry('appdiscovery',
                                        app=self.app,
                                        registry_namespace='pathns')

        assert len(self.app.extensions['registry']['myns']) == 1
        from flask_registry.registries import appdiscovery
        assert self.app.extensions['registry']['myns'][0] == appdiscovery

    def test_registry_proxy(self):
        Registry(app=self.app)

        self.app.extensions['registry']['pathns'] = \
            ImportPathRegistry(initial=['flask_registry.*'])

        myns = RegistryProxy(
            'myns', ModuleAutoDiscoveryRegistry, 'appdiscovery',
            registry_namespace='pathns'
        )

        with self.app.app_context():
            self.assertEqual(3, len(self.app.extensions['registry']['pathns']))
            self.assertEqual(1, len(list(myns)))
            from flask_registry.registries import appdiscovery
            self.assertEqual(appdiscovery, myns[0])
