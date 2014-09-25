# -*- coding: utf-8 -*-
##
## This file is part of Flask-Registry
## Copyright (C) 2014 CERN.
##
## Flask-Registry is free software; you can redistribute it and/or
## modify it under the terms of the Revised BSD License; see LICENSE
## file for more details.

"""Utility functions."""

from six import iteritems


def depends(*plugins):
    """Add dependencies for a plugin.

    This decorator adds the given dependencies to the plugin. Multiple
    dependencies can be specified using multiple arguments or by using the
    decorator multiple times.

    :param plugins: plugin names
    """

    def wrapper(cls):
        if not hasattr(cls, '__required_plugins'):
            cls.__required_plugins = set(plugins)
        else:
            cls.__required_plugins |= frozenset(plugins)
        return cls

    return wrapper


def uses(*plugins):
    """Add soft dependencies for a plugin.

    This decorator adds the given soft dependencies to the plugin.  Multiple
    soft dependencies can be specified using multiple arguments or by using the
    decorator multiple times.

    Unlike dependencies, the specified plugins will be loaded before the plugin
    if possible, but if they are not available, the plugin will be loaded
    anyway.

    :param plugins: plugin names
    """

    def wrapper(cls):
        if not hasattr(cls, '__used_plugins'):
            cls.__used_plugins = set(plugins)
        else:
            cls.__used_plugins |= frozenset(plugins)
        return cls

    return wrapper


def resolve_dependencies(plugins):
    """Resolve dependencies between plugins and sorts them accordingly.

    This function guarantees that a plugin is never loaded before any plugin it
    depends on. If multiple plugins are ready to be loaded, the order in which
    they are loaded is undefined and should not be relied upon. If you want a
    certain order, add a (soft) dependency!

    :param plugins: dict mapping plugin names to plugin classes
    """
    def _extract_metadata(cls):
        return getattr(cls, '__required_plugins', set()), \
            getattr(cls, '__used_plugins', set())

    plugins_dependencies = dict([
        (name, _extract_metadata(cls)) for name, cls in iteritems(plugins)
    ])
    resolved_dependencies = set()
    while plugins_dependencies:
        # Get plugins with both hard and soft dependencies being met
        ready = set(cls for cls, deps in iteritems(plugins_dependencies)
                    if all(d <= resolved_dependencies for d in deps))
        if not ready:
            # Otherwise check for plugins with all hard dependencies being met
            ready = set(cls for cls, deps in iteritems(plugins_dependencies)
                        if deps[0] <= resolved_dependencies)
        if not len(ready):
            # Either a circular dependency or a dependency that's not loaded
            raise Exception('Could not resolve dependencies between plugins')
            # FIXME display what is left in plugins_dependencies
        resolved_dependencies |= ready
        for name in ready:
            yield name, plugins[name]
            del plugins_dependencies[name]
