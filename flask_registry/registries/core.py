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

from werkzeug.utils import find_modules
from flask_registry import RegistryBase, RegistryError


class ListRegistry(RegistryBase):
    """
    Basic registry that just keeps a list of items.
    """
    def __init__(self):
        self.registry = []

    def __iter__(self):
        return self.registry.__iter__()

    def __len__(self):
        return self.registry.__len__()

    def __contains__(self, item):
        return self.registry.__contains__(item)

    def register(self, item):
        self.registry.append(item)

    def unregister(self, item):
        self.registry.remove(item)


class DictRegistry(RegistryBase):
    """
    Basic registry that just keeps a key, value pairs.
    """
    def __init__(self):
        self.registry = {}

    def __iter__(self):
        return self.registry.__iter__()

    def __len__(self):
        return self.registry.__len__()

    def __contains__(self, item):
        return self.registry.__contains__(item)

    def __getitem__(self, key):
        return self.registry[key]

    def __setitem__(self, key, value):
        return self.register(key, value)

    def __delitem__(self, key):
        return self.registry.__delitem__(key)

    def register(self, key, value):
        if key in self.registry:
            raise RegistryError("Key %s already registered." % key)
        self.registry[key] = value

    def unregister(self, key):
        del self.registry[key]

    def items(self):
        return self.registry.items()


class ImportPathRegistry(ListRegistry):
    """
    Import path registry

    Example::

        registry = ImportPathRegistry(initial=[
            'invenio.core.*',
            'invenio.modules.record',
        ])

        for impstr in registry:
            print impstr
    """
    def __init__(self, initial=None):
        super(ImportPathRegistry, self).__init__()
        if initial:
            for import_path in initial:
                self.register(import_path)

    def register(self, import_path):
        if import_path.endswith('.*'):
            for p in find_modules(import_path[:-2], include_packages=True):
                super(ImportPathRegistry, self).register(p)
        else:
            super(ImportPathRegistry, self).register(import_path)

    def unregister(self, *args, **kwargs):
        raise NotImplementedError()


class ModuleRegistry(ListRegistry):
    """
    Registry for Python modules

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
    """
    setup_func_name = 'setup'
    teardown_func_name = 'teardown'

    def __init__(self, with_setup=True):
        super(ModuleRegistry, self).__init__()
        self.with_setup = with_setup

    def register(self, module, *args, **kwargs):
        super(ModuleRegistry, self).register(module)
        if self.with_setup:
            setup_func = getattr(module, self.setup_func_name, None)
            if setup_func and callable(setup_func):
                setup_func(*args, **kwargs)

    def unregister(self, module, *args, **kwargs):
        super(ModuleRegistry, self).unregister(module)
        if self.with_setup:
            teardown_func = getattr(module, self.teardown_func_name, None)
            if teardown_func and callable(teardown_func):
                teardown_func(*args, **kwargs)
