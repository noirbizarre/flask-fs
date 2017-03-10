Configuration
=============

Flask-FS expose both global and by storage settings.

Global configuration
--------------------

FS_SERVE
~~~~~~~~

**default**: ``DEBUG``

A boolean whether or not Flask-FS should serve files


FS_ROOT
~~~~~~~

**default**: ``{app.instance_path}/fs``

The global local storage root.
Each storage will have its own root as a subdirectory unless not local or overridden by configuration.

FS_PREFIX
~~~~~~~~~

**default**: ``None``

An optionnal URL path prefix for storages (ex: ``'/fs'``).


FS_URL
~~~~~~

**default**: ``None``

An optionnal URL on which the `FS_ROOT` is visible (ex: ``'https://static.mydomain.com/'``).


FS_BACKEND
~~~~~~~~~~

**default**: ``'local'``

The default backend used for storages.
Can be one of ``local``, ``s3``, ``gridfs`` or ``swift``

FS_IMAGES_OPTIMIZE
~~~~~~~~~~~~~~~~~~

**default**: ``False``

Whether or not image should be compressedd/optimized by default.


Storages configuration
----------------------

Each storage configuration can be overriden from the application configuration.
The configuration is loaded in the following order:

- ``FS_{BACKEND_NAME}_{KEY}`` (backend specific configuration)
- ``{STORAGE_NAME}_FS_{KEY}`` (specific configuration)
- ``FS_{KEY}`` (global configuration)
- default value

Given a storage declared like this:

.. code-block:: python

    import flask_fs as fs

    avatars = fs.Storage('avatars', fs.IMAGES)

You can override its root with the following configuration:

.. code-block:: python

    AVATARS_FS_ROOT = '/somewhere/on/the/filesystem'

Or you can set a base URL to all storages for a given backend:

.. code-block:: python

    FS_S3_URL = 'https://s3.somewhere.com/'
    FS_S3_REGION = 'us-east-1'
