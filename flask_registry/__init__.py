# -*- coding: utf-8 -*-
##
## This file is part of Flask-Registry
## Copyright (C) 2013, 2014 CERN.
##
## Flask-Registry is free software; you can redistribute it and/or
## modify it under the terms of the Revised BSD License; see LICENSE
## file for more details.

"""
Flask extension to dynamically assemble your Flask application from packages.

Flask-Registry is initialized like this:

.. code-block:: pycon

    >>> from flask import Flask
    >>> from flask_registry import Registry, ListRegistry
    >>> app = Flask('myapp')
    >>> r = Registry(app=app)

A simple usage example of ``ListRegistry`` looks like this:

.. code-block:: pycon

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

from .base import Registry, RegistryError, RegistryProxy, RegistryBase
from .registries.core import (ListRegistry, DictRegistry,
                              ImportPathRegistry, ModuleRegistry,
                              SingletonRegistry)
from .registries.modulediscovery import (ModuleDiscoveryRegistry,
                                         ModuleAutoDiscoveryRegistry)
from .registries.pkgresources import (EntryPointRegistry,
                                      PkgResourcesDirDiscoveryRegistry)
from .registries.appdiscovery import (PackageRegistry,
                                      ExtensionRegistry,
                                      ConfigurationRegistry,
                                      BlueprintAutoDiscoveryRegistry)

from .version import __version__

__all__ = (
    'Registry', 'RegistryError', 'RegistryProxy', 'RegistryBase',
    'ListRegistry', 'DictRegistry', 'ImportPathRegistry', 'ModuleRegistry',
    'ModuleDiscoveryRegistry', 'ModuleAutoDiscoveryRegistry',
    'EntryPointRegistry', 'PkgResourcesDirDiscoveryRegistry',
    'PackageRegistry', 'ExtensionRegistry', 'ConfigurationRegistry',
    'BlueprintAutoDiscoveryRegistry', 'SingletonRegistry', '__version__'
)
