========
Flask-FS
========

.. image:: https://secure.travis-ci.org/noirbizarre/flask-fs.svg
    :target: https://travis-ci.org/noirbizarre/flask-fs
    :alt: Build status
.. image:: https://coveralls.io/repos/noirbizarre/flask-fs/badge.svg?branch=master
    :target: https://coveralls.io/r/noirbizarre/flask-fs?branch=master
    :alt: Code coverage
.. image:: https://requires.io/github/noirbizarre/flask-fs/requirements.svg?branch=master
    :target: https://requires.io/github/noirbizarre/flask-fs/requirements/?branch=master
    :alt: Requirements Status
.. image:: https://readthedocs.org/projects/flask-fs/badge/?version=0.2.1
    :target: http://flask-fs.readthedocs.org/en/latest/
    :alt: Documentation status

Simple and easy file storages for Flask


Compatibility
=============

Flask-FS requires Python 2.7+ and Flask 0.10+.

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
