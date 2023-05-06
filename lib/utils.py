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
if six.PY3:
    long = int
    LOGINFO = xbmc.LOGINFO
else:
    LOGINFO = xbmc.LOGNOTICE

try:
    translatePath = xbmcvfs.translatePath
except:
    translatePath = xbmc.translatePath

ADDON = xbmcaddon.Addon()
data_path = translatePath(ADDON.getAddonInfo('Profile'))

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


def logger(message, level=None):
    def format_message(data=""):
        try:
            value = str(data)
        except Exception:
            value = repr(data)

        if isinstance(value, six.binary_type):
            value = six.text_type(value, 'utf8', 'replace')

        """if isinstance(value, unicode):
            return [value]
        else:
            return value"""
        return value

    texto = '[%s] %s' % (xbmcaddon.Addon().getAddonInfo('id'), format_message(message))

    try:
        if level == 'info':
            xbmc.log(texto, LOGINFO)
        elif level == 'error':
            xbmc.log("######## ERROR #########", xbmc.LOGERROR)
            xbmc.log(texto, xbmc.LOGERROR)
        else:
            xbmc.log("######## DEBUG #########", LOGINFO)
            xbmc.log(texto, LOGINFO)
    except:
        # xbmc.log(six.ensure_str(texto, encoding='latin1', errors='strict'), LOGINFO)
        xbmc.log(str([texto]), LOGINFO)


locker = Lock()
def load_json_file(path):
    with locker:
        data = open(path, 'rb').read()

    data = load_json(six.ensure_str(data))
    return data


def dump_json_file(data, path):
    if not os.path.exists(os.path.dirname(path)):
        os.makedirs(os.path.dirname(path))
    data = six.ensure_binary(dump_json(data))
    with locker:
        open(path, 'wb').write(data)

def load_json(*args, **kwargs):
    if "object_hook" not in kwargs:
        kwargs["object_hook"] = set_encoding

    try:
        value = json.loads(*args, **kwargs)
    except Exception as e:
        #logger(e, "error")
        value = {}

    return value

def dump_json(*args, **kwargs):
    if not kwargs:
        kwargs = {
            'indent': 4,
            'skipkeys': True,
            'sort_keys': True,
            'ensure_ascii': False
        }

    try:
        value = json.dumps(*args, **kwargs)
    except Exception as e:
        #logger(e, "error")
        value = ''

    return value

def set_encoding(dct):
    if isinstance(dct, dict):
        return dict((set_encoding(key), set_encoding(value)) for key, value in dct.items())
    elif isinstance(dct, list):
        return [set_encoding(element) for element in dct]
    elif isinstance(dct, six.string_types):
        return six.ensure_str(dct)
    else:
        return dct

def get_setting(name, default=None):
    value = xbmcaddon.Addon().getSetting(name)

    if not value:
        return default
    elif value == 'true':
        return True
    elif value == 'false':
        return False
    else:
        try:
            value = value
        except ValueError:
            try:
                value = long(value)
            except ValueError:
                try:
                    is_list = eval(value)
                    if isinstance(is_list, list):
                        value = is_list
                    else:
                        raise()
                except:
                    try:
                        aux = load_json(value)
                        if aux: value = aux
                    except ValueError:
                        pass

        return value


def set_setting(name, value):
    try:
        if isinstance(value, bool):
            if value:
                value = "true"
            else:
                value = "false"
        elif isinstance(value, (int, long, list)):
            value = str(value)
        elif not isinstance(value, str):
            value = dump_json(value)

        xbmcaddon.Addon().setSetting(name, value)

    except Exception as ex:
        logger("Error al convertir '%s' no se guarda el valor \n%s" % (name, ex), 'error')
        return None

    return value

