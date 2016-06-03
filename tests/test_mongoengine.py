# -*- coding: utf-8 -*-
from __future__ import unicode_literals, division

import filecmp
import shutil
import tempfile

from PIL import Image

import flask_fs as fs
from flask_fs.mongo import FileField, ImageField
from flask_mongoengine import MongoEngine

from . import TestCase, BIN_FILE

db = MongoEngine()


class MongoEngineTestCase(TestCase):
    def setUp(self):
        super(MongoEngineTestCase, self).setUp()
        self.app.config['MONGODB_SETTINGS'] = {'DB': 'flask_fs_tests'}
        self._instance_path = self.app.instance_path
        self.app.instance_path = tempfile.mkdtemp()
        self.storage = fs.Storage('test', fs.ALL)
        fs.init_app(self.app, self.storage)
        db.init_app(self.app)
        self._ctx = self.app.test_request_context()
        self._ctx.push()

    def tearsDown(self):  # noqa
        '''Cleanup the mess'''
        super(MongoEngineTestCase, self).tearsDown()
        shutil.rmtree(self.app.instance_path)
        self.app.instance_path = self._instance_path
        db_name = self.app.config['MONGODB_SETTINGS']['DB']
        db.connection.drop_database(db_name)
        self._ctx.pop()
        del self._ctx


class FileFieldTest(MongoEngineTestCase):
    def test_default_validate(self):
        class Tester(db.Document):
            file = FileField(fs=self.storage)

        tester = Tester()

        self.assertIsNone(tester.validate())

        self.assertFalse(tester.file)
        self.assertEqual(str(tester.file), '')
        self.assertEqual(tester.to_mongo(), {})
        self.assertIsNone(tester.file.filename)

    def test_set_filename(self):
        class Tester(db.Document):
            file = FileField(fs=self.storage)

        filename = 'file.test'

        tester = Tester()
        tester.file = filename

        self.assertIsNone(tester.validate())

        self.assertTrue(tester.file)
        self.assertEqual(tester.file.filename, filename)
        self.assertEqual(tester.to_mongo(), {
            'file': {
                'filename': filename,
            }
        })

        tester.save()
        tester.reload()
        self.assertEqual(tester.file.filename, filename)

    def test_save_from_file(self):
        class Tester(db.Document):
            file = FileField(fs=self.storage)

        filename = 'test.png'

        tester = Tester()
        f = open(BIN_FILE, 'rb')
        tester.file.save(f, filename)
        tester.validate()

        self.assertTrue(tester.file)
        self.assertEqual(str(tester.file), tester.file.url)

        self.assertEqual(tester.file.filename, filename)

        self.assertEqual(tester.to_mongo(), {
            'file': {
                'filename': filename,
            }
        })

        self.assertIn(filename, self.storage)

        self.assertTrue(filecmp.cmp(self.storage.path(filename), BIN_FILE))

        tester.save()
        tester = Tester.objects.get(id=tester.id)
        self.assertEqual(tester.file.filename, filename)

    def test_save_from_filestorage(self):
        class Tester(db.Document):
            file = FileField(fs=self.storage)

        filename = 'test.txt'

        tester = Tester()
        tester.file.save(self.filestorage(filename, 'this is a stest'))
        tester.validate()

        self.assertTrue(tester.file)
        self.assertEqual(str(tester.file), tester.file.url)

        self.assertEqual(tester.file.filename, filename)

        self.assertEqual(tester.to_mongo(), {
            'file': {
                'filename': filename,
            }
        })

        self.assertIn(filename, self.storage)

        tester.save()
        tester = Tester.objects.get(id=tester.id)
        self.assertEqual(tester.file.filename, filename)

    def test_save_with_upload_to(self):
        upload_to = 'prefix'

        class Tester(db.Document):
            file = FileField(fs=self.storage, upload_to=upload_to)

        filename = 'test.txt'

        tester = Tester()
        tester.file.save(self.filestorage(filename, 'this is a stest'))
        tester.validate()

        expected_filename = '/'.join([upload_to, filename])
        self.assertTrue(tester.file)
        self.assertEqual(tester.file.filename, expected_filename)
        self.assertIn(expected_filename, self.storage)
        self.assertEqual(tester.to_mongo(), {
            'file': {
                'filename': expected_filename,
            }
        })

        tester.save()
        tester = Tester.objects.get(id=tester.id)
        self.assertEqual(tester.file.filename, expected_filename)

    def test_save_with_callable_upload_to(self):
        upload_to = 'prefix'

        class Tester(db.Document):
            file = FileField(fs=self.storage, upload_to=lambda o: upload_to)

        filename = 'test.txt'

        tester = Tester()
        tester.file.save(self.filestorage(filename, 'this is a stest'))
        tester.validate()

        expected_filename = '/'.join([upload_to, filename])
        self.assertTrue(tester.file)
        self.assertEqual(tester.file.filename, expected_filename)
        self.assertIn(expected_filename, self.storage)
        self.assertEqual(tester.to_mongo(), {
            'file': {
                'filename': expected_filename,
            }
        })

        tester.save()
        tester = Tester.objects.get(id=tester.id)
        self.assertEqual(tester.file.filename, expected_filename)

    def test_save_with_callable_basename(self):
        class Tester(db.Document):
            file = FileField(fs=self.storage, basename=lambda o: 'prefix/filename')

        filename = 'test.txt'

        tester = Tester()
        tester.file.save(self.filestorage(filename, 'this is a stest'))
        tester.validate()

        expected_filename = 'prefix/filename.txt'
        self.assertTrue(tester.file)
        self.assertEqual(tester.file.filename, expected_filename)
        self.assertIn(expected_filename, self.storage)
        self.assertEqual(tester.to_mongo(), {
            'file': {
                'filename': expected_filename,
            }
        })

        tester.save()
        tester = Tester.objects.get(id=tester.id)
        self.assertEqual(tester.file.filename, expected_filename)

    def test_save_with_callable_basename_override(self):
        class Tester(db.Document):
            file = FileField(fs=self.storage, basename=lambda o: 'prefix/filename')

        filename = 'test.txt'
        expected_filename = 'other.txt'

        tester = Tester()
        tester.file.save(self.filestorage(filename, 'this is a stest'), expected_filename)
        tester.validate()

        self.assertTrue(tester.file)
        self.assertEqual(tester.file.filename, expected_filename)
        self.assertIn(expected_filename, self.storage)
        self.assertEqual(tester.to_mongo(), {
            'file': {
                'filename': expected_filename,
            }
        })

        tester.save()
        tester = Tester.objects.get(id=tester.id)
        self.assertEqual(tester.file.filename, expected_filename)


class ImageFieldTest(MongoEngineTestCase):
    def image(self):
        return self.app.open_resource('flask.png', 'rb')

    def resource(self):
        return self.filestorage('flask.png', self.image())

    def test_default_validate(self):
        class Tester(db.Document):
            image = ImageField(fs=self.storage)

        tester = Tester()
        self.assertIsNone(tester.validate())

        self.assertFalse(tester.image)
        self.assertEqual(str(tester.image), '')
        self.assertEqual(tester.to_mongo(), {})
        self.assertIsNone(tester.image.filename)
        self.assertIsNone(tester.image.original)

    def test_save_file(self):
        class Tester(db.Document):
            image = ImageField(fs=self.storage)

        filename = 'test.png'

        tester = Tester()
        tester.image.save(self.image(), filename)
        tester.validate()

        self.assertTrue(tester.image)
        self.assertEqual(str(tester.image), tester.image.url)
        self.assertEqual(tester.image.filename, filename)
        self.assertEqual(tester.image.original, filename)
        self.assertIn(filename, self.storage)
        self.assertEqual(tester.to_mongo(), {
            'image': {
                'filename': filename,
            }
        })

        tester.save()
        tester = Tester.objects.get(id=tester.id)
        self.assertEqual(tester.image.filename, filename)

        with open(self.storage.path(filename), 'rb') as f_stored, self.image() as f_original:
            stored = Image.open(f_stored)
            original = Image.open(f_original)
            self.assertEqual(stored.size, original.size)

    def test_save_filestorage(self):
        class Tester(db.Document):
            image = ImageField(fs=self.storage)

        filename = 'flask.png'

        tester = Tester()
        tester.image.save(self.resource())
        tester.validate()

        self.assertTrue(tester.image)
        self.assertEqual(str(tester.image), tester.image.url)
        self.assertEqual(tester.image.filename, filename)
        self.assertEqual(tester.image.original, filename)
        self.assertIn(filename, self.storage)
        self.assertEqual(tester.to_mongo(), {
            'image': {
                'filename': filename,
            }
        })

        tester.save()
        tester = Tester.objects.get(id=tester.id)
        self.assertEqual(tester.image.filename, filename)

        with open(self.storage.path(filename), 'rb') as f_stored, self.image() as f_original:
            stored = Image.open(f_stored)
            original = Image.open(f_original)
            self.assertEqual(stored.size, original.size)

    def test_save_max_size(self):
        max_size = 150

        class Tester(db.Document):
            image = ImageField(fs=self.storage, max_size=max_size)

        filename = 'flask.png'
        filename_original = 'flask-original.png'

        tester = Tester()
        tester.image.save(self.resource())
        tester.validate()

        self.assertTrue(tester.image)
        self.assertEqual(str(tester.image), tester.image.url)
        self.assertEqual(tester.image.filename, filename)
        self.assertEqual(tester.image.original, filename_original)
        self.assertIn(filename, self.storage)
        self.assertEqual(tester.to_mongo(), {
            'image': {
                'filename': filename,
                'original': filename_original,
            }
        })

        tester.save()
        tester = Tester.objects.get(id=tester.id)
        self.assertEqual(tester.image.filename, filename)
        self.assertEqual(tester.image.original, filename_original)

        with self.image() as f:
            with open(self.storage.path(filename_original), 'rb') as f_orig:
                with open(self.storage.path(filename), 'rb') as f_resized:
                    source = Image.open(f)
                    original = Image.open(f_orig)
                    resized = Image.open(f_resized)
                    self.assertEqual(original.size, source.size)
                    self.assertLessEqual(resized.size[0], max_size)
                    self.assertLessEqual(resized.size[1], max_size)
                    self.assertAlmostEqual(resized.size[0] / resized.size[1],
                                           source.size[0] / source.size[1], 1)

    def test_save_thumbnails(self):
        sizes = [150, 32]

        class Tester(db.Document):
            image = ImageField(fs=self.storage, thumbnails=sizes)

        filename = 'flask.png'
        filename_150 = 'flask-150.png'
        filename_32 = 'flask-32.png'

        tester = Tester()
        tester.image.save(self.resource())
        tester.validate()

        self.assertTrue(tester.image)
        self.assertEqual(str(tester.image), tester.image.url)
        self.assertEqual(tester.image.filename, filename)
        self.assertEqual(tester.image.original, filename)
        self.assertEqual(tester.image.thumbnail(32), filename_32)
        self.assertEqual(tester.image.thumbnail(150), filename_150)
        with self.assertRaises(ValueError):
            tester.image.thumbnail(200)

        self.assertIn(filename, self.storage)
        self.assertIn(filename_32, self.storage)
        self.assertIn(filename_150, self.storage)
        self.assertEqual(tester.to_mongo(), {
            'image': {
                'filename': filename,
                'thumbnails': {
                    '32': filename_32,
                    '150': filename_150,
                },
            }
        })

        tester.save()
        tester = Tester.objects.get(id=tester.id)
        self.assertEqual(tester.image.filename, filename)
        self.assertEqual(tester.image.original, filename)
        self.assertEqual(tester.image.thumbnail(32), filename_32)
        self.assertEqual(tester.image.thumbnail(150), filename_150)

        with self.image() as f:
            with open(self.storage.path(filename), 'rb') as f_orig:
                with open(self.storage.path(filename_32), 'rb') as f_32:
                    with open(self.storage.path(filename_150), 'rb') as f_150:
                        source = Image.open(f)
                        original = Image.open(f_orig)
                        thumb_32 = Image.open(f_32)
                        thumb_150 = Image.open(f_150)
                        self.assertEqual(original.size, source.size)
                        self.assertLessEqual(thumb_32.size, (32, 32))
                        self.assertLessEqual(thumb_150.size, (150, 150))

    def test_save_thumbnails_with_bbox(self):
        sizes = [150, 32]
        bbox = (10, 10, 100, 100)

        filename = 'flask.png'
        filename_150 = 'flask-150.png'
        filename_32 = 'flask-32.png'

        class Tester(db.Document):
            image = ImageField(fs=self.storage, thumbnails=sizes)

        tester = Tester()
        tester.image.save(self.resource(), bbox=bbox)
        tester.validate()

        self.assertTrue(tester.image)
        self.assertEqual(str(tester.image), tester.image.url)
        self.assertEqual(tester.image.filename, filename)
        self.assertEqual(tester.image.original, filename)
        self.assertEqual(tester.image.thumbnail(32), filename_32)
        self.assertEqual(tester.image.thumbnail(150), filename_150)
        self.assertSequenceEqual(tester.image.bbox, bbox)
        with self.assertRaises(ValueError):
            tester.image.thumbnail(200)

        self.assertIn(filename, self.storage)
        self.assertIn(filename_32, self.storage)
        self.assertIn(filename_150, self.storage)
        self.assertEqual(tester.to_mongo(), {
            'image': {
                'filename': filename,
                'bbox': (10, 10, 100, 100),
                'thumbnails': {
                    '32': filename_32,
                    '150': filename_150,
                },
            }
        })

        tester.save()
        tester = Tester.objects.get(id=tester.id)
        self.assertEqual(tester.image.filename, filename)
        self.assertEqual(tester.image.original, filename)
        self.assertEqual(tester.image.thumbnail(32), filename_32)
        self.assertEqual(tester.image.thumbnail(150), filename_150)
        self.assertSequenceEqual(tester.image.bbox, bbox)

        with self.image() as f:
            with open(self.storage.path(filename), 'rb') as f_orig:
                with open(self.storage.path(filename_32), 'rb') as f_32:
                    with open(self.storage.path(filename_150), 'rb') as f_150:
                        source = Image.open(f)
                        original = Image.open(f_orig)
                        thumb_32 = Image.open(f_32)
                        thumb_150 = Image.open(f_150)
                        self.assertEqual(original.size, source.size)
                        self.assertLessEqual(thumb_32.size, (32, 32))
                        self.assertLessEqual(thumb_150.size, (150, 150))

    def test_save_wih_two_fields(self):
        sizes = [32]
        bbox = (10, 10, 100, 100)

        filename = 'flask.png'
        filename_32 = 'flask-32.png'

        filename2 = 'flask2.png'

        class Tester(db.Document):
            image = ImageField(fs=self.storage, thumbnails=sizes)
            image2 = ImageField(fs=self.storage)

        tester = Tester()
        tester.image.save(self.resource(), bbox=bbox)
        tester.image2.save(self.resource(), filename='flask2.png')
        tester.validate()

        self.assertTrue(tester.image)
        self.assertEqual(str(tester.image), tester.image.url)
        self.assertEqual(tester.image.filename, filename)
        self.assertEqual(tester.image.thumbnail(32), filename_32)
        self.assertSequenceEqual(tester.image.bbox, bbox)

        self.assertTrue(tester.image2)
        self.assertEqual(str(tester.image2), tester.image2.url)
        self.assertEqual(tester.image2.filename, filename2)
        self.assertIsNone(tester.image2.bbox)

        self.assertIn(filename, self.storage)
        self.assertIn(filename_32, self.storage)
        self.assertIn(filename2, self.storage)
        self.assertEqual(tester.to_mongo(), {
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
        })

    def test_save_and_update(self):
        sizes = [150, 32]
        bbox = (10, 10, 100, 100)

        filename = 'flask.png'
        filename_150 = 'flask-150.png'
        filename_32 = 'flask-32.png'

        class Tester(db.Document):
            image = ImageField(fs=self.storage, thumbnails=sizes)

        tester = Tester.objects.create()

        tester.image.save(self.resource(), bbox=bbox)

        self.assertEqual(tester._changed_fields, ['image'])

        tester.save()
        tester = Tester.objects.get(id=tester.id)
        self.assertEqual(tester.image.filename, filename)
        self.assertEqual(tester.image.original, filename)
        self.assertEqual(tester.image.thumbnail(32), filename_32)
        self.assertEqual(tester.image.thumbnail(150), filename_150)
        self.assertSequenceEqual(tester.image.bbox, bbox)

    def test_best_match(self):
        sizes = [150, 32]

        # filename = 'flask.png'
        filename_150 = 'flask-150.png'
        filename_32 = 'flask-32.png'

        filename2 = 'flask2.png'

        class Tester(db.Document):
            image = ImageField(fs=self.storage, thumbnails=sizes)
            image2 = ImageField(fs=self.storage)

        tester = Tester()

        self.assertIsNone(tester.image(150))
        self.assertIsNone(tester.image.best_url())

        tester.image.save(self.resource())
        tester.image2.save(self.resource(), filename2)

        self.assertEqual(tester.image.best_url(150), self.storage.url(filename_150))
        self.assertEqual(tester.image.best_url(140), self.storage.url(filename_150))
        self.assertEqual(tester.image.best_url(100), self.storage.url(filename_150))
        self.assertEqual(tester.image.best_url(32), self.storage.url(filename_32))
        self.assertEqual(tester.image.best_url(30), self.storage.url(filename_32))
        self.assertEqual(tester.image.best_url(160), self.storage.url(filename_150))
        self.assertEqual(tester.image.best_url(), self.storage.url(filename_150))

        self.assertEqual(tester.image(150), self.storage.url(filename_150))
        self.assertEqual(tester.image(140), self.storage.url(filename_150))
        self.assertEqual(tester.image(160), self.storage.url(filename_150))

        self.assertEqual(tester.image2.best_url(150), self.storage.url(filename2))
        self.assertEqual(tester.image2.best_url(), self.storage.url(filename2))

    def test_save_with_upload_to(self):
        upload_to = 'prefix'

        class Tester(db.Document):
            image = ImageField(fs=self.storage, upload_to=upload_to)

        filename = 'flask.png'

        tester = Tester()
        tester.image.save(self.resource())
        tester.validate()

        expected_filename = '/'.join([upload_to, filename])
        self.assertTrue(tester.image)
        self.assertEqual(tester.image.filename, expected_filename)
        self.assertIn(expected_filename, self.storage)
        self.assertEqual(tester.to_mongo(), {
            'image': {
                'filename': expected_filename,
            }
        })

        tester.save()
        tester = Tester.objects.get(id=tester.id)
        self.assertEqual(tester.image.filename, expected_filename)

    def test_save_with_callable_upload_to(self):
        upload_to = 'prefix'

        class Tester(db.Document):
            image = ImageField(fs=self.storage, upload_to=lambda o: upload_to)

        filename = 'flask.png'

        tester = Tester()
        tester.image.save(self.resource())
        tester.validate()

        expected_filename = '/'.join([upload_to, filename])
        self.assertTrue(tester.image)
        self.assertEqual(tester.image.filename, expected_filename)
        self.assertIn(expected_filename, self.storage)
        self.assertEqual(tester.to_mongo(), {
            'image': {
                'filename': expected_filename,
            }
        })

        tester.save()
        tester = Tester.objects.get(id=tester.id)
        self.assertEqual(tester.image.filename, expected_filename)

    def test_save_with_callable_basename(self):
        class Tester(db.Document):
            image = ImageField(fs=self.storage, basename=lambda o: 'prefix/filename')

        tester = Tester()
        tester.image.save(self.resource())
        tester.validate()

        expected_filename = 'prefix/filename.png'
        self.assertTrue(tester.image)
        self.assertEqual(tester.image.filename, expected_filename)
        self.assertIn(expected_filename, self.storage)
        self.assertEqual(tester.to_mongo(), {
            'image': {
                'filename': expected_filename,
            }
        })

        tester.save()
        tester = Tester.objects.get(id=tester.id)
        self.assertEqual(tester.image.filename, expected_filename)

    def test_save_with_callable_basename_override(self):
        class Tester(db.Document):
            image = ImageField(fs=self.storage, basename=lambda o: 'prefix/filename')

        expected_filename = 'other.png'

        tester = Tester()
        tester.image.save(self.resource(), expected_filename)
        tester.validate()

        self.assertTrue(tester.image)
        self.assertEqual(tester.image.filename, expected_filename)
        self.assertIn(expected_filename, self.storage)
        self.assertEqual(tester.to_mongo(), {
            'image': {
                'filename': expected_filename,
            }
        })

        tester.save()
        tester = Tester.objects.get(id=tester.id)
        self.assertEqual(tester.image.filename, expected_filename)
