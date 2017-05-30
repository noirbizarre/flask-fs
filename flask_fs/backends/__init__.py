# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from ..storage import Config, KWARGS_CONFIG_ATTR_SUFFIX

import six

__all__ = [i.encode('ascii') for i in ('BaseBackend', 'DEFAULT_BACKEND')]


DEFAULT_BACKEND = 'local'


class BaseBackend(object):
    '''
    Abstract class to implement backend.
    '''
    root = None

    def __init__(self, name, config):
        self.name = name
        self.config = config
        # ensure new connection config is in place
        self.kwargs_config = self.config.setdefault(self.backend_name + KWARGS_CONFIG_ATTR_SUFFIX,
                                                    Config())
        # user may have an existing config, honour that, translating to new dict entry
        if hasattr(self, '_convert_legacy_config'):
            self._convert_legacy_config()

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
