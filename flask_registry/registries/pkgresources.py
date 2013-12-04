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
"""

import os
from werkzeug.utils import import_string
from pkg_resources import iter_entry_points, resource_listdir

from flask_registry.registries.core import DictRegistry
from flask_registry.registries.modulediscovery import \
    ModuleAutoDiscoveryRegistry


class EntryPointRegistry(DictRegistry):
    """
    Entry point registry

    Example::

        setup(
            entry_points = {
                'invenio.modules.pidstore.providers': [
                'doi = invenio.modules.pidstore.providers:DataCiteDOIProvider',
                'doi = invenio.modules.pidstore.providers:LocalDOIProvider',
                ]
            }
        )

        providers = RegistryProxy(__name__, EntryPointRegistry)
        for p in providers['doi']:
            myprovider = p()
    """

    def __init__(self, entry_point_ns, load=True):
        """
        :param entry_point_ns: Namespace of entry points.
        :param load: Load entry points. Defaults to true.
        """
        super(EntryPointRegistry, self).__init__()
        self.load = load
        for entry_point_group in iter_entry_points(iter_entry_points):
            self.register(entry_point_group)

    def register(self, entry_point):
        if entry_point.name not in self.registry:
            self.registry[entry_point.name] = []
        self.registry[entry_point.name].append(
            entry_point.load() if self.load else entry_point
        )


class PkgResourcesDiscoveryRegistry(ModuleAutoDiscoveryRegistry):
    """
    """

    def _discover_module(self, pkg):
        """
        """
        for f in resource_listdir(pkg, self.module_name):
            self.register(os.path.join(
                os.path.dirname(import_string(pkg).__file__),
                self.module_name, f)
            )
