# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from flask import url_for

import flask_fs as fs


def test_url(app):
    storage = fs.Storage('test')

    app.configure(storage)

    expected_url = url_for('fs.get_file', fs=storage.name, filename='test.txt')
    assert storage.url('test.txt') == expected_url


def test_get_file(app, mock_backend):
    storage = fs.Storage('test')
    backend = mock_backend.return_value
    backend.serve.return_value = 'content'.encode('utf-8')

    app.configure(storage)

    file_url = url_for('fs.get_file', fs='test', filename='test.txt')

    response = app.test_client().get(file_url)
    assert response.status_code == 200
    assert response.data == 'content'.encode('utf-8')


def test_get_file_not_found(app, mock_backend):
    storage = fs.Storage('test')
    backend = mock_backend.return_value
    backend.exists.return_value = False

    app.configure(storage)

    file_url = url_for('fs.get_file', fs='test', filename='test.txt')

    response = app.test_client().get(file_url)
    assert response.status_code == 404


def test_get_file_no_storage(app):
    app.configure()

    file_url = url_for('fs.get_file', fs='fake', filename='test.txt')

    response = app.test_client().get(file_url)
    assert response.status_code == 404
