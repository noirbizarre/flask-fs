# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from os.path import join

from flask import url_for

from flask_fs import Storage, DEFAULTS, NONE
from flask_fs.backends.local import LocalBackend


def test_default_configuration(app):
    app.configure()
    assert not app.config['FS_SERVE']
    assert app.config['FS_ROOT'] == join(app.instance_path, 'fs')
    assert app.config['FS_PREFIX'] is None
    assert app.config['FS_URL'] is None
    assert app.config['FS_IMAGES_OPTIMIZE'] is False


def test_default_debug_configuration(app):
    app.configure(DEBUG=True)
    assert app.config['FS_SERVE']
    assert app.config['FS_ROOT'] == join(app.instance_path, 'fs')
    assert app.config['FS_PREFIX'] is None
    assert app.config['FS_URL'] is None
    assert app.config['FS_IMAGES_OPTIMIZE'] is False


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


def test_backend_level_configuration(app):
    files = Storage('files')
    app.configure(files,
                  FS_URL='http://somewhere.net/test/',
                  FS_LOCAL_URL='http://somewhere-else.net/local/'
                  )
    assert isinstance(files.backend, LocalBackend)
    assert files.base_url == 'http://somewhere-else.net/local/files/'


def test_configuration_cascading(app):
    files = Storage('files')
    avatars = Storage('avatars')
    images = Storage('images')
    app.configure(files, avatars, images,
                  FS_BACKEND='s3',
                  FS_S3_ENDPOINT='http://localhost:9000',
                  FS_S3_REGION='us-east-1',
                  FS_S3_ACCESS_KEY='ABCDEFGHIJKLMNOQRSTU',
                  FS_S3_SECRET_KEY='abcdefghiklmnoqrstuvwxyz1234567890abcdef',
                  FS_URL='http://somewhere.net/test/',
                  FS_LOCAL_URL='http://somewhere-else.net/local/',
                  FILES_FS_BACKEND='local',
                  AVATARS_FS_BACKEND='local',
                  AVATARS_FS_URL='http://somewhere-else.net/avatars/'
                  )

    assert files.backend_name == 'local'
    assert avatars.backend_name == 'local'
    assert images.backend_name == 's3'
    assert files.base_url == 'http://somewhere-else.net/local/files/'
    assert avatars.base_url == 'http://somewhere-else.net/avatars/'
    assert images.base_url == 'http://somewhere.net/test/images/'
    assert images.config.endpoint == 'http://localhost:9000'


def test_configurable_extensions(app):
    files = Storage('files', NONE)
    app.configure(files, FS_ALLOW=['txt'])
    assert files.extension_allowed('txt')
