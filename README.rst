========
Flask-FS
========

.. image:: https://travis-ci.org/noirbizarre/flask-fs.svg?branch=master
    :target: https://travis-ci.org/noirbizarre/flask-fs
    :alt: Build status
.. image:: https://coveralls.io/repos/noirbizarre/flask-fs/badge.svg?branch=master
    :target: https://coveralls.io/r/noirbizarre/flask-fs?branch=master
    :alt: Code coverage
.. image:: https://readthedocs.org/projects/flask-fs/badge/?version=latest
    :target: http://flask-fs.readthedocs.org/en/latest/
    :alt: Documentation status

Simple and easy file storages for Flask

Flask-RESTX is a community driven fork of `Flask-RESTPlus <https://github.com/noirbizarre/flask-restplus>`_.


Compatibility
=============

Flask-FS requires Python 2.7/3.4+ and Flask 0.10+.

Amazon S3 support requires Boto3.

GridFS support requires PyMongo 3+.

OpenStack Swift support requires python-swift-client.


Installation
============

You can install Flask-FS with pip:

.. code-block:: console

    $ pip install flask-fs
    # or
    $ pip install flask-fs[s3]  # For Amazon S3 backend support
    $ pip install flask-fs[swift]  # For OpenStack swift backend support
    $ pip install flask-fs[gridfs]  # For GridFS backend support
    $ pip install flask-fs[all]  # To include all dependencies for all backends


Quick start
===========

.. code-block:: python

    from flask import Flask
    import flask_fs as fs

    app = Flask(__name__)
    fs.init_app(app)

    images = fs.Storage('images')


    if __name__ == '__main__':
        app.run(debug=True)


Documentation
=============

The full documentation is hosted `on Read the Docs <http://flask-fs.readthedocs.org/en/latest/>`_
