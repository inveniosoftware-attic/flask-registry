# -*- coding: utf-8 -*-
##
## This file is part of Flask-Registry
## Copyright (C) 2013, 2014 CERN.
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
Core Registries
===============

The core registries are useful to use as subclasses for other more
advanced registries. The provide the basic functionality for ``list`` and
``dict`` style registries, as well as simple import path and module style
registries.
"""

from __future__ import absolute_import

from werkzeug.utils import find_modules, import_string

try:
    from collections import Sequence, MutableMapping
except ImportError:
    from collections.abs import Sequence, MutableMapping

from ..base import RegistryBase, RegistryError


class ListRegistry(RegistryBase, Sequence):
    """
    Basic registry that just keeps a list of objects. Provides normal
    list-style access to the registry:

    >>> from flask import Flask
    >>> from flask_registry import Registry, ListRegistry
    >>> app = Flask('myapp')
    >>> r = Registry(app=app)
    >>> r['myns'] = ListRegistry()
    >>> r['myns'].register("something")
    >>> len(r['myns'])
    1
    >>> r['myns'][0]
    'something'
    >>> "something" in r['myns']
    True
    >>> for obj in r['myns']:
    ...     print(obj)
    something
    """
    def __init__(self):
        super(ListRegistry, self).__init__()
        self.registry = []

    def __iter__(self):
        """ Get iterator """
        return iter(self.registry)

    def __len__(self):
        """ Get number of object registered """
        return len(self.registry)

    def __contains__(self, item):
        """
        Check if an object has been registered.

        :param item: Object instance
        """
        return item in self.registry

    def __getitem__(self, idx):
        """
        Get registered object via indexing

        :param idx: Index of object
        """
        return self.registry[idx]

    def register(self, item):  # pylint: disable=W0221
        """
        Register a new object

        :param item: Object to register
        """
        self.registry.append(item)

    def unregister(self, item):  # pylint: disable=W0221
        """
        Unregister an existing object. Raises a ``ValueError`` in case object
        does not exists. If the same object was registered twice, only the
        first registered object will be unregister.

        :param item: Object to unregister
        """
        self.registry.remove(item)


class DictRegistry(RegistryBase, MutableMapping):
    """
    Basic registry that just keeps a key, value pairs. Provides normal
    dict-style access to the registry:

    >>> from flask import Flask
    >>> from flask_registry import Registry, DictRegistry
    >>> app = Flask('myapp')
    >>> r = Registry(app=app)
    >>> r['myns'] = DictRegistry()
    >>> r['myns'].register("mykey", "something")
    >>> len(r['myns'])
    1
    >>> r['myns']["mykey"]
    'something'
    >>> "mykey" in r['myns']
    True
    >>> for k, v in r['myns'].items():
    ...     print("%s: %s" % (k,v))
    mykey: something
    """
    def __init__(self):
        super(DictRegistry, self).__init__()
        self.registry = {}

    def __iter__(self):
        return iter(self.registry)

    def __len__(self):
        return len(self.registry)

    def __contains__(self, item):
        return item in self.registry

    def __getitem__(self, key):
        return self.registry[key]

    def __setitem__(self, key, value):
        return self.register(key, value)

    def __delitem__(self, key):
        return self.registry.__delitem__(key)

    def register(self, key, value):  # pylint: disable=W0221
        """
        Register a new object under a given key.

        :param key: Key to register object under
        :param item: Object to register
        """
        if key in self.registry:
            raise RegistryError("Key %s already registered." % key)
        self.registry[key] = value

    def unregister(self, key):  # pylint: disable=W0221
        """
        Unregister an object under a given key. Raises ``KeyError`` in case
        the given key doesn't exists.
        """
        del self.registry[key]


class SingletonRegistry(RegistryBase):
    """
    Basic registry that just keeps a single object.

    >>> from flask import Flask
    >>> from flask_registry import Registry, SingletonRegistry
    >>> app = Flask('myapp')
    >>> r = Registry(app=app)
    >>> r['singleton'] = SingletonRegistry()
    >>> r['singleton'].register("test string")
    >>> r['singleton'].get()
    'test string'
    >>> r['singleton'].register("another string")
    Traceback (most recent call last):
        ...
    RegistryError: Object already registered.
    >>> r['singleton'].unregister()
    >>> r['singleton'].get() is None
    True
    >>> r['singleton'].unregister()
    Traceback (most recent call last):
        ...
    RegistryError: No object to unregister.
    """

    def __init__(self):
        self._singleton = None

    def register(self, obj):
        """
        Register a new singleton object

        :param obj: The object to register
        """
        if self._singleton is not None:
            raise RegistryError("Object already registered.")
        self._singleton = obj

    def unregister(self):
        """
        Unregister the singleton object
        """
        if self._singleton is None:
            raise RegistryError("No object to unregister.")
        self._singleton = None

    def get(self):
        """
        Get the registered object
        """
        return self._singleton


# pylint: disable=R0921
# pylint: disable=R0922
class ImportPathRegistry(ListRegistry):
    """
    Registry of Python import paths. Supports simple discovery of modules
    without loading them.

    >>> from flask import Flask
    >>> from flask_registry import Registry, ImportPathRegistry
    >>> app = Flask('myapp')
    >>> r = Registry(app=app)
    >>> r['myns'] = ImportPathRegistry(initial=[
    ... 'flask_registry.registries.*',
    ... 'flask_registry'])
    >>> for imp_path in r['myns']:
    ...     print(imp_path)
    flask_registry.registries.appdiscovery
    flask_registry.registries.core
    flask_registry.registries.modulediscovery
    flask_registry.registries.pkgresources
    flask_registry

    When using star imports it is sometimes useful to exclude certain imports:

    >>> r['myns2'] = ImportPathRegistry(
    ... initial=['flask_registry.registries.*',     ],
    ... exclude=['flask_registry.registries.core']
    ... )
    >>> for imp_path in r['myns2']:
    ...     print(imp_path)
    flask_registry.registries.appdiscovery
    flask_registry.registries.modulediscovery
    flask_registry.registries.pkgresources

    :param initial: List of initial import paths.
    :param exclude: A list of import paths to not register. Useful together
        with star imports (``'*'``). Defaults to ``[]``.
    :param load_modules: Load the modules instead of just registering the
        import path. Defaults to ``False``.
    """
    def __init__(self, initial=None, exclude=None, load_modules=False):
        super(ImportPathRegistry, self).__init__()
        self.load_modules = load_modules
        self.exclude = exclude or []
        if initial:
            for import_path in initial:
                self.register(import_path)

    def _load_import_path(self, import_path):
        """ Load module behind an import path """
        return import_string(import_path) if self.load_modules else import_path

    def register(self, import_path):
        """
        Register a new import path

        :param import_path: A full Python import path (e.g.
            ``somepackge.somemodule``) or Python star import path to find all
            modules inside a package (e.g. ``somepackge.*``).
        """
        if import_path.endswith('.*'):
            for mod_path in find_modules(import_path[:-2],
                                         include_packages=True):
                if mod_path not in self.exclude:
                    super(ImportPathRegistry, self).register(
                        self._load_import_path(mod_path)
                    )
        else:
            if import_path not in self.exclude:
                super(ImportPathRegistry, self).register(
                    self._load_import_path(import_path)
                )

    def unregister(self, *args, **kwargs):
        """
        It is not possible to unregister import paths.
        """
        raise NotImplementedError()


class ModuleRegistry(ListRegistry):
    """
    Registry for Python modules with setup and teardown functionality.

    Each module may provide a ``setup()`` and ``teardown()`` function which
    will be called when the module is registered. The name of the methods
    can be customized by subclassing and setting the class attributes
    ``setup_func_name`` and ``teardown_func_name``.

    Any extra arguments and keyword arguments to ``register`` and
    ``unregister`` is passed to the setup and teardown functions.

    Example::

        import mod

        registry = ModuleRegistry(with_setup=True)
        registry.register(mod, arg1, arg2, kw1=...)
        # Will call mod.setup(arg1, arg2, kw1=...)

    :param with_setup: Call setup/teardown function when
        registering/unregistering modules. Defaults to ``True``.
    """

    # pylint: disable=W0105
    setup_func_name = 'setup'
    """ Name of setup function. Defaults to ``setup``."""

    teardown_func_name = 'teardown'
    """ Name of teardown function. Defaults to ``teardown``."""

    def __init__(self, with_setup=True):
        super(ModuleRegistry, self).__init__()
        self.with_setup = with_setup

    def register(self, module, *args, **kwargs):
        """
        :param module: Module to register.
        :param args: Argument passed to the module setup function.
        :param kwargs: Keyword argument passed to the module setup function.
        """
        super(ModuleRegistry, self).register(module)
        if self.with_setup:
            setup_func = getattr(module, self.setup_func_name, None)
            if setup_func and callable(setup_func):
                setup_func(*args, **kwargs)

    def unregister(self, module, *args, **kwargs):
        """
        :param module: Module to unregister.
        :param args: Argument passed to the module teardown function.
        :param kwargs: Keyword argument passed to the module teardown function.
        """
        super(ModuleRegistry, self).unregister(module)
        if self.with_setup:
            teardown_func = getattr(module, self.teardown_func_name, None)
            if teardown_func and callable(teardown_func):
                teardown_func(*args, **kwargs)
