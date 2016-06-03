Quick Start
===========

.. currentmodule:: flask_fs

Initialization
--------------

Flask-FS need to be initialized with an application:

.. code-block:: python

    from flask import Flask
    import flask_fs as fs

    app = Flask(__name__)
    fs.init_app(app)


Storages declaration
--------------------

You need to declare some storages before being able to read or write files.

.. code-block:: python

    import flask_fs as fs

    images = fs.Storage('images')
    uploads = fs.Storage('uploads')


You can limit the allowed file types.

.. code-block:: python

    import flask_fs as fs

    images = fs.Storage('images', fs.IMAGES)
    custom = fs.Storage('custom', ('bat', 'sh'))

You can also specify allowed extensions by exclusion:

.. code-block:: python

    import flask_fs as fs

    WITHOUT_SCRIPTS = fs.AllExcept(fs.SCRIPTS + fs.EXECUTABLES)
    store = fs.Storage('store', WITHOUT_SCRIPTS)


By default files in storage are not overwritables.
You can allow overwriting with the `overwrite` parameter in  :class:`Storage` class.


.. code-block:: python

    import flask_fs as fs

    store = fs.Storage('store', overwrite=True)


Storages operations
-------------------

Storages provides an abstraction layer for common operations.
All filenames are root relative to the storage.

.. code-block:: Python

    store = fs.Storage('store')

    # Writing
    store.write('my.file', 'content')

    # Reading
    content = store.read('my.file')

    # Working with file object
    with store.open('my.file', 'wb') as f:
        # do something

    # Testing file presence
    if store.exists('my.file'):
        # do something

    if 'my.file' in store:
        # do something

    # Deleting file
    store.delete('my.file')


See :class:`Storage` class definition.
