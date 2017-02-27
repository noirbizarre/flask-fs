# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from os.path import join

from flask import url_for

from flask_fs import Storage, DEFAULTS
from flask_fs.backends.local import LocalBackend


def test_default_configuration(app):
    app.configure()
    assert not app.config['FS_SERVE']
    assert app.config['FS_ROOT'] == join(app.instance_path, 'fs')
    assert app.config['FS_PREFIX'] is None
    assert app.config['FS_URL'] is None


def test_default_debug_configuration(app):
    app.configure(DEBUG=True)
    assert app.config['FS_SERVE']
    assert app.config['FS_ROOT'] == join(app.instance_path, 'fs')
    assert app.config['FS_PREFIX'] is None
    assert app.config['FS_URL'] is None


def test_not_configured():
    files = Storage('files')
    assert files.backend is None
    assert files.config == {}


def test_default_f(app):
    files = Storage('files')
    app.configure(files)

    assert files.name == 'files'
    assert files.extensions == DEFAULTS
    assert isinstance(files.backend, LocalBackend)
    assert files.base_url == url_for('fs.get_file', fs='files', filename='', _external=True)

    assert 'files' in app.extensions['fs']
    assert app.extensions['fs']['files'] == files


def test_custom_prefix(app):
    files = Storage('files')
    app.configure(files, FS_PREFIX='/test')

    assert files.name == 'files'
    assert files.extensions == DEFAULTS
    assert isinstance(files.backend, LocalBackend)
    assert files.base_url == url_for('fs.get_file', fs='files', filename='', _external=True)
    assert files.base_url == 'http://localhost/test/files/'


def test_custom_url(app):
    files = Storage('files')
    app.configure(files, FS_URL='http://somewhere.net/test/')
    assert files.base_url == 'http://somewhere.net/test/files/'


def test_custom_f_url(app):
    files = Storage('files')
    app.configure(files,
        FS_URL='http://somewhere.net/test/',
        FILES_FS_URL='http://somewhere-else.net/test/'
    )
    assert files.base_url == 'http://somewhere-else.net/test/'
