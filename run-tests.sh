#!/bin/sh
#
# This file is part of Flask-Registry
# Copyright (C) 2013, 2014, 2016 CERN.
#
# Flask-Registry is free software; you can redistribute it and/or
# modify it under the terms of the Revised BSD License; see LICENSE
# file for more details.

# pydocstyle flask_registry && \
isort -rc -c -df **/*.py && \
# check-manifest --ignore ".travis-*" && \
sphinx-build -qnNW docs docs/_build/html && \
python setup.py test && \
sphinx-build -qnNW -b doctest docs docs/_build/doctest
