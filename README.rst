================
 Flask-Registry
================

.. image:: https://travis-ci.org/inveniosoftware/flask-registry.png?branch=master
    :target: https://travis-ci.org/inveniosoftware/flask-registry
.. image:: https://coveralls.io/repos/inveniosoftware/flask-registry/badge.png?branch=master
    :target: https://coveralls.io/r/inveniosoftware/flask-registry
.. image:: https://pypip.in/v/Flask-Registry/badge.png
   :target: https://pypi.python.org/pypi/Flask-Registry/
.. image:: https://pypip.in/d/Flask-Registry/badge.png
   :target: https://pypi.python.org/pypi/Flask-Registry/

About
=====
Flask-Registry is a Flask extension that allows frameworks to
dynamically assemble Flask application from reusable packages
consisting of blueprints, extensions, and configurations.

Installation
============
Flask-Registry is on PyPI so all you need is: ::

    pip install Flask-Registry

Documentation
============
Documentation is readable at http://flask-registry.readthedocs.org or can be built using Sphinx: ::

    git submodule init
    git submodule update
    pip install Sphinx
    python setup.py build_sphinx

Testing
=======
Running the test suite is as simple as: ::

    python setup.py test

or, to also show code coverage: ::

    source run-tests.sh

License
=======
Copyright (C) 2013, 2014 CERN.

Flask-Registry is free software; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation; either version 2 of the License, or (at your option) any later version.

Flask-Registry is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with Flask-Registry; if not, write to the Free Software Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307, USA.

In applying this licence, CERN does not waive the privileges and immunities granted to it by virtue of its status as an Intergovernmental Organization or submit itself to any jurisdiction.
