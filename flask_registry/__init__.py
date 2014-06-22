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

"""Flask extension.

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
