def depends(*plugins):
    """Adds dependencies for a plugin.

    This decorator adds the given dependencies to the plugin. Multiple
    dependencies can be specified using multiple arguments or by using
    the decorator multiple times.

    :param plugins: plugin names
    """

    def wrapper(cls):
        cls.required_plugins |= frozenset(plugins)
        return cls

    return wrapper


def uses(*plugins):
    """Adds soft dependencies for a plugin.

    This decorator adds the given soft dependencies to the plugin.
    Multiple soft dependencies can be specified using multiple arguments
    or by using the decorator multiple times.

    Unlike dependencies, the specified plugins will be loaded before the
    plugin if possible, but if they are not available, the plugin will be
    loaded anyway.

    :param plugins: plugin names
    """

    def wrapper(cls):
        cls.used_plugins |= frozenset(plugins)
        return cls

    return wrapper


def resolve_dependencies(plugins):
    """Resolves dependencies between plugins and sorts them accordingly.

    This function guarantees that a plugin is never loaded before any
    plugin it depends on. If multiple plugins are ready to be loaded,
    the order in which they are loaded is undefined and should not be
    relied upon. If you want a certain order, add a (soft) dependency!

    :param plugins: dict mapping plugin names to plugin classes
    """
    plugins_deps = {name: (cls.required_plugins, cls.used_plugins) for name, cls in plugins.iteritems()}
    resolved_deps = set()
    while plugins_deps:
        # Get plugins with both hard and soft dependencies being met
        ready = {cls for cls, deps in plugins_deps.iteritems() if all(d <= resolved_deps for d in deps)}
        if not ready:
            # Otherwise check for plugins with all hard dependencies being met
            ready = {cls for cls, deps in plugins_deps.iteritems() if deps[0] <= resolved_deps}
        if not ready:
            # Either a circular dependency or a dependency that's not loaded
            raise Exception('Could not resolve dependencies between plugins')
        resolved_deps |= ready
        for name in ready:
            yield name, plugins[name]
            del plugins_deps[name]
