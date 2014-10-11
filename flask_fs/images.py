# -*- coding: utf-8 -*-
'''
This module handle image operations (thumbnailing, resizing...)
'''
from __future__ import unicode_literals, division

import logging
import six

from PIL import Image


log = logging.getLogger(__name__)


def make_thumbnail(file, size, bbox=None):
    '''
    Generate a thumbnail for a given image file.

    :param file file: The source image file to thumbnail
    :param int size: The thumbnail size in pixels (Thumbnails are squares)
    :param tuple bbox: An optionnal Bounding box definition for the thumbnail
    '''
    image = Image.open(file)
    if bbox:
        thumbnail = crop_thumbnail(image, size, bbox)
    else:
        thumbnail = center_thumbnail(image, size)
    return _img_to_file(thumbnail)


def center_thumbnail(image, size):
    result = Image.new('RGBA', (size, size), (255, 255, 255, 0))
    if image.size[0] > image.size[1]:
        new_size = (size, int(image.size[1] * size / image.size[0]))
    else:
        new_size = (int(image.size[0] * size / image.size[1]), size)

    resized = image.resize(new_size, Image.ANTIALIAS)
    position = (int((size - new_size[0]) / 2), int((size - new_size[1]) / 2))
    result.paste(resized, position)
    return result


def crop_thumbnail(image, size, bbox):
    return image.crop(bbox).resize((size, size), Image.ANTIALIAS)


def resize(file, size):
    image = Image.open(file)
    if image.size[0] > size or image.size[1] > size:
        ratio = min(size / image.size[0], size / image.size[1])
        size = (image.size[0] * ratio, image.size[1] * ratio)

        image.thumbnail(size, Image.ANTIALIAS)

        return _img_to_file(image)


def _img_to_file(image):
    out = six.BytesIO()
    if image.mode == 'CMYK':
        image = image.convert('RGBA')
    image.save(out, 'png')
    out.seek(0)
    return out
