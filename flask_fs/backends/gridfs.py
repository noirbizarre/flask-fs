# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import

import codecs
import io
import logging

from contextlib import contextmanager

from flask import send_file
from gridfs import GridFS
from pymongo import MongoClient


from . import BaseBackend

log = logging.getLogger(__name__)


class GridFsBackend(BaseBackend):
    '''
    A Mongo GridFS backend

    Expect the following settings:

    - `mongo_url`: The Mongo access URL
    - `mongo_db`: The database to store the file in.
    '''
    def __init__(self, name, config):
        super(GridFsBackend, self).__init__(name, config)

        self.client = MongoClient(config.mongo_url)
        self.db = self.client[config.mongo_db]
        self.fs = GridFS(self.db, self.name)

    def exists(self, filename):
        return self.fs.exists(filename=filename)

    @contextmanager
    def open(self, filename, mode='r', encoding='utf8'):
        if 'r' in mode:
            f = self.fs.get_last_version(filename)
            yield f if 'b' in mode else codecs.getreader(encoding)(f)
        else:  # mode == 'w'
            f = io.BytesIO() if 'b' in mode else io.StringIO()
            yield f
            params = {'filename': filename}
            if 'b' not in mode:
                params['encoding'] = encoding
            self.fs.put(f.getvalue(), **params)

    def read(self, filename):
        f = self.fs.get_last_version(filename)
        return f.read()

    def write(self, filename, content):
        return self.fs.put(self.as_binary(content), filename=filename)

    def delete(self, filename):
        for version in self.fs.find({'filename': filename}):
            self.fs.delete(version._id)

    def serve(self, filename):
        file = self.fs.get_last_version(filename)
        return send_file(file, mimetype=file.content_type)
