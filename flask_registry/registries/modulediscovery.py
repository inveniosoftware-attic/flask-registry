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
Module Discovery
================
The module discovery registries provide discovery functionality useful
for searching a list of Python packages for a specific module name, and
afterwards registering the module. This is used to e.g. load and register
Flask blueprints by ``BlueprintAutoDiscoveryRegistry``.

Assume e.g. we want to discover the ``helpers`` module from the ``tests``
package. First we initialize the registry:

>>> from flask import Flask
>>> from flask_registry import Registry, ModuleDiscoveryRegistry
>>> from flask_registry import ImportPathRegistry
>>> app = Flask('myapp')
>>> r = Registry(app=app)

We then create the list of packages to search through using an
``ImportPathRegistry``:

>>> r['mypackages'] = ImportPathRegistry(initial=['tests'])

Then, initialize the ``ModuleDiscoveryRegistry`` and run the discovery:

>>> r['mydiscoveredmodules'] = ModuleDiscoveryRegistry(
...     'helpers', registry_namespace='mypackages')
>>> len(r['mydiscoveredmodules'])
0
>>> r['mydiscoveredmodules'].discover(app=app)
>>> len(r['mydiscoveredmodules'])
1

Lazy discovery
^^^^^^^^^^^^^^
Using ``RegistryProxy`` you may lazily discover modules. Above example using
lazy loading looks like this:

>>> from flask_registry import RegistryProxy
>>> app = Flask('myapp')
>>> r = Registry(app=app)
>>> pkg_proxy = RegistryProxy('mypackages', ImportPathRegistry,
...     initial=['tests'])
>>> mod_proxy = RegistryProxy('mydiscoveredmodules',
...     ModuleDiscoveryRegistry,
...     'helpers',
...     registry_namespace=pkg_proxy)
>>> 'mypackages' in r
False
>>> 'mydiscoveredmodules' in r
False
>>> with app.app_context():
...     mod_proxy.discover(app=app)
>>> 'mypackages' in r
True
>>> 'mydiscoveredmodules' in r
True
"""

from __future__ import absolute_import

import sys
import six
from werkzeug.utils import find_modules, import_string
from werkzeug._compat import reraise
from flask import current_app, has_app_context

from ..base import RegistryProxy, RegistryBase, RegistryError
from .core import ModuleRegistry


class ModuleDiscoveryRegistry(ModuleRegistry):
    """
    Specialized ``ModuleRegistry`` that will search a list of Python packages
    in an ``ImportPathRegistry`` or ``ModuleRegistry`` for a specific module
    name. By default the list of Python packages is read from the ``packages``
    registry namespace.

    Packages may be excluded during the discovery using a configuration
    variables constructed according to the following pattern::

        <NAMESPACE>_<MODULE_NAME>_EXCLUDE

    where ``<NAMESPACE>`` should be replaced by the ``registry_namepsace``, and
    ``<MOUDLE_NAME>`` should be replaced with ``module_name``. Example:
    ``PACKAGES_VIEWS_EXCLUDE``. All namespaces are capitalized and have dots
    replaced with underscores.

    Subclasses of ``ModuleDiscoveryRegistry`` may overwrite the internal
    ``_discover_module()`` method to provide specialized discovery (see e.g.
    ``BlueprintAutoDiscoveryRegistry``).

    :param module_name: Name of module to search for in packages.
    :param registry_namespace: The registry namespace of an
        ``ImportPathRegistry`` or ``ModuleRegistry`` with a list Python
        packages to search for ``module_name`` modules in. Alternatively to
        a registry namespace an instance of a ``RegistryProxy`` or ``Registry``
        may also be used. Defaults to ``packages``.
    :param with_setup: Call setup and teardown function on discovered modules.
        Defaults to ``False`` (see ``ModuleRegistry``).
    :param silent: if set to True import errors are ignored. Defaults to
        ``False``.
    """

    def __init__(self, module_name, registry_namespace=None, with_setup=False,
                 silent=False):
        """
        :param module_name: Name of module to look for in packages
        :param registry_namespace: Name of registry containing the package
            registry. Defaults to ``packages''.
        :param with_setup: Call ``setup`` and ``teardown`` functions on module.
        """
        self.module_name = module_name
        self.silent = silent
        if registry_namespace is not None and \
                isinstance(registry_namespace, (RegistryProxy, RegistryBase)):
            self.registry_namespace = registry_namespace.namespace
        else:
            self.registry_namespace = registry_namespace or 'packages'
        assert self.registry_namespace is not None
        # Setup config variable prefix
        self.cfg_var_prefix = self.registry_namespace.upper()
        self.cfg_var_prefix = self.cfg_var_prefix.replace('.', '_')
        super(ModuleDiscoveryRegistry, self).__init__(with_setup=with_setup)

    def discover(self, app=None):
        """
        Perform module discovery, by iterating over the list of Python packages
        in the order they are specified.

        :param app: Flask application object from where the list of Python
            packages is loaded (from the ``registry_namespace``). Defaults to
            ``current_app`` if not specified (thus requires you are working
            in the Flask application context).
        """
        if app is None and has_app_context():
            app = current_app
        if app is None:
            raise RegistryError("You must provide a Flask application.")

        blacklist = app.config.get(
            '%s_%s_EXCLUDE' % (self.cfg_var_prefix, self.module_name.upper()),
            []
        )

        for pkg in app.extensions['registry'][self.registry_namespace]:
            if not isinstance(pkg, six.string_types):
                pkg = pkg.__name__

            if pkg in blacklist:
                continue

            self._discover_module(pkg)

    def _discover_module(self, pkg):
        """
        Method to discover a single module. May be overwritten by subclasses.
        """
        import_str = pkg + '.' + self.module_name

        try:
            module = import_string(import_str, silent=self.silent)
            if module is not None:
                self.register(module)
        except ImportError as e:  # pylint: disable=C0103
            self._handle_importerror(e, pkg, import_str)
        except SyntaxError as e:
            self._handle_syntaxerror(e, pkg, import_str)

    def _handle_importerror(self, exception, pkg, import_str):
        """
        Properly handle an import error

        If a module does not exists, it's not an error, however an
        ImportError generated from importing an existing module is an
        error.
        """
        try:
            for found_module_name in find_modules(pkg):
                if found_module_name == import_str:
                    reraise(
                        ImportError,
                        ImportError(*exception.args),
                        sys.exc_info()[2]
                    )
        except ValueError:
            # pkg doesn't exist or is not a package
            pass

    def _handle_syntaxerror(self, exception, pkg, import_str):
        """
        Properly handle an syntax error.

        Pass through the error unless silent is set to True.
        """
        if not self.silent:
            reraise(
                SyntaxError,
                SyntaxError(*exception.args),
                sys.exc_info()[2]
            )


class ModuleAutoDiscoveryRegistry(ModuleDiscoveryRegistry):
    """
    Specialized ``ModuleDiscoveryRegistry`` that will discover modules
    immediately on initialization.

    :param module_name: Name of module to search for in packages.
    :param app: Flask application object
    :param registry_namespace: The registry namespace of an
        ``ImportPathRegistry`` or ``ModuleRegistry`` with a list Python
        packages to search for ``module_name`` modules in. Alternatively to
        a registry namespace an instance of a ``RegistryProxy`` or ``Registry``
        may also be used. Defaults to ``packages``.
    :param with_setup: Call setup and teardown function on discovered modules.
        Defaults to ``False`` (see ``ModuleRegistry``).
    :param silent: if set to True import errors are ignored. Defaults to
        ``False``.
    """

    # pylint: disable=R0913
    def __init__(self, module_name, app=None, registry_namespace=None,
                 with_setup=False, silent=False):
        super(ModuleAutoDiscoveryRegistry, self).__init__(
            module_name, with_setup=with_setup, silent=silent,
            registry_namespace=registry_namespace
        )
        if app is None and has_app_context():
            app = current_app
        self.app = app
        self.discover(app=app)
