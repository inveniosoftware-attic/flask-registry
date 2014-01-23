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
Flask extension
===============

Flask-Registry is initialized like this:

>>> from flask import Flask
>>> from flask_registry import Registry, ListRegistry
>>> app = Flask('myapp')
>>> r = Registry(app=app)

A simple usage example of ``ListRegistry`` looks like this:

>>> app.extensions['registry']['my.namespace'] = ListRegistry()
>>> len(app.extensions['registry'])
1
>>> app.extensions['registry']['my.namespace'].register("something")
>>> app.extensions['registry']['my.namespace'].register("something else")
>>> len(app.extensions['registry']['my.namespace'])
2
>>> for obj in app.extensions['registry']['my.namespace']:
...     print(obj)
something
something else
"""

from __future__ import absolute_import

from werkzeug.local import LocalProxy
from flask import current_app


class RegistryError(Exception):
    """
    Exception class raised for user errors (e.g. creating two registries in
    the same namespace)
    """
    pass


class Registry(object):
    """
    Flask extension

    Initialization of the extension:

    >>> from flask import Flask
    >>> from flask_registry import Registry, ListRegistry
    >>> app = Flask('myapp')
    >>> r = Registry(app=app)

    or alternatively using the factory pattern:

    >>> app = Flask('myapp')
    >>> r = Registry()
    >>> r.init_app(app)
    """
    def __init__(self, app=None):
        self._registry = dict()
        self.app = app
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        """
        Initialize a Flask application.

        Only one Registry per application is allowed.
        """
        # Follow the Flask guidelines on usage of app.extensions
        if not hasattr(app, 'extensions'):
            app.extensions = {}
        if 'registry' in app.extensions:
            raise RegistryError("Flask application already initialized")
        app.extensions['registry'] = self

    def __iter__(self):
        """
        Get iterator over registries.
        """
        return self._registry.__iter__()

    def __len__(self):
        """
        Get number of registries.
        """
        return self._registry.__len__()

    def __contains__(self, item):
        """
        Check if namespace exists in Flask application registry.

        :param item: Namespace
        """
        return self._registry.__contains__(item)

    def __getitem__(self, key):
        """
        Get a registry with a given namespace.

        :param key: Namespace
        """
        return self._registry[key]

    def __delitem__(self, key):
        """
        Remove a registry

        :param key: Namespace
        """
        obj = self._registry[key]
        del self._registry[key]
        obj.namespace = None

    def __setitem__(self, key, value):
        """
        Register a registry in the Flask application registry.

        :param key: Namespace
        :param value: Instance of RegistryBase or subclass
        """
        if key in self._registry:
            raise RegistryError("Namespace %s already taken." % key)
        self._registry[key] = value
        self._registry[key].namespace = key

    def items(self):
        """ Get list of (namespace, registry)-pairs. """
        return self._registry.items()


# pylint: disable=R0921
class RegistryBase(object):
    """
    Abstract base class for all registries.

    Each subclass must implement the ``register()`` method.
    Each subclass may implement the ``unregister()`` method.

    Once a registry is registered in the Flask application, the namespace
    under which it is available is injected into it self.

    Please see ``flask_registry.registries.core`` for simple examples of
    subclasses.
    """
    _namespace = None

    @property
    def namespace(self):
        """
        Namespace. Used only by the Flask extension to inject the namespace
        under which this instance is registered in the Flask application.
        Defaults to ``None`` if not registered in a Flask application.
        """
        return self._namespace

    @namespace.setter
    def namespace(self, value):
        """ Setter for namespace property. """
        if self._namespace and value is not None:
            raise RegistryError("Namespace cannot be changed.")
        self._namespace = value

    def register(self, *args, **kwargs):
        """
        Abstract method which MUST be overwritten by subclasses. A subclass
        does not need to take the same number of arguments as the abstract
        base class.
        """
        raise NotImplementedError()

    def unregister(self, *args, **kwargs):
        """
        Abstract method which MAY be overwritten by subclasses. A subclass
        does not need to take the same number of arguments as the abstract
        base class.
        """
        raise NotImplementedError()


class RegistryProxy(LocalProxy):
    """
    Lazy proxy object to a registry in the ``current_app``

    Allows you to define a registry in your local module without needing to
    initialize it first. Once accessed the first time, the registry will be
    initialized in the current_app, thus you must be working in either
    the Flask application context or request context.

    >>> from flask import Flask
    >>> app = Flask('myapp')
    >>> from flask_registry import Registry, RegistryProxy, RegistryBase
    >>> r = Registry(app=app)
    >>> proxy = RegistryProxy('myns', RegistryBase)
    >>> 'myns' in app.extensions['registry']
    False
    >>> with app.app_context():
    ...     print(proxy.namespace)
    ...
    myns
    >>> 'myns' in app.extensions['registry']
    True

    :param namespace: Namespace for registry
    :param registry_class: The registry class - i.e. a sublcass of
        ``RegistryBase``.
    :param args: Arguments passed to ``registry_class`` on initialization.
    :param kwargs: Keyword arguments passed to ``registry_class`` on
        initialization.
    """

    # pylint: disable=W0142, C0111, E1002
    def __init__(self, namespace, registry_class, *args, **kwargs):
        def _lookup():
            if not 'registry' in getattr(current_app, 'extensions', {}):
                raise RegistryError('Registry is not initialized.')
            if namespace not in current_app.extensions['registry']:
                # pylint: disable=W0142
                current_app.extensions['registry'][namespace] = \
                    registry_class(
                        *args, **kwargs
                    )
            return current_app.extensions['registry'][namespace]
        super(RegistryProxy, self).__init__(_lookup)


# Version information
from .version import __version__

#
# API of registries
#
from .registries.core import ListRegistry, DictRegistry, \
    ImportPathRegistry, ModuleRegistry
from .registries.modulediscovery import \
    ModuleDiscoveryRegistry, ModuleAutoDiscoveryRegistry
from .registries.pkgresources import EntryPointRegistry, \
    PkgResourcesDirDiscoveryRegistry
from .registries.appdiscovery import PackageRegistry, \
    ExtensionRegistry, ConfigurationRegistry, BlueprintAutoDiscoveryRegistry

__all__ = [
    'Registry', 'RegistryError', 'RegistryProxy', 'RegistryBase',
    'ListRegistry', 'DictRegistry', 'ImportPathRegistry', 'ModuleRegistry',
    'ModuleDiscoveryRegistry', 'ModuleAutoDiscoveryRegistry',
    'EntryPointRegistry', 'PkgResourcesDirDiscoveryRegistry',
    'PackageRegistry', 'ExtensionRegistry', 'ConfigurationRegistry',
    'BlueprintAutoDiscoveryRegistry', '__version__'
]
