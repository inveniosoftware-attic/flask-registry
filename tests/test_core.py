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

import six

from .helpers import FlaskTestCase, MockModule
from flask.ext.registry import Registry, RegistryError, \
    ListRegistry, DictRegistry, ImportPathRegistry, ModuleRegistry, \
    SingletonRegistry


class TestListRegistry(FlaskTestCase):
    def test_registration(self):
        Registry(app=self.app)
        self.app.extensions['registry']['myns'] = ListRegistry()
        self.app.extensions['registry']['myns'].register('item1')
        self.app.extensions['registry']['myns'].register('item2')

        assert len(self.app.extensions['registry']['myns']) == 2
        assert 'item1' in self.app.extensions['registry']['myns']
        assert 'notin' not in self.app.extensions['registry']['myns']
        assert list(self.app.extensions['registry']['myns'])

        self.app.extensions['registry']['myns'].unregister('item2')
        assert len(self.app.extensions['registry']['myns']) == 1
        assert 'item1' in self.app.extensions['registry']['myns']
        assert 'item2' not in self.app.extensions['registry']['myns']


class TestDictRegistry(FlaskTestCase):
    def test_registration(self):
        Registry(app=self.app)
        self.app.extensions['registry']['myns'] = DictRegistry()
        self.app.extensions['registry']['myns'].register('key1', 'item1')
        self.app.extensions['registry']['myns']['key2'] = 'item2'

        self.assertRaises(
            RegistryError,
            self.app.extensions['registry']['myns'].register,
            'key2', 'item3'
        )

        assert len(self.app.extensions['registry']['myns']) == 2
        assert len(self.app.extensions['registry']['myns'].items()) == 2
        assert 'key2' in self.app.extensions['registry']['myns']
        assert 'notin' not in self.app.extensions['registry']['myns']
        assert list(self.app.extensions['registry']['myns'])

        assert self.app.extensions['registry']['myns']['key2'] == 'item2'

        self.app.extensions['registry']['myns'].unregister('key2')
        assert len(self.app.extensions['registry']['myns']) == 1
        assert 'key1' in self.app.extensions['registry']['myns']
        assert 'key2' not in self.app.extensions['registry']['myns']

        del self.app.extensions['registry']['myns']['key1']
        assert len(self.app.extensions['registry']['myns']) == 0


class TestSingletonRegistry(FlaskTestCase):
    def test_registration(self):
        Registry(app=self.app)
        self.app.extensions['registry']['myns'] = SingletonRegistry()
        self.app.extensions['registry']['myns'].register('item1')
        assert self.app.extensions['registry']['myns'].get() == 'item1'

        self.assertRaises(
            RegistryError,
            self.app.extensions['registry']['myns'].register,
            'item 2'
        )

        self.app.extensions['registry']['myns'].unregister()
        assert self.app.extensions['registry']['myns'].get() is None

        self.assertRaises(
            RegistryError,
            self.app.extensions['registry']['myns'].unregister,
        )


class TestImportPathRegistry(FlaskTestCase):
    def test_registration(self):
        Registry(app=self.app)
        self.app.extensions['registry']['impns'] = ImportPathRegistry()

        self.app.extensions['registry']['impns'].register('flask_registry')
        self.app.extensions['registry']['impns'].register(
            'flask_registry.registries.*'
        )

        assert len(self.app.extensions['registry']['impns']) == 5
        assert 'flask_registry.registries.core' in \
            self.app.extensions['registry']['impns']

    def test_init(self):
        Registry(app=self.app)
        self.app.extensions['registry']['impns'] = ImportPathRegistry(
            initial=['flask_registry.registries.*']
        )
        assert len(self.app.extensions['registry']['impns']) == 4
        assert isinstance(
            self.app.extensions['registry']['impns'][0], six.string_types
        )

    def test_load_modules(self):
        Registry(app=self.app)
        self.app.extensions['registry']['impns'] = ImportPathRegistry(
            initial=['flask_registry.registries.*'], load_modules=True
        )
        assert len(self.app.extensions['registry']['impns']) == 4
        assert not isinstance(
            self.app.extensions['registry']['impns'][0], six.string_types
        )

    def test_exclude(self):
        Registry(app=self.app)
        self.app.extensions['registry']['impns'] = ImportPathRegistry(
            initial=['flask_registry.registries.*'],
            exclude=['flask_registry.registries.pkgresources'],
        )
        assert len(self.app.extensions['registry']['impns']) == 3
        assert 'flask_registry.registries.pkgresources' not in \
            self.app.extensions['registry']['impns']

    def test_unregister(self):
        Registry(app=self.app)
        self.app.extensions['registry']['impns'] = ImportPathRegistry(
            initial=['flask_registry.registries.*']
        )

        self.assertRaises(
            NotImplementedError,
            self.app.extensions['registry']['impns'].unregister,
            'flask_registry.*'
        )


class TestModuleRegistry(FlaskTestCase):
    def test_creation(self):
        Registry(app=self.app)
        self.app.extensions['registry']['modns'] = ModuleRegistry()

        moda = MockModule()

        self.app.extensions['registry']['modns'].register(moda)
        self.app.extensions['registry']['modns'].unregister(moda)
        moda.assert_called()

    def test_creation_setup(self):
        Registry(app=self.app)
        self.app.extensions['registry']['modns'] = ModuleRegistry(
            with_setup=False
        )

        moda = MockModule()

        self.app.extensions['registry']['modns'].register(moda)
        self.app.extensions['registry']['modns'].unregister(moda)
        moda.assert_not_called()
