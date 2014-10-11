.. _installation:

Installation
============

Install Flask-FS with ``pip``:

.. code-block:: console

    pip install flask-fs

Each backend has its own dependencies:

.. code-block:: console

    $ pip install flask-fs[s3]  # For Amazon S3 backend support
    $ pip install flask-fs[swift]  # For OpenStack swift backend support
    $ pip install flask-fs[gridfs]  # For GridFS backend support
    $ pip install flask-fs[all]  # To include all dependencies for all backends


The development version can be downloaded from
`GitHub <https://github.com/noirbizarre/flask-fs>`_.

.. code-block:: console

    git clone https://github.com/noirbizarre/flask-fs.git
    cd flask-fs
    pip install -e .[dev]


Flask-FS requires Python version 2.6, 2.7, 3.3, 3.4 or 3.5.
It's also working with PyPy and PyPy3.
