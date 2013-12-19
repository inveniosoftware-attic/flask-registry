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
Flask-Registry extension
"""

from __future__ import absolute_import

import sys
import six
from werkzeug.utils import find_modules, import_string
from werkzeug._compat import reraise
from flask import current_app, has_app_context

from flask_registry import RegistryProxy, RegistryBase, RegistryError
from .core import ModuleRegistry


class ModuleDiscoveryRegistry(ModuleRegistry):
    """
    Python module registry with discover capabilities.

    The registry will discover module with a given name from packages specified
    in a ``PackageRegistry``.

    Example::

        app.config['PACKAGES'] = ['invenio.modules.*', ...]
        app.config['PACKAGES_VIEWS_EXCLUDE'] = ['invenio.modules.oldstuff']

        app.extensions['registry']['packages'] = PackageRegistry()
        app.extensions['registry']['views'] = DiscoverRegistry('views')
        app.extensions['registry']['views'].discover(app)
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
        # Setup config variable prefix
        self.cfg_var_prefix = self.registry_namespace.upper()
        self.cfg_var_prefix = self.cfg_var_prefix.replace('.', '_')
        super(ModuleDiscoveryRegistry, self).__init__(with_setup=with_setup)

    def discover(self, app=None):
        """
        Discover modules

        Specific modules can be excluded with the configuration variable
        ``<NAMESPACE>_<MODULE_NAME>_EXCLUDE`` (e.g ``PACKAGES_VIEWS_EXCLUDE``).
        The namespace name is capitalized and have dots replace by underscore.

        :param module_name: Name of module to look for in packages
        :param registry_namespace: Name of registry containing the package
            registry. Defaults to ``packages``.
        :param with_setup: Call ``setup`` and ``teardown`` functions on module.
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
        """
        import_str = pkg + '.' + self.module_name

        try:
            module = import_string(import_str, self.silent)
            self.register(module)
        except ImportError as e:
            # If a module does not exists, it's not an error, however an
            # ImportError generated from importing an existing module is an
            # error.
            try:
                for found_module_name in find_modules(pkg):
                    if found_module_name == import_str:
                        reraise(
                            ImportError,
                            ImportError(*e.args),
                            sys.exc_info()[2]
                        )
            except ValueError:
                # pkg doesn't exist or is not a package
                pass


class ModuleAutoDiscoveryRegistry(ModuleDiscoveryRegistry):
    """
    """

    def __init__(self, module_name, app=None, *args, **kwargs):
        """
        """
        super(ModuleAutoDiscoveryRegistry, self).__init__(
            module_name, *args, **kwargs
        )
        self.app = app
        self.discover(app=app)
