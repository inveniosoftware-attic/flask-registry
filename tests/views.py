# -*- coding: utf-8 -*-
#
# This file is part of Flask-Registry
# Copyright (C) 2013, 2014, 2015 CERN.
#
# Flask-Registry is free software; you can redistribute it and/or
# modify it under the terms of the Revised BSD License; see LICENSE
# file for more details.

"""
Test file for BlueprintAutoDiscoverRegistry testing
"""

from flask import Blueprint

blueprint = Blueprint('test', __name__)

blueprints = [
    Blueprint('test1', __name__),
    Blueprint('test2', __name__)
]


@blueprint.route("/", methods=['GET', ])
def index():
    from flask import current_app
    if current_app.config['USER_CFG'] and current_app.config['DEFAULT_CFG'] \
       and current_app.config['MOCKEXT']:
        return "Hello from Flask-Registry"
    else:
        return "Not everything loaded"
