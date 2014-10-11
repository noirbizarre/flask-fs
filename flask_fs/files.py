# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import os.path

__all__ = (
    'TEXT', 'DOCUMENTS', 'IMAGES', 'AUDIO', 'DATA', 'SCRIPTS', 'ARCHIVES', 'EXECUTABLES',
    'DEFAULTS', 'ALL', 'All', 'AllExcept',
)

#: This just contains plain text files (.txt).
TEXT = ['txt']

#: This contains various office document formats
#: (.rtf, .odf, .ods, .gnumeric, .abw, .doc, .docx, .xls, and .xlsx).
#: Note that the macro-enabled versions of Microsoft Office 2007 files are not included.
DOCUMENTS = 'rtf odf ods gnumeric abw doc docx xls xlsx'.split()

#: This contains basic image types that are viewable from most browsers (.jpg,
#: .jpe, .jpeg, .png, .gif, .svg, and .bmp).
IMAGES = 'jpg jpe jpeg png gif svg bmp'.split()

#: This contains audio file types (.wav, .mp3, .aac, .ogg, .oga, and .flac).
AUDIO = 'wav mp3 aac ogg oga flac'.split()

#: This is for structured data files (.csv, .ini, .json, .plist, .xml, .yaml, and .yml).
DATA = 'csv ini json plist xml yaml yml'.split()

#: This contains various types of scripts (.js, .php, .pl, .py .rb, and .sh).
#: If your Web server has PHP installed and set to auto-run,
#: you might want to add ``php`` to the DENY setting.
SCRIPTS = 'js php pl py rb sh bat'.split()

#: This contains archive and compression formats (.gz, .bz2, .zip, .tar, .tgz, .txz, and .7z).
ARCHIVES = 'gz bz2 zip tar tgz txz 7z'.split()

#: This contains shared libraries and executable files (.so, .exe and .dll).
#: Most of the time, you will not want to allow this - it's better suited for use with `AllExcept`.
EXECUTABLES = 'so exe dll'.split()

#: The default allowed extensions - `TEXT`, `DOCUMENTS`, `DATA`, and `IMAGES`.
DEFAULTS = TEXT + DOCUMENTS + IMAGES + DATA


def extension(filename):
    ext = os.path.splitext(filename)[1]
    if ext.startswith('.'):
        # os.path.splitext retains . separator
        ext = ext[1:]
    return ext.lower()


def lower_extension(filename):
    '''
    This is a helper used by :meth:`Storage.save` to provide lowercase extensions for
    all processed files, to compare with configured extensions in the same
    case.

    :param str filename: The filename to ensure has a lowercase extension.
    '''
    if '.' in filename:
        main, ext = os.path.splitext(filename)
        return main + ext.lower()
    # For consistency with os.path.splitext,
    # do not treat a filename without an extension as an extension.
    # That is, do not return filename.lower().
    return filename


class All(object):
    '''
    This type can be used to allow all extensions.
    There is a predefined instance named `ALL`.
    '''
    def __contains__(self, item):
        return True


#: This "contains" all items. You can use it to allow all extensions to be uploaded.
ALL = All()


class AllExcept(object):
    '''
    This can be used to allow all file types except certain ones.

    For example, to exclude .exe and .iso files, pass::

        AllExcept(('exe', 'iso'))

    to the :class:`~flask_fs.Storage` constructor as `extensions` parameter.

    You can use any container, for example::

        AllExcept(SCRIPTS + EXECUTABLES)
    '''
    def __init__(self, items):
        self.items = items

    def __contains__(self, item):
        return item not in self.items
