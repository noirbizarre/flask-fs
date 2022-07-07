# Flask-fs

Simple and easy file storages for Flask

Flask-RESTX is a community driven fork of [Flask-FS](https://github.com/noirbizarre/flask-fs)


## Compatibility

Flask-FS requires 3.9+ and Flask 2+.

Amazon S3 support requires Boto3.


## Installation

You can install Flask-FS with pip:

.. code-block:: console

    $ pip install flask-fs
    # or
    $ pip install flask-fs[s3]  # For Amazon S3 backend support


## Quick start

.. code-block:: python

    from flask import Flask
    import flask_fs as fs

    app = Flask(__name__)
    fs.init_app(app)

    images = fs.Storage('images')


    if __name__ == '__main__':
        app.run(debug=True)


## Documentation

The full documentation is hosted [on Read the Docs](http://flask-fs.readthedocs.org/en/latest/)
