# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import six

from flask_fs import files

__all__ = [i.encode('ascii') for i in ('BaseBackend', 'DEFAULT_BACKEND')]


DEFAULT_BACKEND = 'local'


class BaseBackend(object):
    '''
    Abstract class to implement backend.
    '''
    root = None
    DEFAULT_MIME = 'application/octet-stream'

    def __init__(self, name, config):
        self.name = name
        self.config = config

    def exists(self, filename):
        '''Test wether a file exists or not given its filename in the storage'''
        raise NotImplementedError('Existance checking is not implemented')

    def open(self, filename, *args, **kwargs):
        '''Open a file given its filename relative to the storage root'''
        raise NotImplementedError('Open operation is not implemented')

    def read(self, filename):
        '''Read a file content given its filename in the storage'''
        raise NotImplementedError('Read operation is not implemented')

    def write(self, filename, content):
        '''Write content into a file given its filename in the storage'''
        raise NotImplementedError('Write operation is not implemented')

    def delete(self, filename):
        '''Delete a file given its filename in the storage'''
        raise NotImplementedError('Delete operation is not implemented')

    def copy(self, filename, target):
        '''Copy a file given its filename to another path in the storage'''
        raise NotImplementedError('Copy operation is not implemented')

    def move(self, filename, target):
        '''
        Move a file given its filename to another path in the storage

        Default implementation perform a copy then a delete.
        Backends should overwrite it if there is a better way.
        '''
        self.copy(filename, target)
        self.delete(filename)

    def save(self, file_or_wfs, filename, overwrite=False):
        '''
        Save a file-like object or a `werkzeug.FileStorage` with the specified filename.

        :param storage: The file or the storage to be saved.
        :param filename: The destination in the storage.
        :param overwrite: if `False`, raise an exception if file exists in storage

        :raises FileExists: when file exists and overwrite is `False`
        '''
        self.write(filename, file_or_wfs.read())
        return filename

    def metadata(self, filename):
        '''
        Fetch all available metadata for a given file
        '''
        meta = self.get_metadata(filename)
        # Fix backend mime misdetection
        meta['mime'] = meta.get('mime') or files.mime(filename, self.DEFAULT_MIME)
        return meta

    def get_metadata(self, filename):
        '''
        Backend specific method to retrieve metadata for a given file
        '''
        raise NotImplementedError('Copy operation is not implemented')

    def serve(self, filename):
        '''Serve a file given its filename'''
        raise NotImplementedError('serve operation is not implemented')

    def as_binary(self, content, encoding='utf8'):
        '''Perform content encoding for binary write'''
        if hasattr(content, 'read'):
            return content.read()
        elif isinstance(content, six.text_type):
            return content.encode(encoding)
        else:
            return content
