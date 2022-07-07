import pytest
import os

from .test_backend_mixin import BackendTestCase

from flask_fs.backends.local import LocalBackend
from flask_fs.storage import Config


class LocalBackendTest(BackendTestCase):
    hasher = 'sha1'

    @pytest.fixture(autouse=True)
    def setup(self, tmpdir):
        self.test_dir = tmpdir
        self.config = Config({
            'root': str(tmpdir),
        })
        self.backend = LocalBackend('test', self.config)

    def filename(self, filename):
        return str(self.test_dir.join(filename))

    def put_file(self, filename, content):
        filename = self.filename(filename)
        parent = os.path.dirname(filename)
        if not os.path.exists(parent):
            os.makedirs(parent)
        with open(filename, 'wb') as f:
            f.write(self.b(content))

    def get_file(self, filename):
        with open(self.filename(filename), 'rb') as f:
            return f.read()

    def file_exists(self, filename):
        return self.test_dir.join(filename).exists()

    def test_root(self):
        assert self.backend.root == str(self.test_dir)

    def test_default_root(self, app):
        app.config['FS_ROOT'] = str(self.test_dir)
        root = self.test_dir.join('default')
        backend = LocalBackend('default', Config({}))
        assert backend.root == root

    def test_backend_root(self, app):
        app.config['FS_LOCAL_ROOT'] = str(self.test_dir)
        root = self.test_dir.join('default')
        backend = LocalBackend('default', Config({}))
        assert backend.root == root
