# -*- coding: utf-8 -*-

import datetime
from flask.ext.babel import gettext

def get_version(typ):
    version_info = { \
        'version' : '2.0.X beta', 'date' : '2015-07-01',
        'now' : datetime.datetime.now().strftime('%Y-%m-%d'), 'time' : datetime.datetime.now().strftime('%H:%M'), 
        'author' : gettext(''),
        'product_version': gettext('Product Version'),
        'x' : u'©',
        }
    version = '%(product_version)s %(version)s, %(date)s, %(author)s' % version_info
    shortcut_version = u'%(product_version)s %(version)s %(x)s %(author)s, %(date)s' % version_info
    date_version = '%(now)s %(time)s' % version_info
    return typ == 'shortcut' and shortcut_version or version

