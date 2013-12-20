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

from __future__ import absolute_import

from werkzeug.utils import import_string
from .core import ListRegistry, ImportPathRegistry
from .modulediscovery import ModuleDiscoveryRegistry, \
    ModuleAutoDiscoveryRegistry


# pylint: disable=R0921
class ExtensionRegistry(ListRegistry):
    """
    Flask extensions registry

    Loads all extensions specified by ``EXTENSIONS`` configuration variable.
    The registry will look for a ``setup_app`` function in the extension and
    call it if it exists.

    Example::

        EXTENSIONS = [
            'invenio.ext.debug_toolbar',
            'invenio.ext.menu:MenuAlchemy',
        ]
    """
    def __init__(self, app):
        """
        :param app: Flask application to get configuration from.
        """
        super(ExtensionRegistry, self).__init__()
        for ext_name in app.config.get('EXTENSIONS', []):
            self.register(app, ext_name)

    def register(self, app, ext_name):  # pylint: disable=W0221
        ext = import_string(ext_name)
        super(ExtensionRegistry, self).register(ext_name)
        ext = getattr(ext, 'setup_app', ext)
        ext(app)

    def unregister(self):  # pylint: disable=W0221
        raise NotImplementedError()


# pylint: disable=W0223
class PackageRegistry(ImportPathRegistry):
    """
    Specialized import path registry that takes the initial list of import
    paths from ``PACKAGES`` configuration variable.

    Example::

        app.extensions['registry']['packages'] = PackageRegistry()

        for impstr in app.extensions['registry']['packages']:
            print impstr
    """
    def __init__(self, app):
        super(PackageRegistry, self).__init__(
            initial=app.config.get('PACKAGES', [])
        )


# pylint: disable=R0921
class ConfigurationRegistry(ModuleDiscoveryRegistry):
    """
    Specialized import path registry that takes the initial list of import
    paths from ``PACKAGES`` configuration variable.

    Example::

        app.extensions['registry']['packages'] = PackageRegistry()
        ConfigurationRegistry(app)
    """
    def __init__(self, app, registry_namespace=None):
        super(ConfigurationRegistry, self).__init__(
            'config',
            registry_namespace=registry_namespace,
            with_setup=False,
        )

        # Create a new configuration module to collect configuration in.
        from flask import Config
        self.new_config = Config(app.config.root_path)

        # Auto-discover configuration in packages
        self.discover(app)

        # Overwrite default configuration with user specified configuration
        self.new_config.update(app.config)
        app.config = self.new_config

    def register(self, new_object):
        self.new_config.from_object(new_object)
        super(ConfigurationRegistry, self).register(new_object)

    def unregister(self, *args, **kwargs):
        raise NotImplementedError()


from flask import Blueprint


class BlueprintAutoDiscoveryRegistry(ModuleAutoDiscoveryRegistry):
    """
    Discover Flask Blueprints from packages defined in another registry.

    Defaults to loading ``views`` from each package, and looking for a variable
    ``blueprints`` (list of Blueprint instances) or  ``blueprint`` (a
    Blueprint instance). If found, the blueprint will be registered on the
    Flask application.

    A blueprint URL prefix can be overwritten using the
    ``BLUEPRINTS_URL_PREFIXES`` variable in the application configuration::

        BLUEPRINTS_URL_PREFIXES = {
            '<blueprint name>': '<new url prefix>',
            # ...
        }
    """
    def __init__(self, module_name=None, app=None, *args, **kwargs):
        super(BlueprintAutoDiscoveryRegistry, self).__init__(
            module_name or 'views', app=app, *args, **kwargs
        )

    def _discover_module(self, pkg):
        import_str = pkg + '.' + self.module_name

        module = import_string(import_str)

        candidates = []
        if 'blueprints' in dir(module):
            candidates += getattr(module, 'blueprints')

        if 'blueprint' in dir(module):
            candidates.append(getattr(module, 'blueprint'))

        for candidate in candidates:
            if isinstance(candidate, Blueprint):
                # Register on app
                self.app.register_blueprint(
                    candidate,
                    url_prefix=self.app.config.get(
                        'BLUEPRINTS_URL_PREFIXES', {}
                    ).get(candidate.name)
                )
                # Register in registry
                self.register(candidate)
