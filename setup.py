# -*- coding: utf-8 -*-
#
# This file is part of Flask-Registry
# Copyright (C) 2013, 2014, 2016 CERN.
#
# Flask-Registry is free software; you can redistribute it and/or
# modify it under the terms of the Revised BSD License; see LICENSE
# file for more details.

import os
import re
import sys

from setuptools import setup

# Get the version string.  Cannot be done with import!
with open(os.path.join('flask_registry', 'version.py'), 'rt') as f:
    version = re.search(
        '__version__\s*=\s*"(?P<version>.*)"\n',
        f.read()
    ).group('version')

tests_require = [
    'check-manifest>=0.25',
    'coverage>=4.0',
    'isort>=4.2.2',
    'mock>=1.3.0',
    'pydocstyle>=1.0.0',
    'pytest-cache>=1.0',
    'pytest-cov>=1.8.0',
    'pytest-pep8>=1.0.6',
    'pytest>=2.8.0',
]

extras_require = {
    'docs': [
        'Sphinx>=1.4.2',
    ],
    'tests': tests_require,
}

extras_require['all'] = []
for reqs in extras_require.values():
    extras_require['all'].extend(reqs)

setup(
    name='Flask-Registry',
    version=version,
    url='http://github.com/inveniosoftware/flask-registry/',
    license='BSD',
    author='Invenio collaboration',
    author_email='info@inveniosoftware.org',
    description='Flask-Registry is an extension for Flask that allow '
        'frameworks to dynamically assemble your Flask application from '
        'reusable packages consisting of blueprints, extensions, and '
        'configurations.',
    long_description=open('README.rst').read(),
    packages=['flask_registry', 'flask_registry.registries'],
    zip_safe=False,
    include_package_data=True,
    platforms='any',
    extras_require=extras_require,
    install_requires=[
        'Flask',
        'six',
    ],
    setup_requires=[
        'pytest-runner>=2.6.2',
    ],
    tests_require=tests_require,
    classifiers=[
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Framework :: Flask',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Development Status :: 5 - Production/Stable',
    ],
    entry_points={
        'flask_registry.test_entry': [
            'testcase = flask_registry:RegistryBase',
            'registry = flask_registry:Registry',
            'proxy = flask_registry:RegistryProxy',
        ]
    },
)
