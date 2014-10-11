# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import io
import logging
import os

from shutil import copyfileobj

from flask import current_app, send_from_directory
from werkzeug import cached_property
from werkzeug.datastructures import FileStorage

from . import BaseBackend

log = logging.getLogger(__name__)


class LocalBackend(BaseBackend):
    '''
    A local file system storage

    Expect the following settings:

    - `root`: The file system root
    '''
    @cached_property
    def root(self):
        return self.config.get('root') or os.path.join(current_app.config.get('FS_ROOT'), self.name)

    def exists(self, filename):
        dest = self.path(filename)
        return os.path.exists(dest)

    def open(self, filename, mode='r', encoding='utf8'):
        dest = self.path(filename)
        if 'b' in mode:
            return open(dest, mode)
        else:
            return io.open(dest, mode, encoding=encoding)

    def read(self, filename):
        with self.open(filename, 'rb') as f:
            return f.read()

    def write(self, filename, content):
        dest = self.path(filename)
        dirname = os.path.dirname(dest)
        if not os.path.exists(dirname):
            os.makedirs(dirname)

        with self.open(filename, 'wb') as f:
            return f.write(self.as_binary(content))

    def delete(self, filename):
        dest = os.path.join(self.root, filename)
        return os.remove(dest)

    def save(self, file_or_wfs, filename):
        dest = self.path(filename)

        folder = os.path.dirname(dest)
        if not os.path.exists(folder):
            os.makedirs(folder)

        if isinstance(file_or_wfs, FileStorage):
            file_or_wfs.save(dest)
        else:
            with open(dest, 'wb') as out:
                copyfileobj(file_or_wfs, out)
        return filename

    def path(self, filename):
        '''Return the full path for a given filename in the storage'''
        return os.path.join(self.root, filename)

    def serve(self, filename):
        '''Serve files for storages with direct file access'''
        return send_from_directory(self.root, filename)
