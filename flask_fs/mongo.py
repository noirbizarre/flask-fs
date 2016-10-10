# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import bisect
import logging

from os.path import splitext

from mongoengine.fields import BaseField
from werkzeug.datastructures import FileStorage

from .files import extension
from .images import make_thumbnail, resize

log = logging.getLogger(__name__)


class FileReference(object):
    '''Implements the FileField interface'''
    def __init__(self, fs=None, filename=None, upload_to=None, basename=None,
                 instance=None, name=None):
        self.fs = fs
        self.upload_to = upload_to
        self._filename = filename
        self.basename = basename
        self._instance = instance
        self._name = name

    def to_mongo(self):
        return {
            'filename': self.filename
        }

    def save(self, wfs, filename=None):
        '''Save a Werkzeug FileStorage object'''
        if self.basename and not filename:
            ext = extension(filename or wfs.filename)
            filename = '.'.join([self.basename(self._instance), ext])
        prefix = self.upload_to(self._instance) if callable(self.upload_to) else self.upload_to
        self.filename = self.fs.save(wfs, filename, prefix=prefix)
        return self.filename

    @property
    def filename(self):
        return self._filename

    @filename.setter
    def filename(self, value):
        self._mark_as_changed()
        self._filename = value

    @property
    def url(self):
        if self.filename:
            return self.fs.url(self.filename)

    def __unicode__(self):
        return self.url or ''

    __str__ = __unicode__

    def __nonzero__(self):
        return bool(self.filename)

    __bool__ = __nonzero__

    def _mark_as_changed(self):
        if hasattr(self._instance, '_mark_as_changed'):
            self._instance._mark_as_changed(self._name)


class ImageReference(FileReference):
    '''Implements the ImageField interface'''
    def __init__(self, original=None, max_size=None, thumbnail_sizes=None, thumbnails=None,
                 bbox=None, **kwargs):
        super(ImageReference, self).__init__(**kwargs)
        self._original = original
        self.max_size = max_size
        self.thumbnails = thumbnails or {}
        self.bbox = bbox
        self.thumbnail_sizes = thumbnail_sizes

    def to_mongo(self):
        data = super(ImageReference, self).to_mongo()

        if self._original:
            data['original'] = self._original

        if self.thumbnails:
            data['thumbnails'] = self.thumbnails

        if self.bbox:
            data['bbox'] = self.bbox
        return data

    def save(self, file_or_wfs, filename=None, bbox=None):
        '''Save a Werkzeug FileStorage object'''
        self._mark_as_changed()
        override = filename is not None
        filename = filename or getattr(file_or_wfs, 'filename')

        if self.basename and not override:
            basename = self.basename(self._instance)
        elif filename:
            basename = splitext(filename)[0]
        else:
            raise ValueError('Filename is required')

        ext = extension(filename)
        prefix = self.upload_to(self._instance) if callable(self.upload_to) else self.upload_to

        def name(size=None, new_ext=None):
            if size:
                return '.'.join(['-'.join([basename, str(size)]), new_ext or ext])
            else:
                return '.'.join([basename, new_ext or ext])

        if self.max_size:
            resized = resize(file_or_wfs, self.max_size)
            file_or_wfs.seek(0)
            if resized:
                self.original = self.fs.save(file_or_wfs, name('original'), prefix=prefix)
                self.filename = self.fs.save(resized, name(new_ext='png'), prefix=prefix)
            else:
                self.filename = self.fs.save(file_or_wfs, name(), prefix=prefix)
        else:
            self.filename = self.fs.save(file_or_wfs, name(), prefix=prefix)

        if self.thumbnail_sizes:
            self.bbox = bbox
            for size in self.thumbnail_sizes:
                file_or_wfs.seek(0)
                thumbnail = make_thumbnail(file_or_wfs, size, self.bbox)
                self.thumbnails[str(size)] = self.fs.save(FileStorage(thumbnail),
                                                          name(size, 'png'),
                                                          prefix=prefix)
        return self.filename

    @property
    def original(self):
        return self._original or self.filename

    @original.setter
    def original(self, value):
        self._mark_as_changed()
        self._original = value

    def thumbnail(self, size):
        '''Get the thumbnail filename for a given size'''
        if size in self.thumbnail_sizes:
            return self.thumbnails.get(str(size))
        else:
            raise ValueError('Unregistered thumbnail size {0}'.format(size))

    def best_url(self, size=None, external=False):
        '''
        Provide the best thumbnail for downscaling.

        If there is no match, provide the bigger if exists or the original
        '''
        if not self.thumbnail_sizes:
            return self.url
        elif not size:
            self.thumbnail_sizes.sort()
            best_size = self.thumbnail_sizes[-1]
        else:
            self.thumbnail_sizes.sort()
            index = bisect.bisect_left(self.thumbnail_sizes, size)
            if index >= len(self.thumbnail_sizes):
                best_size = self.thumbnail_sizes[-1]
            else:
                best_size = self.thumbnail_sizes[index]
        filename = self.thumbnail(best_size)
        return self.fs.url(filename, external=external) if filename else None

    __call__ = best_url


class FileField(BaseField):
    '''
    Store reference to files in a given storage.
    '''
    proxy_class = FileReference

    def __init__(self, fs=None, upload_to=None, basename=None, *args, **kwargs):
        self.fs = fs
        self.upload_to = upload_to
        self.basename = basename
        super(FileField, self).__init__(*args, **kwargs)

    def proxy(self, filename=None, instance=None, **kwargs):
        return self.proxy_class(
            fs=self.fs,
            filename=filename,
            upload_to=self.upload_to,
            basename=self.basename,
            instance=instance,
            name=self.name,
            **kwargs
        )

    def to_python(self, value):
        if not isinstance(value, self.proxy_class):
            if isinstance(value, dict):
                value = self.proxy(**value)
            elif isinstance(value, basestring):
                value = self.proxy(filename=value)
        return value

    def __set__(self, instance, value):
        if not isinstance(value, self.proxy_class):
            value = self.proxy(filename=value, instance=instance)
        return super(FileField, self).__set__(instance, value)

    def __get__(self, instance, owner):
        if instance is None:
            return self

        fileref = instance._data.get(self.name)
        if not isinstance(fileref, self.proxy_class):
            fileref = self.proxy(filename=fileref, instance=instance)
            instance._data[self.name] = fileref
        elif fileref._instance is None:
            fileref._instance = instance
        return fileref

    def to_mongo(self, value):
        if not value:
            return None
        return value.to_mongo()


class ImageField(FileField):
    '''
    Store reference to images in a given Storage.

    Allow to automatically generate thumbnails or resized image.
    Original image always stay untouched.
    '''
    proxy_class = ImageReference

    def __init__(self, max_size=None, thumbnails=None, *args, **kwargs):
        self.max_size = max_size
        self.thumbnail_sizes = thumbnails
        super(ImageField, self).__init__(*args, **kwargs)

    def proxy(self, **kwargs):
        return super(ImageField, self).proxy(max_size=self.max_size,
                                             thumbnail_sizes=self.thumbnail_sizes,
                                             **kwargs)
