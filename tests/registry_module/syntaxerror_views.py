# -*- coding: utf-8 -*-
#
# This file is part of Flask-Registry
# Copyright (C) 2013, 2014, 2016 CERN.
#
# Flask-Registry is free software; you can redistribute it and/or
# modify it under the terms of the Revised BSD License; see LICENSE
# file for more details.

"""Test file for BlueprintAutoDiscoverRegistry testing of syntax errors."""

from flask import Blueprint

# SYNTAX ERROR IS ON PURPOSE
blueprint = Blueprint('test', __name__
