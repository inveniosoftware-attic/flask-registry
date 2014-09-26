# -*- coding: utf-8 -*-
#
# This file is part of Flask-Registry
# Copyright (C) 2013, 2014, 2015 CERN.
#
# Flask-Registry is free software; you can redistribute it and/or
# modify it under the terms of the Revised BSD License; see LICENSE
# file for more details.

from unittest import TestCase
from flask import Flask


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


class MockModule(object):
    """
    Helper mock module to check that specific methods are called.
    """

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
