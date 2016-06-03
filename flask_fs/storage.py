# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import os.path

try:
    from urllib.parse import urljoin
except:
    from urlparse import urljoin

from flask import current_app, url_for, request, abort
from werkzeug import secure_filename, FileStorage, cached_property
from werkzeug.utils import import_string


from .backends import BUILTIN_BACKENDS
from .errors import UnauthorizedFileType, FileExists, OperationNotSupported, FileNotFound
from .files import DEFAULTS, extension, lower_extension


DEFAULT_CONFIG = {
    'allow': DEFAULTS,
    'deny': tuple(),
}

CONF_PREFIX = 'FS_'
PREFIX = '{0}_FS_'


class Config(dict):
    '''
    Wrap the configuration for a single :class:`Storage`.

    Basically, it's an ObjectDict
    '''
    def __getattr__(self, name):
        if name in self:
            return self[name]
        else:
            raise AttributeError('Unknown attribute: ' + name)

    def __setattr__(self, name, value):
        self[name] = value

    def __delattr__(self, name):
        if name in self:
            del self[name]
        else:
            raise AttributeError('Unknown attribute: ' + name)


class Storage(object):
    '''
    This represents a single set of files.
    Each Storage is independent of the others.
    This can be reused across multiple application instances,
    as all configuration is stored on the application object itself
    and found with `flask.current_app`.

    :param str name:
        The name of this storage. It defaults to ``files``,
        but you can pick any alphanumeric name you want.
    :param tuple extensions:
        The extensions to allow uploading in this storage.
        The easiest way to do this is to add together the extension presets
        (for example, ``TEXT + DOCUMENTS + IMAGES``).
        It can be overridden by the configuration with the `{NAME}_FS_ALLOW`
        and `{NAME}_FS__DENY` configuration parameters.
        The default is `DEFAULTS`.
    :param str|callable upload_to:
        If given, this should be a callable.
        If you call it with the app,
        it should return the default upload destination path for that app.
    :param bool overwrite:
        Whether or not to allow overwriting
    '''

    def __init__(self, name='files', extensions=DEFAULTS, upload_to=None, overwrite=False):
        self.name = name
        self.extensions = extensions
        self.config = Config()
        self.upload_to = upload_to
        self.backend = None
        self.overwrite = overwrite

    def configure(self, app):
        '''
        Load configuration from application configuration.

        For each storage, the configuration is loaded with the following pattern::

            {STORAGE_NAME}_FS_{KEY}

        If no configuration is set for a given key, global config is taken as default.
        '''
        prefix = PREFIX.format(self.name.upper())
        config = Config()

        # Set default values
        for key, value in DEFAULT_CONFIG.items():
            config.setdefault(key, value)

        for key, value in app.config.items():
            if key.startswith(prefix):
                config[key.replace(prefix, '').lower()] = value

        backend = config.get('backend', app.config['FS_BACKEND'])
        if backend in BUILTIN_BACKENDS:
            backend_class = import_string(BUILTIN_BACKENDS[backend])
        else:
            backend_class = import_string(backend)
        self.backend = backend_class(self.name, config)
        self.config = config

    @cached_property
    def root(self):
        return self.backend.root

    @property
    def base_url(self):
        '''The public URL for this storage'''
        config_value = self.config.get('url')
        if config_value:
            return self._clean_url(config_value)
        default_url = current_app.config.get('FS_URL')
        if default_url:
            url = urljoin(default_url, self.name)
            return self._clean_url(url)
        return url_for('fs.get_file', fs=self.name, filename='', _external=True)

    def _clean_url(self, url):
        if not url.startswith('http://') and not url.startswith('https://'):
            url = ('https://' if request.is_secure else 'http://') + url
        if not url.endswith('/'):
            url += '/'
        return url

    @property
    def has_url(self):
        '''Whether this storage has a public URL or not'''
        return bool(self.config.get('url') or current_app.config.get('FS_URL'))

    def url(self, filename, external=False):
        '''
        This function gets the URL a file uploaded to this set would be
        accessed at. It doesn't check whether said file exists.

        :param string filename: The filename to return the URL for.
        :param bool external: If True, returns an absolute URL
        '''
        if filename.startswith('/'):
            filename = filename[1:]
        if self.has_url:
            return self.base_url + filename
        else:
            return url_for('fs.get_file', fs=self.name, filename=filename, _external=external)

    def path(self, filename):
        '''
        This returns the absolute path of a file uploaded to this set. It
        doesn't actually check whether said file exists.

        :param filename: The filename to return the path for.
        :param folder: The subfolder within the upload set previously used
                       to save to.

        :raises OperationNotSupported: when the backenddoesn't support direct file access
        '''
        if not self.backend.root:
            raise OperationNotSupported(
                'Direct file access is not supported by ' +
                self.backend.__class__.__name__
            )
        return os.path.join(self.backend.root, filename)

    def exists(self, filename):
        '''
        Verify whether a file exists or not.
        '''
        return self.backend.exists(filename)

    def file_allowed(self, storage, basename):
        '''
        This tells whether a file is allowed.

        It should return `True` if the given :class:`~werkzeug.FileStorage` object
        can be saved with the given basename, and `False` if it can't.
        The default implementation just checks the extension,
        so you can override this if you want.

        :param storage: The `werkzeug.FileStorage` to check.
        :param basename: The basename it will be saved under.
        '''
        return self.extension_allowed(extension(basename))

    def extension_allowed(self, ext):
        '''
        This determines whether a specific extension is allowed.
        It is called by `file_allowed`, so if you override that but still want to check
        extensions, call back into this.

        :param str ext: The extension to check, without the dot.
        '''
        return ((ext in self.config.allow) or
                (ext in self.extensions and ext not in self.config.deny))

    def read(self, filename):
        '''
        Read a file content.

        :param string filename: The storage root-relative filename
        :raises FileNotFound: If the file does not exists
        '''
        if not self.backend.exists(filename):
            raise FileNotFound(filename)
        return self.backend.read(filename)

    def open(self, filename, mode='r', **kwargs):
        '''
        Open the file and return a file-like object.

        :param str filename: The storage root-relative filename
        :param str mode: The open mode (``(r|w)b?``)
        :raises FileNotFound: If trying to read a file that does not exists
        '''
        if 'r' in mode and not self.backend.exists(filename):
            raise FileNotFound(filename)
        return self.backend.open(filename, mode, **kwargs)

    def write(self, filename, content, overwrite=False):
        '''
        Write content to a file.

        :param str filename: The storage root-relative filename
        :param content: The content to write in the file
        :param bool overwrite: Whether to wllow overwrite or not
        :raises FileExists: If the file exists and `overwrite` is `False`
        '''
        if not self.overwrite and not overwrite and self.backend.exists(filename):
            raise FileExists()
        return self.backend.write(filename, content)

    def delete(self, filename):
        '''
        Delete a file.

        :param str filename: The storage root-relative filename
        '''
        return self.backend.delete(filename)

    def save(self, file_or_wfs, filename=None, prefix=None, overwrite=None):
        '''
        Saves a `file` or a :class:`~werkzeug.FileStorage` into this storage.

        If the upload is not allowed, an :exc:`UploadNotAllowed` error will be raised.
        Otherwise, the file will be saved and its name (including the folder)
        will be returned.

        :param file_or_wfs: a file or :class:`werkzeug.FileStorage` file to save.
        :param string filename: The expected filename in the storage.
            Optionnal with a :class:`~werkzeug.FileStorage` but allow to override clietn value
        :param string prefix: a path or a callable returning a path to be prepended to the filename.
        :param bool overwrite: if specified, override the storage default value.

        :raise UnauthorizedFileType: If the file type is not allowed
        '''
        if not filename and isinstance(file_or_wfs, FileStorage):
            filename = lower_extension(secure_filename(file_or_wfs.filename))

        if not filename:
            raise ValueError('filename is required')

        if not self.file_allowed(file_or_wfs, filename):
            raise UnauthorizedFileType()

        if prefix:
            filename = '/'.join((prefix() if callable(prefix) else prefix, filename))

        if self.upload_to:
            upload_to = self.upload_to() if callable(self.upload_to) else self.upload_to
            filename = '/'.join((upload_to, filename))

        overwrite = self.overwrite if overwrite is None else overwrite
        if not overwrite and self.exists(filename):
            raise FileExists(filename)

        self.backend.save(file_or_wfs, filename)

        return filename

    def __contains__(self, value):
        return self.exists(value)

    def resolve_conflict(self, target_folder, basename):
        '''
        If a file with the selected name already exists in the target folder,
        this method is called to resolve the conflict. It should return a new
        basename for the file.

        The default implementation splits the name and extension and adds a
        suffix to the name consisting of an underscore and a number, and tries
        that until it finds one that doesn't exist.

        :param str target_folder: The absolute path to the target.
        :param str basename: The file's original basename.
        '''
        name, ext = os.path.splitext(basename)
        count = 0
        while True:
            count = count + 1
            newname = '%s_%d%s' % (name, count, ext)
            if not os.path.exists(os.path.join(target_folder, newname)):
                return newname

    def serve(self, filename):
        '''Serve a file given its filename'''
        if not self.exists(filename):
            abort(404)
        return self.backend.serve(filename)
