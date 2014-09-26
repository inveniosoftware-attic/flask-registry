# -*- coding: utf-8 -*-
#
# This file is part of Flask-Registry
# Copyright (C) 2013, 2014, 2015 CERN.
#
# Flask-Registry is free software; you can redistribute it and/or
# modify it under the terms of the Revised BSD License; see LICENSE
# file for more details.

from __future__ import absolute_import

import sys
import six

from .helpers import FlaskTestCase
from flask.ext.registry import Registry, RegistryError, RegistryBase, \
    RegistryProxy


class TestRegistry(FlaskTestCase):
    """
    Tests for the main registry class
    """
    def test_version(self):
        # Assert that version number can be parsed.
        from flask_registry import __version__
        from distutils.version import LooseVersion
        LooseVersion(__version__)

    def test_creation(self):
        assert 'registry' not in self.app.extensions
        Registry(app=self.app)
        assert isinstance(self.app.extensions['registry'], Registry)

    def test_creation_old_flask(self):
        # Simulate old Flask
        del self.app.extensions
        Registry(app=self.app)
        assert isinstance(self.app.extensions['registry'], Registry)

    def test_creation_init(self):
        assert 'registry' not in self.app.extensions
        r = Registry()
        r.init_app(app=self.app)
        assert isinstance(self.app.extensions['registry'], Registry)

    def test_double_creation(self):
        Registry(app=self.app)
        self.assertRaises(RegistryError, Registry, app=self.app)

    def test_registration_iter(self):
        Registry(app=self.app)
        self.app.extensions['registry']['mynamespace'] = RegistryBase()
        self.app.extensions['registry']['myothernamespace'] = RegistryBase()

        assert len(self.app.extensions['registry']) == 2
        assert 'mynamespace' in self.app.extensions['registry']
        assert 'myothernamespace' in self.app.extensions['registry']

        # Double registration
        try:
            self.app.extensions['registry']['mynamespace'] = RegistryBase()
            raise AssertionError("No exception raise for double registration")
        except RegistryError:
            pass

        # Registered object
        assert isinstance(
            self.app.extensions['registry']['mynamespace'],
            RegistryBase
        )
        assert isinstance(
            self.app.extensions['registry']['myothernamespace'],
            RegistryBase
        )

        # Iteration
        assert set(self.app.extensions['registry']) == \
            set(['myothernamespace', 'mynamespace', ])

        for ns, r in self.app.extensions['registry'].items():
            assert ns in ['mynamespace', 'myothernamespace']

        # Removal
        myregistry = self.app.extensions['registry']['mynamespace']
        assert myregistry.namespace
        del self.app.extensions['registry']['mynamespace']
        assert myregistry.namespace is None

    def test_namespace_injection(self):
        Registry(app=self.app)
        self.app.extensions['registry']['mynamespace'] = RegistryBase()
        assert self.app.extensions['registry']['mynamespace'].namespace == \
            'mynamespace'

        try:
            self.app.extensions['registry']['mynamespace'].namespace = "na"
            raise AssertionError("RegistryError not raised.")
        except RegistryError:
            pass

    def test_registry_base(self):
        Registry(app=self.app)
        self.app.extensions['registry']['myns'] = RegistryBase()
        self.assertRaises(
            NotImplementedError,
            self.app.extensions['registry']['myns'].register
        )
        self.assertRaises(
            NotImplementedError,
            self.app.extensions['registry']['myns'].unregister
        )


class TestRegistryProxy(FlaskTestCase):
    def test_proxy(self):
        Registry(app=self.app)
        proxy = RegistryProxy('prxns', RegistryBase)

        assert 'prxns' not in self.app.extensions['registry']

        with self.app.app_context():
            self.assertRaises(
                NotImplementedError,
                proxy.register
            )
            assert 'prxns' in self.app.extensions['registry']
            assert isinstance(
                self.app.extensions['registry']['prxns'],
                RegistryBase
            )

    def test_proxy_noregistry(self):
        proxy = RegistryProxy('prxns', RegistryBase)
        with self.app.app_context():
            try:
                proxy.register()
                raise AssertionError(
                    "Registry is supposed not to be avialable"
                )
            except RegistryError:
                pass


class TestExampleApp(FlaskTestCase):
    def setUp(self):
        from tests.example_app import create_app, Config
        self.config = Config()
        self.app = create_app(self.config)
        self.app.config['DEBUG'] = True
        self.app.config['TESTING'] = True
        self.app.logger.disabled = True
        self.client = self.app.test_client()

    # The following test is known to fail on Python 3.4.0 and 3.4.1
    # while it works well on lesser or higher Pythons.  (Additionally
    # cannot use unittest.skipIf() here due to Python-2.6.)
    if sys.version_info != (3, 4, 0, 'final', 0) and \
       sys.version_info != (3, 4, 1, 'final', 0):
        def test_blueprint_loaded(self):
            # Test that app is loaded and that blueprints have been registered
            response = self.client.get("/")
            self.assertEqual(response.data, six.b("Hello from Flask-Registry"))
