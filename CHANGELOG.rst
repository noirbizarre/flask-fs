Changelog
=========

0.4.0 (2017-06-24)
------------------

- Added backend level configuration ``FS_{BACKEND_NAME}_{KEY}``
- Improved backend documentation
- Use setuptools entry points to register backends.
- Added `NONE` extensions specification
- Added `list_files` to `Storage` to list the current bucket files
- Image optimization preserve file type as much as possible
- Ensure images are not overwritted before rerendering

0.3.0 (2017-03-05)
------------------

- Switch to pytest
- ``ImageField`` optimization/compression.
  Resized images are now compressed.
  Default image can also be optimized on upload with ``FS_IMAGES_OPTIMIZE = True``
  or by specifying `optimize=True` as field parameter.
- ``ImageField`` has now the ability to rerender images with the ``rerender()`` method.

0.2.1 (2017-01-17)
------------------

- Expose Python 3 compatibility

0.2.0 (2016-10-11)
------------------

- Proper github publication
- Initial S3, GridFS and Swift backend implementations
- Python 3 fixes


0.1 (2015-04-07)
----------------

- Initial release
