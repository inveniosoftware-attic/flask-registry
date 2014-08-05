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

    ./run-tests.sh
