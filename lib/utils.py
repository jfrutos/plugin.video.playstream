# -*- coding: utf-8 -*-

import sys, os ,re
import xbmc, xbmcgui, xbmcplugin, xbmcaddon, xbmcvfs
import base64
import shutil
import time
import json
import subprocess

from threading import Thread, Lock
from six.moves import urllib_parse

import six


class Item(object):
    defaults = {}

    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)

    def __contains__(self, item):
        return item in self.__dict__

    def __getattribute__(self, item):
        return object.__getattribute__(self, item)

    def __getattr__(self, item):
        if item.startswith("__"):
            return object.__getattribute__(self, item)
        else:
            return self.defaults.get(item, '')

    def __str__(self):
        return '{%s}' % (', '.join(['\'%s\': %s' % (k, repr(self.__dict__[k])) for k in sorted(self.__dict__.keys())]))

    def getart(self):
        if 'fanart' not in self.__dict__:
            self.__dict__['fanart'] = os.path.join(runtime_path,'fanart.jpg')
        if 'icon' not in self.__dict__ and 'poster' not in self.__dict__ and 'thumb' not in self.__dict__:
            self.__dict__['icon'] = icon_path
        return {k:self.__dict__.get(k) for k in ['poster', 'icon', 'fanart', 'thumb'] if k in self.__dict__}

    def tourl(self):
        value = self.__str__()
        if not isinstance(value, six.binary_type):
            value = six.binary_type(value, 'utf8')
        return six.ensure_str(urllib_parse.quote(base64.b64encode(value)))

    def fromurl(self, url):
        str_item = base64.b64decode(urllib_parse.unquote(url))
        self.__dict__.update(eval(str_item))
        return self

    def tojson(self, path=""):
        if path:
            open(path, "wb").write(dump_json(self.__dict__))
        else:
            return dump_json(self.__dict__)

    def fromjson(self, json_item=None, path=""):
        if path:
            json_item = open(path, "rb").read()

        if type(json_item) == str:
            item = load_json(json_item)
        else:
            item = json_item
        self.__dict__.update(item)
        return self

    def clone(self, **kwargs):
        newitem = copy.deepcopy(self)
        for k, v in kwargs.items():
            '''if k in  ['plot']:
                continue'''
            setattr(newitem, k, v)
        return newitem



