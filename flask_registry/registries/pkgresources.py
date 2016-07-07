# -*- coding: utf-8 -*-
#
# This file is part of Flask-Registry
# Copyright (C) 2013, 2014, 2015 CERN.
#
# Flask-Registry is free software; you can redistribute it and/or
# modify it under the terms of the Revised BSD License; see LICENSE
# file for more details.

"""
Package Resources
=================

Package resource registries may be used to discover e.g. package resources
as well as loading entry points.

Entry points
^^^^^^^^^^^^
``setuptools`` entry points are a simple way for packages to "advertise"
Python objects, so that frameworks can search for these entry points.
``setup.py`` files for instance allows you to specify ``console_scripts``
entry points, which will install scripts into system path for you.

The ``EntryPointRegistry`` allows you to easily register these entry points
into your Flask application:

>>> from flask import Flask
>>> from flask_registry import Registry, EntryPointRegistry
>>> app = Flask('myapp')
>>> r = Registry(app=app)
>>> r['scripts'] = EntryPointRegistry('console_scripts')
>>> 'easy_install' in r['scripts']
True

Entry points are specified in you ``setup.py``, e.g.::

    setup(
        # ...
        entry_points={
            'flask_registry.test_entry': [
                'testcase = flask_registry:RegistryBase',
            ]
        },
        # ...
    )

>>> r['entrypoints'] = EntryPointRegistry(
...     'flask_registry.test_entry', load=True)
>>> 'testcase' in r['entrypoints']
True
>>> from flask_registry import RegistryBase
>>> r['entrypoints']['testcase'][0] == RegistryBase
True

See http://pythonhosted.org/setuptools/pkg_resources.html#entry-points for
more information on entry points.

Resource files
^^^^^^^^^^^^^^
The ``PkgResourcesDirDiscoveryRegistry`` will search a list of Python
packages for a specific resource directory and register all files found in the
directories.

Assume e.g. a package ``tests`` have a directory ``resources`` with one file
in it called ``testresource.cfg``. This file can be discovered in the following
manner:

>>> import os
>>> app = Flask('myapp')
>>> r = Registry(app=app)
>>> from flask_registry import ImportPathRegistry
>>> from flask_registry import PkgResourcesDirDiscoveryRegistry
>>> r['packages'] = ImportPathRegistry(initial=['tests'])
>>> r['res'] = PkgResourcesDirDiscoveryRegistry('resources', app=app)
>>> os.path.basename(r['res'][0]) == 'testresource.cfg'
True
"""

from __future__ import absolute_import

import os
from werkzeug.utils import import_string
from pkg_resources import iter_entry_points, resource_listdir, resource_isdir

from .core import DictRegistry
from .modulediscovery import ModuleAutoDiscoveryRegistry


class EntryPointRegistry(DictRegistry):
    """
    Entry point registry. Based on ``DictRegistry`` with keys being
    the entry point group, and the value being a list of objects referenced
    by the entry points.

    :param entry_point_ns: Entry point namespace
    :param load: if False, entry point will not be loaded. Defaults to
        ``True``.
    :param initial: List of initial names. If ``None`` it defaults to all.
    :param exclude: A list of names to not register. Useful together
        with initial equals to ``None``. Defaults to ``[]``.
    :param unique: Allow only unique options in entry point group if ``True``.
    """

    def __init__(self, entry_point_ns, load=True, initial=None, exclude=None,
                 unique=False):
        super(EntryPointRegistry, self).__init__()
        self.load = load
        self.initial = initial or [None]
        self.exclude = set(exclude or [])
        self.unique = unique
        for name in self.initial:
            for entry_point_group in iter_entry_points(entry_point_ns,
                                                       name=name):
                if entry_point_group.name in self.exclude:
                    continue
                self.register(entry_point_group)

    def register(self, entry_point):  # pylint: disable=W0221
        """Register a new entry point

        :param entry_point: The entry point
        """
        value = entry_point.load() if self.load else entry_point
        is_registered = entry_point.name in self.registry
        if self.unique:
            if is_registered:
                raise RuntimeError("{0} is already registered".format(
                    entry_point.name
                ))
            self.registry[entry_point.name] = value
        else:
            if not is_registered:
                self.registry[entry_point.name] = []
            self.registry[entry_point.name].append(value)


class PkgResourcesDirDiscoveryRegistry(ModuleAutoDiscoveryRegistry):
    """
    Specialized ``ModuleAutoDiscoveryRegistry`` that will search a list of
    Python packages in an ``ImportPathRegistry`` or ``ModuleRegistry`` for
    a specific resource directory and register all files found in the
    directories. By default the list of Python packages is read from the
    ``packages`` registry namespace.
    """
    def _discover_module(self, pkg):
        """
        Load list of files from resource directory.
        """
        if resource_isdir(pkg, self.module_name):
            for filename in resource_listdir(pkg, self.module_name):
                self.register(os.path.join(
                    os.path.dirname(import_string(pkg).__file__),
                    self.module_name, filename)
                )
