#!/usr/bin/env python
import re

from os.path import join, dirname

from setuptools import setup, find_packages

ROOT = dirname(__file__)

RE_REQUIREMENT = re.compile(r'^\s*-r\s*(?P<filename>.*)$')


def pip(filename):
    """Parse pip reqs file and transform it to setuptools requirements."""
    requirements = []
    for line in open(join(ROOT, 'requirements', filename)):
        line = line.strip()
        if not line or '://' in line:
            continue
        match = RE_REQUIREMENT.match(line)
        if match:
            requirements.extend(pip(match.group('filename')))
        else:
            requirements.append(line)
    return requirements


long_description = '\n'.join((
    open('README.md').read(),
    open('CHANGELOG.rst').read(),
    ''
))

s3_require = pip('s3.pip')
all_require = s3_require
tests_require = pip('test.pip')
doc_require = pip('doc.pip')
qa_require = pip('qa.pip')
ci_require = pip('ci.pip')
dev_require = pip('develop.pip')

setup(
    name='flask-fs',
    version=__import__('flask_fs').__version__,
    description=__import__('flask_fs').__description__,
    long_description=long_description,
    url='https://github.com/etalab/flask-fs',
    author='Etalab',
    author_email='etalab@data.gouv.fr',
    packages=find_packages(),
    include_package_data=True,
    install_requires=pip('install.pip'),
    tests_require=tests_require,
    extras_require={
        'doc': doc_require,
        'test': tests_require,
        's3': s3_require,
        'all': all_require,
        'test': tests_require,
        'qa': tests_require,
        'ci': ci_require,
        'dev': dev_require,
    },
    entry_points={
        'fs.backend': [
            'local = flask_fs.backends.local:LocalBackend',
            's3 = flask_fs.backends.s3:S3Backend [s3]',
            'mock = flask_fs.backends.mock:MockBackend',
        ]
    },
    license='MIT',
    use_2to3=False,
    zip_safe=False,
    keywords='',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Programming Language :: Python',
        'Environment :: Web Environment',
        'Operating System :: OS Independent',
        'Intended Audience :: Developers',
        'Topic :: System :: Software Distribution',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'License :: OSI Approved :: MIT License',
    ],
)
