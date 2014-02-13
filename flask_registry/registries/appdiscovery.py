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
.. _application-discovery:

Application Discovery
=====================

The application discovery registries provide discovery functionality useful
for dynamically constructing Flask applications based on configuration
variables. This allows a developer to package config, blueprints and extensions
into isolated and reusable packages which a framework can dynamically install
into a Flask application.

Such a package (named ``tests``) could look like:

 * ``tests.views`` -- contains blueprints which should be registered on the
   application object.
 * ``tests.mockext`` -- contains a ``setup_app()`` method which be used to
   install any Flask extensions on the application object.
 * ``tests.config`` -- contains configuration variables specific for this
   module.

Following is a simplified example of a Flask application factory, that will
load config, extensions and blueprints:

>>> from flask import Flask, Blueprint
>>> from flask_registry import Registry, PackageRegistry
>>> from flask_registry import ExtensionRegistry
>>> from flask_registry import ConfigurationRegistry
>>> from flask_registry import BlueprintAutoDiscoveryRegistry
>>> class Config(object):
...     PACKAGES = ['tests']
...     EXTENSIONS = ['tests.mockext']
...     USER_CFG = True
>>> def create_app(config):
...     app = Flask('myapp')
...     app.config.from_object(config)
...     r = Registry(app=app)
...     r['packages'] = PackageRegistry(app)
...     r['extensions'] = ExtensionRegistry(app)
...     r['config'] = ConfigurationRegistry(app)
...     r['blueprints'] = BlueprintAutoDiscoveryRegistry(app=app)
...     return app
>>> config = Config()
>>> app = create_app(config)

Packages
^^^^^^^^
The config variable ``PACKAGES`` specifies the list of Python packages, which
``ConfigurationRegistry`` and ``BlueprintAutoDiscoveryRegistry``
will search for ``config.py`` and ``views.py`` modules inside.

>>> for pkg in app.extensions['registry']['packages']:
...     print(pkg)
tests

Extensions
^^^^^^^^^^
The config variable ``EXTENSIONS`` specifies the list of Python packages,
which the ``ExtensionRegistry`` will load and call ``setup_app(app)`` on,
to dynamically initialize Flask extensions.

>>> for pkg in app.extensions['registry']['extensions']:
...     print(pkg)
tests.mockext

Configuration
^^^^^^^^^^^^^
The ``ConfigurationRegistry`` will merge any package defined config, with the
application config without overwriting already set variables in the application
config:

>>> config.USER_CFG
True
>>> import tests.config
>>> tests.config.USER_CFG
False
>>> app.config['USER_CFG']
True

Blueprints
^^^^^^^^^^
The ``BlueprintAutoDiscoveryRegistry`` will search for blueprints defined
inside a ``views`` module in each package defined in ``PACAKGES``. It will
also register the discovered blueprints on the Flask application.
Each ``views`` module should define either a single blueprint in the variable
``blueprint`` and/or multiple blueprints in the variable ``blueprints``:

>>> from tests import views
>>> isinstance(views.blueprint, Blueprint)
True
>>> len(views.blueprints)
2
>>> for k in sorted(app.blueprints.keys()):
...     print(k)
test
test1
test2
"""

from __future__ import absolute_import

from werkzeug.utils import import_string
from flask import Blueprint, Config

from .core import ListRegistry, ImportPathRegistry
from .modulediscovery import ModuleDiscoveryRegistry, \
    ModuleAutoDiscoveryRegistry


# pylint: disable=R0921
class ExtensionRegistry(ListRegistry):
    """
    Flask extensions registry (Specialized ``ListRegistry``). Loads all
    extensions specified by ``EXTENSIONS`` configuration variable.
    The registry will look for a ``setup_app`` function in the extension and
    call it if it exists.

    Example configuration::

        EXTENSIONS = [
            'invenio.ext.debug_toolbar',
            'invenio.ext.menu:MenuAlchemy',
        ]

    :param app: Flask application to get configuration from.
    """
    def __init__(self, app):
        super(ExtensionRegistry, self).__init__()
        for ext_name in app.config.get('EXTENSIONS', []):
            self.register(app, ext_name)

    def register(self, app, ext_name):  # pylint: disable=W0221
        """
        Register a Flask extensions and call ``setup_app()`` on it.

        :param app: Flask application object
        :param ext_name: An import path (e.g. a package, module, object) which
            when loaded has an method ``setup_app()``.
        """
        ext = import_string(ext_name)
        super(ExtensionRegistry, self).register(ext_name)
        ext = getattr(ext, 'setup_app', ext)
        ext(app)

    def unregister(self):  # pylint: disable=W0221
        """
        It is not possible to unregister configuration.
        """
        raise NotImplementedError()


# pylint: disable=W0223
class PackageRegistry(ImportPathRegistry):
    """
    Specialized ``ImportPathRegistry`` that takes the initial list of import
    paths from the ``PACKAGES`` configuration variable in the application.

    :param app: The Flask application object from which includes a ``PACAKGES``
        variable in it's configuration.
    """
    def __init__(self, app):
        super(PackageRegistry, self).__init__(
            initial=app.config.get('PACKAGES', []),
            exclude=app.config.get('PACKAGES_EXCLUDE', [])
        )


# pylint: disable=R0921
class ConfigurationRegistry(ModuleDiscoveryRegistry):
    """
    Specialized ``ModuleDiscoveryRegistry`` that search for ``config`` modules
    in a list of Python packages and merge them into the Flask application
    config without overwriting already set variables.

    :param app: A Flask application
    :param registry_namespace: The registry namespace of an
        ``ImportPathRegistry`` with a list Python packages to search for
        ``config`` modules in. Defaults to ``packages``.
    """
    def __init__(self, app, registry_namespace=None):
        super(ConfigurationRegistry, self).__init__(
            'config',
            registry_namespace=registry_namespace,
            with_setup=False,
        )

        # Create a new configuration module to collect configuration in.
        self.new_config = Config(app.config.root_path)

        # Auto-discover configuration in packages
        self.discover(app)

        # Overwrite default configuration with user specified configuration
        self.new_config.update(app.config)
        app.config.update(self.new_config)

    def register(self, new_object):
        """
        Register a new ``config`` module.

        :param new_object: The configuration module.
            ``app.config.from_object()`` will be called on it.
        """
        self.new_config.from_object(new_object)
        super(ConfigurationRegistry, self).register(new_object)

    def unregister(self, *args, **kwargs):
        """
        It is not possible to unregister configuration.
        """
        raise NotImplementedError()


class BlueprintAutoDiscoveryRegistry(ModuleAutoDiscoveryRegistry):
    """
    Specialized ``ModuleAutoDiscoveryRegistry`` that search for ``views``
    modules in a list of Python packages and register blueprints found inside
    them.

    Blueprints are loaded by searching for a variable ``blueprints``
    (list of Blueprint instances) or  ``blueprint`` (a
    Blueprint instance). If found, the blueprint will be registered on the
    Flask application.

    A blueprint URL prefix can be overwritten using the
    ``BLUEPRINTS_URL_PREFIXES`` variable in the application configuration::

        BLUEPRINTS_URL_PREFIXES = {
            '<blueprint name>': '<new url prefix>',
            # ...
        }
    """
    def __init__(self, module_name=None, app=None, with_setup=False,
                 silent=False):
        super(BlueprintAutoDiscoveryRegistry, self).__init__(
            module_name or 'views', app=app, with_setup=with_setup,
            silent=silent
        )

    def _discover_module(self, pkg):
        import_str = pkg + '.' + self.module_name

        try:
            module = import_string(import_str, silent=self.silent)
        except ImportError as e:  # pylint: disable=C0103
            self._handle_importerror(e, pkg, import_str)
            return
        except SyntaxError as e:
            self._handle_syntaxerror(e, pkg, import_str)
            return

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
