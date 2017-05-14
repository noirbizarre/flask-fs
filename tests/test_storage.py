# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import io

from flask import url_for

import flask_fs as fs

import pytest


def test_by_name(app, mock_backend):
    storage = fs.Storage('test_storage')
    app.configure(storage)

    assert fs.by_name('test_storage') == storage


def test_exists(app, mock_backend):
    storage = fs.Storage('test')
    app.configure(storage)

    backend = mock_backend.return_value

    backend.exists.return_value = True
    assert storage.exists('file.test')
    backend.exists.assert_called_with('file.test')

    backend.exists.return_value = False
    assert not storage.exists('other.test')


def test_in_operator(app, mock_backend):
    storage = fs.Storage('test')
    app.configure(storage)

    backend = mock_backend.return_value

    backend.exists.return_value = True
    assert 'file.test' in storage
    assert 'file.test' in storage
    assert backend.exists.call_count == 2
    backend.exists.assert_called_with('file.test')

    backend.exists.reset_mock()
    backend.exists.return_value = False
    assert 'other.test' not in storage
    assert 'other.test' not in storage
    assert backend.exists.call_count == 2
    backend.exists.assert_called_with('other.test')


def test_open(app, mock_backend):
    storage = fs.Storage('test')
    app.configure(storage)

    backend = mock_backend.return_value
    backend.open.return_value = io.StringIO('content')

    with storage.open('file.test') as f:
        assert f.read() == 'content'

    backend.open.assert_called_with('file.test', 'r')


def test_open_write_new_file(app, mock_backend):
    storage = fs.Storage('test')
    app.configure(storage)

    backend = mock_backend.return_value
    backend.open.return_value = io.StringIO('content')

    with storage.open('file.test', 'w') as f:
        f.write('test')

    backend.open.assert_called_with('file.test', 'w')


def test_open_read_not_found(app, mock_backend):
    storage = fs.Storage('test')
    app.configure(storage)

    backend = mock_backend.return_value
    backend.exists.return_value = False

    with pytest.raises(fs.FileNotFound):
        with storage.open('file.test'):
            pass


def test_read(app, mock_backend):
    storage = fs.Storage('test')
    app.configure(storage)

    backend = mock_backend.return_value
    backend.read.return_value = 'content'

    assert storage.read('file.test') == 'content'


def test_read_not_found(app, mock_backend):
    storage = fs.Storage('test')
    app.configure(storage)

    backend = mock_backend.return_value
    backend.exists.return_value = False

    with pytest.raises(fs.FileNotFound):
        storage.read('file.test')


def test_write(app, mock_backend):
    storage = fs.Storage('test')
    app.configure(storage)

    backend = mock_backend.return_value
    backend.exists.return_value = False

    storage.write('file.test', 'content')
    backend.exists.assert_called_with('file.test')
    backend.write.assert_called_with('file.test', 'content')


def test_write_file_exists(app, mock_backend):
    storage = fs.Storage('test')
    app.configure(storage)

    backend = mock_backend.return_value
    backend.exists.return_value = True

    with pytest.raises(fs.FileExists):
        storage.write('file.test', 'content')


def test_write_overwrite(app, mock_backend):
    storage = fs.Storage('test')
    app.configure(storage)

    backend = mock_backend.return_value

    storage.write('file.test', 'content', overwrite=True)

    backend.write.assert_called_with('file.test', 'content')


def test_write_overwritable(app, mock_backend):
    storage = fs.Storage('test', overwrite=True)
    app.configure(storage)

    backend = mock_backend.return_value

    storage.write('file.test', 'content')

    backend.write.assert_called_with('file.test', 'content')


def test_save_file_exists(app, mock_backend, utils, faker):
    storage = fs.Storage('test')
    app.configure(storage)

    f = utils.file(faker.binary())

    backend = mock_backend.return_value
    backend.exists.return_value = True

    with pytest.raises(fs.FileExists):
        storage.save(f, 'test.png')


def test_save_overwrite(app, mock_backend, utils, faker):
    storage = fs.Storage('test')
    app.configure(storage)

    f = utils.file(faker.binary())

    backend = mock_backend.return_value
    backend.exists.return_value = True

    filename = storage.save(f, 'test.png', overwrite=True)

    assert filename == 'test.png'
    backend.save.assert_called_with(f, 'test.png')


def test_save_from_file(app, mock_backend, utils, faker):
    storage = fs.Storage('test')
    f = utils.file(faker.binary())

    app.configure(storage)

    backend = mock_backend.return_value
    backend.exists.return_value = False

    filename = storage.save(f, 'test.png')

    assert filename == 'test.png'
    backend.save.assert_called_with(f, 'test.png')


def test_save_from_file_storage(app, mock_backend, utils):
    storage = fs.Storage('test')
    content = 'test'
    wfs = utils.filestorage('test.txt', content)

    app.configure(storage)

    backend = mock_backend.return_value
    backend.exists.return_value = False

    filename = storage.save(wfs)

    assert filename == 'test.txt'
    backend.save.assert_called_with(wfs, 'test.txt')


def test_save_with_filename(app, mock_backend, utils):
    storage = fs.Storage('test')
    content = 'test'
    wfs = utils.filestorage('test.txt', content)

    app.configure(storage)

    backend = mock_backend.return_value
    backend.exists.return_value = False

    filename = storage.save(wfs, 'other.gif')

    assert filename == 'other.gif'
    backend.save.assert_called_with(wfs, 'other.gif')


def test_save_with_prefix(app, mock_backend, utils):
    storage = fs.Storage('test')
    content = 'test'
    wfs = utils.filestorage('test.txt', content)

    app.configure(storage)

    backend = mock_backend.return_value
    backend.exists.return_value = False

    filename = storage.save(wfs, prefix='prefix')

    assert filename == 'prefix/test.txt'
    backend.save.assert_called_with(wfs, 'prefix/test.txt')


def test_save_with_callable_prefix(app, mock_backend, utils):
    storage = fs.Storage('test')
    content = 'test'
    wfs = utils.filestorage('test.txt', content)

    app.configure(storage)

    backend = mock_backend.return_value
    backend.exists.return_value = False

    filename = storage.save(wfs, prefix=lambda: 'prefix')

    assert filename == 'prefix/test.txt'
    backend.save.assert_called_with(wfs, 'prefix/test.txt')


def test_save_with_upload_to(app, mock_backend, utils):
    storage = fs.Storage('test', upload_to='upload_to')
    content = 'test'
    wfs = utils.filestorage('test.txt', content)

    app.configure(storage)

    backend = mock_backend.return_value
    backend.exists.return_value = False

    filename = storage.save(wfs)

    assert filename == 'upload_to/test.txt'
    backend.save.assert_called_with(wfs, 'upload_to/test.txt')


def test_save_with_callable_upload_to(app, mock_backend, utils):
    storage = fs.Storage('test', upload_to=lambda: 'upload_to')
    content = 'test'
    wfs = utils.filestorage('test.txt', content)

    app.configure(storage)

    backend = mock_backend.return_value
    backend.exists.return_value = False

    filename = storage.save(wfs)

    assert filename == 'upload_to/test.txt'
    backend.save.assert_called_with(wfs, 'upload_to/test.txt')


def test_save_with_upload_to_and_prefix(app, mock_backend, utils):
    storage = fs.Storage('test', upload_to='upload_to')
    content = 'test'
    wfs = utils.filestorage('test.txt', content)

    app.configure(storage)

    backend = mock_backend.return_value
    backend.exists.return_value = False

    filename = storage.save(wfs, prefix='prefix')

    assert filename == 'upload_to/prefix/test.txt'
    backend.save.assert_called_with(wfs, 'upload_to/prefix/test.txt')


def test_delete(app, mock_backend):
    storage = fs.Storage('test')

    app.configure(storage)

    backend = mock_backend.return_value

    storage.delete('test.txt')

    backend.delete.assert_called_with('test.txt')


def test_url(app):
    storage = fs.Storage('test')

    app.configure(storage)

    params = {'fs': storage.name, 'filename': 'test.txt'}
    expected_url = url_for('fs.get_file', **params)
    assert storage.url('test.txt') == expected_url

    params['_external'] = True
    expected_url = url_for('fs.get_file', **params)
    assert storage.url('test.txt', external=True) == expected_url


def test_url_from_config_without_scheme(app):
    storage = fs.Storage('test')

    app.configure(storage, TEST_FS_URL='somewhere.com/static')

    assert storage.url('test.txt') == 'http://somewhere.com/static/test.txt'

    with app.test_request_context(environ_overrides={'wsgi.url_scheme': 'http'}):
        assert storage.url('test.txt') == 'http://somewhere.com/static/test.txt'

    with app.test_request_context(environ_overrides={'wsgi.url_scheme': 'https'}):
        assert storage.url('test.txt') == 'https://somewhere.com/static/test.txt'


def test_url_from_config_with_scheme(app):
    http = fs.Storage('http')
    https = fs.Storage('https')

    app.configure(http, https,
                  HTTP_FS_URL='http://somewhere.com/static',
                  HTTPS_FS_URL='https://somewhere.com/static'
                  )

    assert http.url('test.txt') == 'http://somewhere.com/static/test.txt'
    assert https.url('test.txt') == 'https://somewhere.com/static/test.txt'

    with app.test_request_context(environ_overrides={'wsgi.url_scheme': 'http'}):
        assert http.url('test.txt') == 'http://somewhere.com/static/test.txt'
        assert https.url('test.txt') == 'https://somewhere.com/static/test.txt'

    with app.test_request_context(environ_overrides={'wsgi.url_scheme': 'https'}):
        assert http.url('test.txt') == 'http://somewhere.com/static/test.txt'
        assert https.url('test.txt') == 'https://somewhere.com/static/test.txt'


def test_root(app, mock_backend):
    storage = fs.Storage('test')
    backend = mock_backend.return_value
    backend.root = '/root'

    app.configure(storage, SERVER_NAME='somewhere')

    assert storage.root == '/root'


def test_no_root(app, mock_backend):
    storage = fs.Storage('test')
    backend = mock_backend.return_value
    backend.root = None

    app.configure(storage, SERVER_NAME='somewhere')

    assert storage.root is None


def test_path(app, mock_backend):
    storage = fs.Storage('test')
    backend = mock_backend.return_value
    backend.root = '/root'

    app.configure(storage)
    assert storage.path('file.test') == '/root/file.test'


def test_path_not_supported(app, mock_backend):
    storage = fs.Storage('test')
    backend = mock_backend.return_value
    backend.root = None

    app.configure(storage)

    with pytest.raises(fs.OperationNotSupported):
        storage.path('file.test')


def test_list_files(app, mock_backend):
    storage = fs.Storage('test')
    backend = mock_backend.return_value
    backend.list_files.return_value = ['one.txt']

    app.configure(storage)

    assert storage.list_files() == ['one.txt']
