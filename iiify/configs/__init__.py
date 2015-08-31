#!/usr/bin/env python
# -*-coding: utf-8 -*-

"""
    __init__.py
    ~~~~~~~~~~~
    Configurations for iiify

    :copyright: (c) 2015 by AUTHORS
    :license: see LICENSE for more details
"""

import os
import types
import configparser

path = os.path.dirname(os.path.realpath(__file__))
approot = os.path.abspath(os.path.join(path, os.pardir))


def getdef(self, section, option, default_value):
    try:
        return self.get(section, option)
    except:
        return default_value


config = configparser.ConfigParser()
config.read('%s/settings.cfg' % path)
config.getdef = types.MethodType(getdef, config)

HOST = config.getdef('server', 'host', '0.0.0.0')
PORT = int(config.getdef('server', 'port', 8080))
DEBUG = bool(int(config.getdef('server', 'debug', 1)))
CRT = config.getdef('ssl', 'crt', '')
KEY = config.getdef('ssl', 'key', '')
options = {'debug': DEBUG, 'host': HOST, 'port': PORT}
if CRT and KEY:
    options['ssl_context'] = (CRT, KEY)

# Enable CORS to allow cross-domain loading of tilesets from this server
# Especially useful for SeaDragon viewers running locally
cors = bool(int(config.getdef('server', 'cors', 0)))

media_root = config.getdef('media', 'root', 'media')
if not os.path.isabs(media_root):
    media = os.path.join(approot, media_root)
if not os.path.exists(media_root):
    os.makedirs(media_root)

cache_root = config.getdef('cache', 'root', 'cache')
if not os.path.isabs(cache_root):
    cache = os.path.join(approot, cache_root)
if not os.path.exists(cache_root):
    os.makedirs(cache_root)

cache_expr = config.getdef('cache', 'expr', 100)
