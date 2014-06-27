===================================
 Flask-Registry v0.2.0 is released
===================================

Flask-Registry v0.2.0 was released on June 27, 2014.

About
-----

Flask-Registry is a Flask extension that allows frameworks to
dynamically assemble Flask application from reusable packages
consisting of blueprints, extensions, and configurations.

What's new
----------

- ListRegistry now fuly behaves as a list.
- DictRegistry now fuly behaves as a dict.
- Fixes issue with app in ModuleAutoDiscoveryRegistry.
- Excludes option for ImportPathRegistry.
- Fixes handling of missing package resource directory.
- Fixes issue in configuration loading.
- Allows removal of registries.
- Fixes ImportError and SyntaxError handling.
- Documentation and code coverage improvements.
- Differentiates between missing and broken modules.
- New BlueprintAutoDiscoveryRegistry.
- New SingletonRegistry.

Installation
------------

   $ pip install Flask-Registry

Documentation
-------------

   http://flask-registry.readthedocs.org/en/v0.2.0

Homepage
--------

   https://github.com/inveniosoftware/flask-registry

Good luck and thanks for choosing Flask-Registry.

| Invenio Development Team
|   Email: info@invenio-software.org
|   IRC: #invenio on irc.freenode.net
|   Twitter: http://twitter.com/inveniosoftware
|   GitHub: http://github.com/inveniosoftware
|   URL: http://invenio-software.org
