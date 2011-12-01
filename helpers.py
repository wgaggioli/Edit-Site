from __future__ import division

from django.forms import CheckboxInput
from django.contrib.admin.helpers import AdminField

class InputFieldset(object):
    def __init__(self, input, fields):
        self.input = input
        self.fields = fields

    def __getattr__(self, x):
        return self.input.__getattribute__(x)

    def __iter__(self):
        for field in self.fields:
            yield LayoutField(field)

class LayoutField(AdminField):
    def __init__(self, field):
        self.field = field
        self.is_first = True
        self.is_checkbox = isinstance(self.field.field.widget, CheckboxInput)

def make_safe_input_name(name):
    return name.replace(' ','_').lower()

def get_data_with_prefix(data, prefix):
    filtered = {}
    for key, val in data.iteritems():
        if key.startswith(prefix):
            filtered[key.replace(prefix+'-', '')] = val
    return filtered

def get_image_format_from_name(filename):
    import os.path
    name, ext = os.path.splitext(filename)
    ext = ext[1:]
    if ext in ('jpg','JPG','jpeg','JPEG'):
        return 'JPEG'
    if ext in ('png','PNG'):
        return 'PNG'
    if ext in ('gif','GIF'):
        return 'GIF'
    if ext in ('bmp','BMP'):
        return 'BMP'
    raise TypeError('Image Format not supported')

def resize_image(filename, width=None, height=None):
    from PIL import Image
    im = Image.open(filename)
    w = width or im.size[0]
    h = height or im.size[1]
    w_r = w/im.size[0]
    h_r = h/im.size[1]
    if (w_r < h_r):
        h = int(round(w_r*h))
    else:
        w = int(round(h_r * w))
    if (im.mode != 'RGB'):
        im = im.convert('RGB')
    im = im.resize((w,h), Image.ANTIALIAS)
    im.save(filename, quality=95)
