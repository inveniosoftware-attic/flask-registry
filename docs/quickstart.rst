.. _quickstart:

Quickstart
==========

This guide assumes you have successfully installed Flask-Registry and a working
understanding of Flask. If not, follow the Flask Quickstart guide.


A Minimal Example
-----------------

A minimal Flask-Registry suage looks like this: ::

    from flask import Flask
    from flask.ext import registry

    app = Flask(__name__)

    # Initialize Flask-Registry
    registry.Registry(app=app)

    # Create a the registry namespace 'myfirstregistry' as a ListRegistry
    app.extensions['registry']['myfirstregistry'] = registry.ListRegistry()

    # Use the newly create ListRegistry
    app.extensions['registry']['myfirstregistry'].register('Something')
    app.extensions['registry']['myfirstregistry'].register('Something else')

    if __name__ == '__main__':
        app.run(debug=True)


Save this as app.py and run it using your Python interpreter. ::

    $ python app.py
     * Running on http://127.0.0.1:5000/

