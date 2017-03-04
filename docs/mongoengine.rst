Mongoengine support
===================

Flask-FS provides a thin mongoengine integration as :class:`field classes <mongoengine.base.fields.BaseField>`.

Both :class:`~flask_fs.mongo.FileField` and :class:`~flask_fs.mongo.ImageField`
provides a common interface:

.. code-block:: python

    images = fs.Storage('images', fs.IMAGES,
                        upload_to=lambda o: 'prefix',
                        basename=lambda o: 'basename')

    class MyDoc(Document):
        file = FileField(fs=files)


    doc = MyDoc()

    # Test file presence
    print(bool(doc.file))  # False
    # Get filename
    print(doc.file.filename)  # None
    # Get file URL
    print(doc.file.url)  # None
    # Print file URL
    print(str(doc.file))  # ''

    doc.file.save(io.Bytes(b'xxx'), 'test.file')

    print(bool(doc.file))  # True
    print(doc.file.filename)  # 'test.file'
    print(doc.file.url)  # 'http://myserver.com/files/prefix/test.file'
    print(str(doc.file))  # 'http://myserver.com/files/prefix/test.file'

    # Override Werkzeug Filestorage filename with basename
    f = FileStorage(io.Bytes(b'xxx'), 'test.file')
    doc.file.save(f)
    print(doc.file.filename)  # 'basename.file'


The :class:`~flask_fs.mongo.ImageField` provides some extra features.

On declaration:

 - an optionnal `max_size` attribute allows to limit image size
 - an optionnal `thumbnails` list of thumbnail sizes to be generated
 - an optionnal `optimize` booleanoverriding the ``FS_IMAGES_OPTIMIZE`` setting by field.

On instance:

 - the `original` property gives the unmodified image filename
 - the `best_url(size)` method match a thumbnail URL given a size
 - the `thumbnail(size)` method get a thumbnail filename given a registered size
 - the `save` method accept an optionnal `bbox` kwarg for to crop the thumbnails
 - the `rerender` method allows to force a new image rendering (taking in account new parameters)
 - the instance is callable as shortcut for `best_url()`

.. code-block:: python

    images = fs.Storage('images', fs.IMAGES)
    files = fs.Storage('files', fs.ALL)

    class MyDoc(Document):
        image = ImageField(fs=images,
                           max_size=150,
                           thumbnails=[100, 32])


    doc = MyDoc()

    with open(some_image, 'rb') as f:
        doc.file.save(f, 'test.png')

    print(doc.image.filename)  # 'test.png'
    print(doc.image.original)  # 'test-original.png'
    print(doc.image.thumbnail(100))  # 'test-100.png'
    print(doc.image.thumbnail(32))  # 'test-32.png'

    # Guess best image url for a given size
    assert doc.image.best_url().endswith(doc.image.filename)
    assert doc.image.best_url(200).endswith(doc.image.filename)
    assert doc.image.best_url(150).endswith(doc.image.filename)
    assert doc.image.best_url(100).endswith(doc.image.thumbnail(100))
    assert doc.image.best_url(90).endswith(doc.image.thumbnail(100))
    assert doc.image.best_url(30).endswith(doc.image.thumbnail(32))

    # Call as shortcut for best_url()
    assert doc.image().endswith(doc.image.filename)
    assert doc.image(200).endswith(doc.image.filename)
    assert doc.image(150).endswith(doc.image.filename)
    assert doc.image(100).endswith(doc.image.thumbnail(100))

    # Save an optionnal bbox for thumbnails cropping
    bbox = (10, 10, 100, 100)
    with open(some_image, 'rb') as f:
        doc.file.save(f, 'test.png', bbox=bbox)
