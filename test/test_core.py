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

from unittest import TestCase
from flask import Flask

from flask.ext.registry import Registry, RegistryError, \
    ListRegistry, DictRegistry, ImportPathRegistry, ModuleRegistry


class FlaskTestCase(TestCase):
    """
    Mix-in class for creating the Flask application
    """

    def setUp(self):
        app = Flask(__name__)
        app.config['DEBUG'] = True
        app.config['TESTING'] = True
        app.logger.disabled = True
        self.app = app


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


class MockModule(object):
    def __init__(self):
        self.called_setup = None
        self.called_teardown = None

    def setup(self):
        self.called_setup = True

    def teardown(self):
        self.called_teardown = True

    def assert_called(self):
        assert self.called_setup is True
        assert self.called_teardown is True

    def assert_not_called(self):
        assert self.called_setup is None
        assert self.called_teardown is None


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
