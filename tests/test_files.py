from flask_fs import files


def test_extension():
    assert files.extension('foo.txt') == 'txt'
    assert files.extension('foo') == ''
    assert files.extension('archive.tar.gz') == 'gz'
    assert files.extension('audio.m4a') == 'm4a'


def test_lowercase_ext():
    assert files.lower_extension('foo.txt') == 'foo.txt'
    assert files.lower_extension('FOO.TXT') == 'FOO.txt'
    assert files.lower_extension('foo') == 'foo'
    assert files.lower_extension('FOO') == 'FOO'
    assert files.lower_extension('archive.tar.gz') == 'archive.tar.gz'
    assert files.lower_extension('ARCHIVE.TAR.GZ') == 'ARCHIVE.TAR.gz'
    assert files.lower_extension('audio.m4a') == 'audio.m4a'
    assert files.lower_extension('AUDIO.M4A') == 'AUDIO.m4a'


def test_all():
    assert 'txt' in files.ALL
    assert 'exe' in files.ALL
    assert 'any' in files.ALL


def test_none():
    assert 'txt' not in files.NONE
    assert 'exe' not in files.NONE
    assert 'any' not in files.NONE


def test_all_except():
    all_except = files.AllExcept('exe')
    assert 'csv' in all_except
    assert 'exe' not in all_except


def test_mime_known_type():
    assert files.mime('test.txt') == 'text/plain'
    assert files.mime('test.csv') == 'text/csv'


def test_mime_default_to_none():
    assert files.mime('test') is None
    assert files.mime('test', default=None) is None


def test_mime_default_to_custom():
    default = 'application/octet-stream'
    assert files.mime('test', default=default) == default
