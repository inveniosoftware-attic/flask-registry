# -*- coding: utf-8 -*-
#
# This file is part of Flask-Registry
# Copyright (C) 2013, 2014, 2016 CERN.
#
# Flask-Registry is free software; you can redistribute it and/or
# modify it under the terms of the Revised BSD License; see LICENSE
# file for more details.

"""
Flask-Registry extensions.

Extending Flask-Registry
========================
You can easily create your own type of registries by subclassing one of the
existing registries found in the modules under ``flask_registry.registries``.

If you for instance want to create a list registry that only accepts integers,
you could create it like this:

.. doctest::

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
