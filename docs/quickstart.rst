.. _quickstart:

Quickstart
==========

This guide assumes you have successfully installed Flask-Registry and a working
understanding of Flask. If not, follow the installation steps and read about
Flask at http://flask.pocoo.org/docs/.


A Minimal Example
-----------------

A minimal Flask-Registry usage example looks like this. First create the
application and initialize the extension:

>>> from flask import Flask
>>> from flask_registry import Registry
>>> from flask_registry import ListRegistry
>>> app = Flask('myapp')
>>> r = Registry(app=app)

Then, we can create a simple ListRegistry that just keeps a list of objects:

>>> r['my_namespace'] = ListRegistry()
>>> r['my_namespace'].register("something")
>>> r['my_namespace'].register("something else")
>>> for obj in r['my_namespace']:
...     print(obj)
something
something else


Application Discovery Example
-----------------------------
Flask-Registry also has support for dynamically discovering Python modules,
resources, entry points and the like. All this can be put together in your
Flask application factory to create and easily extensible application.

Following is a small example how a Flask application can be assemble from
reusable packages that each provides configuration, extensions and blueprints:

.. literalinclude:: ../tests/example_app.py

Save this in a file named ``app.py`` next to the ``tests`` folder in the
Flask-Registry distribution and run it using your Python interpreter.
::

    $ python app.py
     * Running on http://127.0.0.1:5000/
    $ curl http://localhost:5000
    Hello from Flask-Registry

The blueprint is loaded from ``tests.views`` and only works if the extension
``tests.mockext`` and the configuration in ``tests.config`` has been loaded.

See :ref:`application-discovery` for full explanation on what is
happening in the example.