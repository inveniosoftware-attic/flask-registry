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

"""
Extending Flask-Registry
========================
You can easily create your own type of registries by subclassing one of the
existing registries found in the modules under ``flask_registry.registries``.

If you for instance want to create a list registry that only accepts integers,
you could create it like this:

>>> from flask import Flask
>>> from flask_registry import Registry, RegistryError, ListRegistry
>>> class IntListRegistry(ListRegistry):
...     def register(self, item):
...         if not isinstance(item, int):
...             raise ValueError("Object must be of type int")
>>> app = Flask('myapp')
>>> r = Registry(app=app)
>>> r['myns'] = IntListRegistry()
>>> r['myns'].register(1)
>>> r['myns'].register("some string")
Traceback (most recent call last):
  File "/usr/lib/python2.7/doctest.py", line 1289, in __run
    compileflags, 1) in test.globs
  File "<doctest default[7]>", line 1, in <module>
    r['myns'].register("some string")
  File "<doctest default[2]>", line 4, in register
    raise ValueError("Object must be of type int")
ValueError: Object must be of type int
"""
