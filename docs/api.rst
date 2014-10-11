.. _api:

API
===

Core
----

.. automodule:: flask_fs
    :members:

.. autoclass:: flask_fs.Storage
    :members:


File types
----------

.. autodata:: flask_fs.TEXT
.. autodata:: flask_fs.DOCUMENTS
.. autodata:: flask_fs.IMAGES
.. autodata:: flask_fs.AUDIO
.. autodata:: flask_fs.DATA
.. autodata:: flask_fs.SCRIPTS
.. autodata:: flask_fs.ARCHIVES
.. autodata:: flask_fs.EXECUTABLES
.. autodata:: flask_fs.DEFAULTS
.. autodata:: flask_fs.ALL

.. autoclass:: flask_fs.All
.. autoclass:: flask_fs.AllExcept

.. .. automodule:: flask_fs.files
..     :members:


.. automodule:: flask_fs.images
    :members:


Backends
--------

.. automodule:: flask_fs.backends
    :members:


.. autoclass:: flask_fs.backends.local.LocalBackend
    :members:


.. autoclass:: flask_fs.backends.s3.S3Backend
    :members:


.. autoclass:: flask_fs.backends.swift.SwiftBackend
    :members:


.. autoclass:: flask_fs.backends.gridfs.GridFsBackend
    :members:


Mongo
-----

.. automodule:: flask_fs.mongo
    :members:



Errors
------

These are all errors used accross this extensions.

.. automodule:: flask_fs.errors
    :members:


Internals
---------

These are internal classes or helpers.
Most of the time you shouldn't have to deal directly with them.


.. autoclass:: flask_fs.storage.Config
