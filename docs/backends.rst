Backends
========

Local backend (``local``)
-------------------------

A local file system storage. This is the default storage backend.

Expect the following settings:

- ``ROOT``: The file system root


S3 backend (``s3``)
-------------------

An Amazon S3 Backend (compatible with any S3-like API)

Expect the following settings:

- ``ENDPOINT``: The S3 API endpoint
- ``REGION``: The region to work on.
- ``ACCESS_KEY``: The AWS credential access key
- ``SECRET_KEY``: The AWS credential secret key


GridFS backend (``gridfs``)
---------------------------

A Mongo GridFS backend

Expect the following settings:

- ``MONGO_URL``: The Mongo access URL
- ``MONGO_DB``: The database to store the file in.

Swift backend (``swift``)
-------------------------

An OpenStack Swift backend

Expect the following settings:

- ``AUTHURL``: The Swift Auth URL
- ``USER``: The Swift user in
- ``KEY``: The user API Key


Custom backends
---------------

Flask-FS allows you to defined your own backend
by extending the :class:`~flask_fs.backends.BaseBackend` class.

You need to register your backend using setuptools entrypoints in your ``setup.py``:

.. code-block:: python

    entry_points={
        'fs.backend': [
            'custom = my.custom.package:CustomBackend',
        ]
    },


Sample configuration
--------------------

Given these storages:

.. code-block:: python

    import flask_fs as fs

    files = fs.Storage('files')
    avatars = fs.Storage('avatars', fs.IMAGES)
    images = fs.Storage('images', fs.IMAGES)


Here an example configuration with local files storages and s3 images storage:

.. code-block:: python

    # Shared S3 configuration
    FS_S3_ENDPOINT = 'https://s3-eu-west-2.amazonaws.com'
    FS_S3_REGION = 'eu-west-2'
    FS_S3_ACCESS_KEY = 'ABCDEFGHIJKLMNOQRSTU'
    FS_S3_SECRET_KEY = 'abcdefghiklmnoqrstuvwxyz1234567890abcdef'
    FS_S3_URL = 'https://s3.somewhere.com/'

    # storage specific configuration
    AVATARS_FS_BACKEND = 's3'
    IMAGES_FS_BACKEND = 's3'
    FILES_FS_URL = 'https://images.somewhere.com/'
    FILES_FS_URL = 'https://files.somewhere.com/'


In this configuration, storages will have the following configuration:

- ``files``: ``local`` storage served on ``https://files.somewhere.com/``
- ``avatars``: ``s3`` storage served on ``https://s3.somewhere.com/avatars/``
- ``images``: ``s3`` storage served on ``https://images.somewhere.com/``
