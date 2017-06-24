# -*- coding: utf-8 -*-
from __future__ import unicode_literals, division

import filecmp
import os

from PIL import Image

import flask_fs as fs
from flask_fs.mongo import FileField, ImageField
from flask_mongoengine import MongoEngine

import pytest


db = MongoEngine()


class MongoEngineTestCase(object):
    @pytest.fixture(autouse=True)
    def storage(self, app, tmpdir):
        app.instance_path = str(tmpdir)
        storage = fs.Storage('test', fs.ALL)
        fs.init_app(app, storage)
        db.init_app(app)
        yield storage
        with app.test_request_context():
            db_name = app.config['MONGODB_DB']
            try:
                db.connection.client.drop_database(db_name)
            except TypeError:
                db.connection.drop_database(db_name)


class FileFieldTest(MongoEngineTestCase):
    def test_default_validate(self, storage):
        class Tester(db.Document):
            file = FileField(fs=storage)

        tester = Tester()

        assert tester.validate() is None

        assert not tester.file
        assert str(tester.file) == ''
        assert tester.to_mongo() == {}
        assert tester.file.filename is None

    def test_set_filename(self, storage):
        class Tester(db.Document):
            file = FileField(fs=storage)

        filename = 'file.test'

        tester = Tester()
        tester.file = filename

        assert tester.validate() is None

        assert tester.file
        assert tester.file.filename == filename
        assert tester.to_mongo() == {
            'file': {
                'filename': filename,
            }
        }

        tester.save()
        tester.reload()
        assert tester.file.filename == filename

    def test_save_from_file(self, storage, binfile):
        class Tester(db.Document):
            file = FileField(fs=storage)

        filename = 'test.png'

        tester = Tester()
        f = open(binfile, 'rb')
        tester.file.save(f, filename)
        tester.validate()

        assert tester.file
        assert str(tester.file) == tester.file.url

        assert tester.file.filename == filename

        assert tester.to_mongo() == {
            'file': {
                'filename': filename,
            }
        }

        assert filename in storage

        assert filecmp.cmp(storage.path(filename), binfile)

        tester.save()
        tester = Tester.objects.get(id=tester.id)
        assert tester.file.filename == filename

    def test_save_from_filestorage(self, storage, utils):
        class Tester(db.Document):
            file = FileField(fs=storage)

        filename = 'test.txt'

        tester = Tester()
        tester.file.save(utils.filestorage(filename, 'this is a stest'))
        tester.validate()

        assert tester.file
        assert str(tester.file) == tester.file.url

        assert tester.file.filename == filename

        assert tester.to_mongo() == {
            'file': {
                'filename': filename,
            }
        }

        assert filename in storage

        tester.save()
        tester = Tester.objects.get(id=tester.id)
        assert tester.file.filename == filename

    def test_save_with_upload_to(self, storage, utils):
        upload_to = 'prefix'

        class Tester(db.Document):
            file = FileField(fs=storage, upload_to=upload_to)

        filename = 'test.txt'

        tester = Tester()
        tester.file.save(utils.filestorage(filename, 'this is a stest'))
        tester.validate()

        expected_filename = '/'.join([upload_to, filename])
        assert tester.file
        assert tester.file.filename == expected_filename
        assert expected_filename in storage
        assert tester.to_mongo() == {
            'file': {
                'filename': expected_filename,
            }
        }

        tester.save()
        tester = Tester.objects.get(id=tester.id)
        assert tester.file.filename == expected_filename

    def test_save_with_callable_upload_to(self, storage, utils):
        upload_to = 'prefix'

        class Tester(db.Document):
            file = FileField(fs=storage, upload_to=lambda o: upload_to)

        filename = 'test.txt'

        tester = Tester()
        tester.file.save(utils.filestorage(filename, 'this is a stest'))
        tester.validate()

        expected_filename = '/'.join([upload_to, filename])
        assert tester.file
        assert tester.file.filename == expected_filename
        assert expected_filename in storage
        assert tester.to_mongo() == {
            'file': {
                'filename': expected_filename,
            }
        }

        tester.save()
        tester = Tester.objects.get(id=tester.id)
        assert tester.file.filename == expected_filename

    def test_save_with_callable_basename(self, storage, utils):
        class Tester(db.Document):
            file = FileField(fs=storage, basename=lambda o: 'prefix/filename')

        filename = 'test.txt'

        tester = Tester()
        tester.file.save(utils.filestorage(filename, 'this is a stest'))
        tester.validate()

        expected_filename = 'prefix/filename.txt'
        assert tester.file
        assert tester.file.filename == expected_filename
        assert expected_filename in storage
        assert tester.to_mongo() == {
            'file': {
                'filename': expected_filename,
            }
        }

        tester.save()
        tester = Tester.objects.get(id=tester.id)
        assert tester.file.filename == expected_filename

    def test_save_with_callable_basename_override(self, storage, utils):
        class Tester(db.Document):
            file = FileField(fs=storage, basename=lambda o: 'prefix/filename')

        filename = 'test.txt'
        expected_filename = 'other.txt'

        tester = Tester()
        tester.file.save(utils.filestorage(filename, 'this is a stest'), expected_filename)
        tester.validate()

        assert tester.file
        assert tester.file.filename == expected_filename
        assert expected_filename in storage
        assert tester.to_mongo() == {
            'file': {
                'filename': expected_filename,
            }
        }

        tester.save()
        tester = Tester.objects.get(id=tester.id)
        assert tester.file.filename == expected_filename


class ImageFieldTestMixin(MongoEngineTestCase):
    @pytest.fixture
    def resource(self, utils, image):
        return utils.filestorage('flask.{0}'.format(self.ext), image)

    def test_default_validate(self, storage):
        class Tester(db.Document):
            image = ImageField(fs=storage)

        tester = Tester()
        assert tester.validate() is None

        assert not tester.image
        assert str(tester.image) == ''
        assert tester.to_mongo() == {}
        assert tester.image.filename is None
        assert tester.image.original is None

    def test_save_file(self, storage, image):
        class Tester(db.Document):
            image = ImageField(fs=storage)

        filename = 'test.{0}'.format(self.ext)

        tester = Tester()
        tester.image.save(image, filename)
        tester.validate()

        assert tester.image
        assert str(tester.image) == tester.image.url
        assert tester.image.filename == filename
        assert tester.image.original == filename
        assert filename in storage
        assert tester.to_mongo() == {
            'image': {
                'filename': filename,
            }
        }

        tester.save()
        tester = Tester.objects.get(id=tester.id)
        assert tester.image.filename == filename

        with open(storage.path(filename), 'rb') as f_stored:
            stored = Image.open(f_stored)
            original = Image.open(image)
            assert stored.size == original.size

    def test_save_filestorage(self, storage, resource, image):
        class Tester(db.Document):
            image = ImageField(fs=storage)

        filename = 'flask.{0}'.format(self.ext)

        tester = Tester()
        tester.image.save(resource)
        tester.validate()

        assert tester.image
        assert str(tester.image) == tester.image.url
        assert tester.image.filename == filename
        assert tester.image.original == filename
        assert filename in storage
        assert tester.to_mongo() == {
            'image': {
                'filename': filename,
            }
        }

        tester.save()
        tester = Tester.objects.get(id=tester.id)
        assert tester.image.filename == filename

        with open(storage.path(filename), 'rb') as f_stored:
            stored = Image.open(f_stored)
            original = Image.open(image)
            assert stored.size == original.size

    def test_save_optimize_settings(self, app, storage, resource, image):
        app.config['FS_IMAGES_OPTIMIZE'] = True

        class Tester(db.Document):
            image = ImageField(fs=storage)

        filename = 'flask.{0}'.format(self.ext)
        filename_original = 'flask-original.{0}'.format(self.ext)

        tester = Tester()
        tester.image.save(resource)
        tester.validate()

        assert tester.image
        assert str(tester.image) == tester.image.url
        assert tester.image.filename == filename
        assert tester.image.original == filename_original
        assert filename in storage
        assert tester.to_mongo() == {
            'image': {
                'filename': filename,
                'original': filename_original,
            }
        }

        tester.save()
        tester = Tester.objects.get(id=tester.id)
        assert tester.image.filename == filename
        assert tester.image.original == filename_original

        path_original = storage.path(filename_original)
        path_optimized = storage.path(filename)

        with open(path_original, 'rb') as f_orig:
            with open(path_optimized, 'rb') as f_optimized:
                source = Image.open(image)
                original = Image.open(f_orig)
                optimized = Image.open(f_optimized)
                assert original.size == source.size
                assert optimized.size == source.size
        assert os.stat(path_optimized).st_size < os.stat(path_original).st_size

    def test_save_optimize_attribute(self, app, storage, resource, image):
        class Tester(db.Document):
            image = ImageField(fs=storage, optimize=True)

        filename = 'flask.{0}'.format(self.ext)
        filename_original = 'flask-original.{0}'.format(self.ext)

        tester = Tester()
        tester.image.save(resource)
        tester.validate()

        assert tester.image
        assert str(tester.image) == tester.image.url
        assert tester.image.filename == filename
        assert tester.image.original == filename_original
        assert filename in storage
        assert tester.to_mongo() == {
            'image': {
                'filename': filename,
                'original': filename_original,
            }
        }

        tester.save()
        tester = Tester.objects.get(id=tester.id)
        assert tester.image.filename == filename
        assert tester.image.original == filename_original

        path_original = storage.path(filename_original)
        path_optimized = storage.path(filename)

        with open(path_original, 'rb') as f_orig:
            with open(path_optimized, 'rb') as f_optimized:
                source = Image.open(image)
                original = Image.open(f_orig)
                optimized = Image.open(f_optimized)
                assert original.size == source.size
                assert optimized.size == source.size
        assert os.stat(path_optimized).st_size < os.stat(path_original).st_size

    def test_save_max_size(self, storage, resource, image):
        max_size = 150

        class Tester(db.Document):
            image = ImageField(fs=storage, max_size=max_size)

        filename = 'flask.{0}'.format(self.ext)
        filename_original = 'flask-original.{0}'.format(self.ext)

        tester = Tester()
        tester.image.save(resource)
        tester.validate()

        assert tester.image
        assert str(tester.image) == tester.image.url
        assert tester.image.filename == filename
        assert tester.image.original == filename_original
        assert filename in storage
        assert tester.to_mongo() == {
            'image': {
                'filename': filename,
                'original': filename_original,
            }
        }

        tester.save()
        tester = Tester.objects.get(id=tester.id)
        assert tester.image.filename == filename
        assert tester.image.original == filename_original

        with open(storage.path(filename_original), 'rb') as f_orig:
            with open(storage.path(filename), 'rb') as f_resized:
                source = Image.open(image)
                original = Image.open(f_orig)
                resized = Image.open(f_resized)
                assert original.size == source.size
                assert resized.size[0] <= max_size
                assert resized.size[1] <= max_size
                resized_ratio = resized.size[0] / resized.size[1]
                source_ratio = source.size[0] / source.size[1]
                assert resized_ratio == pytest.approx(source_ratio, 1)

    def test_save_thumbnails(self, storage, image, resource):
        sizes = [150, 32]

        class Tester(db.Document):
            image = ImageField(fs=storage, thumbnails=sizes)

        filename = 'flask.{0}'.format(self.ext)
        filename_150 = 'flask-150.{0}'.format(self.ext)
        filename_32 = 'flask-32.{0}'.format(self.ext)

        tester = Tester()
        tester.image.save(resource)
        tester.validate()

        assert tester.image
        assert str(tester.image) == tester.image.url
        assert tester.image.filename == filename
        assert tester.image.original == filename
        assert tester.image.thumbnail(32) == filename_32
        assert tester.image.thumbnail(150) == filename_150
        with pytest.raises(ValueError):
            tester.image.thumbnail(200)

        assert filename in storage
        assert filename_32 in storage
        assert filename_150 in storage
        assert tester.to_mongo() == {
            'image': {
                'filename': filename,
                'thumbnails': {
                    '32': filename_32,
                    '150': filename_150,
                },
            }
        }

        tester.save()
        tester = Tester.objects.get(id=tester.id)
        assert tester.image.filename == filename
        assert tester.image.original == filename
        assert tester.image.thumbnail(32) == filename_32
        assert tester.image.thumbnail(150) == filename_150

        with open(storage.path(filename), 'rb') as f_orig:
            with open(storage.path(filename_32), 'rb') as f_32:
                with open(storage.path(filename_150), 'rb') as f_150:
                    source = Image.open(image)
                    original = Image.open(f_orig)
                    thumb_32 = Image.open(f_32)
                    thumb_150 = Image.open(f_150)
                    assert original.size == source.size
                    assert thumb_32.size <= (32, 32)
                    assert thumb_150.size <= (150, 150)

    def test_save_thumbnails_with_bbox(self, storage, resource, image):
        sizes = [150, 32]
        bbox = (10, 10, 100, 100)

        filename = 'flask.{0}'.format(self.ext)
        filename_150 = 'flask-150.{0}'.format(self.ext)
        filename_32 = 'flask-32.{0}'.format(self.ext)

        class Tester(db.Document):
            image = ImageField(fs=storage, thumbnails=sizes)

        tester = Tester()
        tester.image.save(resource, bbox=bbox)
        tester.validate()

        assert tester.image
        assert str(tester.image) == tester.image.url
        assert tester.image.filename == filename
        assert tester.image.original == filename
        assert tester.image.thumbnail(32) == filename_32
        assert tester.image.thumbnail(150) == filename_150
        # self.assertSequenceEqual(tester.image.bbox, bbox)
        assert tester.image.bbox == bbox
        with pytest.raises(ValueError):
            tester.image.thumbnail(200)

        assert filename in storage
        assert filename_32 in storage
        assert filename_150 in storage
        assert tester.to_mongo() == {
            'image': {
                'filename': filename,
                'bbox': (10, 10, 100, 100),
                'thumbnails': {
                    '32': filename_32,
                    '150': filename_150,
                },
            }
        }

        tester.save()
        tester = Tester.objects.get(id=tester.id)
        assert tester.image.filename == filename
        assert tester.image.original == filename
        assert tester.image.thumbnail(32) == filename_32
        assert tester.image.thumbnail(150) == filename_150
        assert tuple(tester.image.bbox) == tuple(bbox)
        # self.assertSequenceEqual(tester.image.bbox, bbox)

        # with image as f:
        with open(storage.path(filename), 'rb') as f_orig:
            with open(storage.path(filename_32), 'rb') as f_32:
                with open(storage.path(filename_150), 'rb') as f_150:
                    source = Image.open(image)
                    original = Image.open(f_orig)
                    thumb_32 = Image.open(f_32)
                    thumb_150 = Image.open(f_150)
                    assert original.size == source.size
                    assert thumb_32.size <= (32, 32)
                    assert thumb_150.size <= (150, 150)

    def test_save_wih_two_fields(self, storage, resource):
        sizes = [32]
        bbox = (10, 10, 100, 100)

        filename = 'flask.{0}'.format(self.ext)
        filename_32 = 'flask-32.{0}'.format(self.ext)

        filename2 = 'flask2.{0}'.format(self.ext)

        class Tester(db.Document):
            image = ImageField(fs=storage, thumbnails=sizes)
            image2 = ImageField(fs=storage)

        tester = Tester()
        tester.image.save(resource, bbox=bbox)
        tester.image2.save(resource, filename='flask2.{0}'.format(self.ext))
        tester.validate()

        assert tester.image
        assert str(tester.image) == tester.image.url
        assert tester.image.filename == filename
        assert tester.image.thumbnail(32) == filename_32
        assert tuple(tester.image.bbox) == tuple(bbox)

        assert tester.image2
        assert str(tester.image2) == tester.image2.url
        assert tester.image2.filename == filename2
        assert tester.image2.bbox is None

        assert filename in storage
        assert filename_32 in storage
        assert filename2 in storage
        assert tester.to_mongo() == {
            'image': {
                'filename': filename,
                'bbox': (10, 10, 100, 100),
                'thumbnails': {
                    '32': filename_32,
                },
            },
            'image2': {
                'filename': filename2,
            }
        }

    def test_save_and_update(self, storage, resource):
        sizes = [150, 32]
        bbox = (10, 10, 100, 100)

        filename = 'flask.{0}'.format(self.ext)
        filename_150 = 'flask-150.{0}'.format(self.ext)
        filename_32 = 'flask-32.{0}'.format(self.ext)

        class Tester(db.Document):
            image = ImageField(fs=storage, thumbnails=sizes)

        tester = Tester.objects.create()

        tester.image.save(resource, bbox=bbox)

        assert tester._changed_fields == ['image']

        tester.save()
        tester = Tester.objects.get(id=tester.id)
        assert tester.image.filename == filename
        assert tester.image.original == filename
        assert tester.image.thumbnail(32) == filename_32
        assert tester.image.thumbnail(150) == filename_150
        assert tuple(tester.image.bbox) == tuple(bbox)

    def test_best_match(self, storage, resource):
        sizes = [150, 32]

        # filename = 'flask.{0}'.format(self.ext)
        filename_150 = 'flask-150.{0}'.format(self.ext)
        filename_32 = 'flask-32.{0}'.format(self.ext)

        filename2 = 'flask2.{0}'.format(self.ext)

        class Tester(db.Document):
            image = ImageField(fs=storage, thumbnails=sizes)
            image2 = ImageField(fs=storage)

        tester = Tester()

        assert tester.image(150) is None
        assert tester.image.best_url() is None

        tester.image.save(resource)
        tester.image2.save(resource, filename2)

        assert tester.image.best_url(150) == storage.url(filename_150)
        assert tester.image.best_url(140) == storage.url(filename_150)
        assert tester.image.best_url(100) == storage.url(filename_150)
        assert tester.image.best_url(32) == storage.url(filename_32)
        assert tester.image.best_url(30) == storage.url(filename_32)
        assert tester.image.best_url(160) == storage.url(filename_150)
        assert tester.image.best_url() == storage.url(filename_150)

        assert tester.image(150) == storage.url(filename_150)
        assert tester.image(140) == storage.url(filename_150)
        assert tester.image(160) == storage.url(filename_150)

        assert tester.image2.best_url(150) == storage.url(filename2)
        assert tester.image2.best_url() == storage.url(filename2)

    def test_save_with_upload_to(self, storage, resource):
        upload_to = 'prefix'

        class Tester(db.Document):
            image = ImageField(fs=storage, upload_to=upload_to)

        filename = 'flask.{0}'.format(self.ext)

        tester = Tester()
        tester.image.save(resource)
        tester.validate()

        expected_filename = '/'.join([upload_to, filename])
        assert tester.image
        assert tester.image.filename == expected_filename
        assert expected_filename in storage
        assert tester.to_mongo() == {
            'image': {
                'filename': expected_filename,
            }
        }

        tester.save()
        tester = Tester.objects.get(id=tester.id)
        assert tester.image.filename == expected_filename

    def test_save_with_callable_upload_to(self, storage, resource):
        upload_to = 'prefix'

        class Tester(db.Document):
            image = ImageField(fs=storage, upload_to=lambda o: upload_to)

        filename = 'flask.{0}'.format(self.ext)

        tester = Tester()
        tester.image.save(resource)
        tester.validate()

        expected_filename = '/'.join([upload_to, filename])
        assert tester.image
        assert tester.image.filename == expected_filename
        assert expected_filename in storage
        assert tester.to_mongo() == {
            'image': {
                'filename': expected_filename,
            }
        }

        tester.save()
        tester = Tester.objects.get(id=tester.id)
        assert tester.image.filename == expected_filename

    def test_save_with_callable_basename(self, storage, resource):
        class Tester(db.Document):
            image = ImageField(fs=storage, basename=lambda o: 'prefix/filename')

        tester = Tester()
        tester.image.save(resource)
        tester.validate()

        expected_filename = 'prefix/filename.{0}'.format(self.ext)
        assert tester.image
        assert tester.image.filename == expected_filename
        assert expected_filename in storage
        assert tester.to_mongo() == {
            'image': {
                'filename': expected_filename,
            }
        }

        tester.save()
        tester = Tester.objects.get(id=tester.id)
        assert tester.image.filename == expected_filename

    def test_save_with_callable_basename_override(self, storage, resource):
        class Tester(db.Document):
            image = ImageField(fs=storage, basename=lambda o: 'prefix/filename')

        expected_filename = 'other.{0}'.format(self.ext)

        tester = Tester()
        tester.image.save(resource, expected_filename)
        tester.validate()

        assert tester.image
        assert tester.image.filename == expected_filename
        assert expected_filename in storage
        assert tester.to_mongo() == {
            'image': {
                'filename': expected_filename,
            }
        }

        tester.save()
        tester = Tester.objects.get(id=tester.id)
        assert tester.image.filename == expected_filename

    def test_rerender(self, app, storage, resource, image):
        class Tester(db.Document):
            image = ImageField(fs=storage, optimize=True)

        filename = 'flask.{0}'.format(self.ext)
        filename_original = 'flask-original.{0}'.format(self.ext)

        storage.write(filename, image)

        tester = Tester()
        tester.image.filename = filename
        assert tester.to_mongo() == {
            'image': {
                'filename': filename,
            }
        }

        tester.image.rerender()
        tester.save().reload()

        assert tester.image
        assert str(tester.image) == tester.image.url
        assert tester.image.filename == filename
        assert tester.image.original == filename_original
        assert filename in storage
        assert tester.to_mongo() == {
            '_id': tester.pk,
            'image': {
                'filename': filename,
                'original': filename_original,
            }
        }

        path_original = storage.path(filename_original)
        path_optimized = storage.path(filename)

        with open(path_original, 'rb') as f_orig:
            with open(path_optimized, 'rb') as f_optimized:
                source = Image.open(image)
                original = Image.open(f_orig)
                optimized = Image.open(f_optimized)
                assert original.size == source.size
                assert optimized.size == source.size
        assert os.stat(path_optimized).st_size < os.stat(path_original).st_size

    def test_rerender_multiple(self, app, storage, resource, image):
        class Tester(db.Document):
            image = ImageField(fs=storage, max_size=100, optimize=True)

        filename = 'flask.{0}'.format(self.ext)
        filename_original = 'flask-original.{0}'.format(self.ext)

        storage.write(filename_original, image)

        tester = Tester()
        tester.image.original = filename_original
        tester.image.filename = filename
        assert tester.to_mongo() == {
            'image': {
                'original': filename_original,
                'filename': filename,
            }
        }

        tester.image.rerender()
        tester.save().reload()

        assert tester.image
        assert str(tester.image) == tester.image.url
        assert tester.image.filename == filename
        assert tester.image.original == filename_original
        assert filename in storage
        assert tester.to_mongo() == {
            '_id': tester.pk,
            'image': {
                'filename': filename,
                'original': filename_original,
            }
        }

        path_original = storage.path(filename_original)
        path_optimized = storage.path(filename)

        with open(path_original, 'rb') as f_orig:
            with open(path_optimized, 'rb') as f_optimized:
                source = Image.open(image)
                original = Image.open(f_orig)
                optimized = Image.open(f_optimized)
                assert original.size == source.size
                assert optimized.size[0] == 100
        assert os.stat(path_optimized).st_size < os.stat(path_original).st_size


class ImageFieldPngTest(ImageFieldTestMixin):
    ext = 'png'

    @pytest.fixture
    def image(self, pngfile):
        with open(pngfile, 'rb') as f:
            yield f


class ImageFieldJpgTest(ImageFieldTestMixin):
    ext = 'jpg'

    @pytest.fixture
    def image(self, jpgfile):
        with open(jpgfile, 'rb') as f:
            yield f
