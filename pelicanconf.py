#!/usr/bin/env python
# -*- coding: utf-8 -*- #
from __future__ import unicode_literals

AUTHOR = u'thikcube'
SITENAME = u'thinkCube: Play'
SITEURL = 'http://play.thinkcube.com'
PAGE_DIR = 'content/pages'
THEME = "/home/chanux/Projects/play/pelican-themes/tuxlite_tbs"

TIMEZONE = 'Asia/Colombo'

DEFAULT_LANG = u'en'

# Feed generation is usually not desired when developing
FEED_RSS = 'rss.xml'

# Blogroll
# LINKS = (('thinkCube', 'http://thinkcube.com/'),)

# Social widget
SOCIAL = (('Twitter', 'http://twitter.com/thinkcube'),
          ('Github', 'https://github.com/thinkcube'),)

MENUITEMS = (('go to thinkcube.com', 'http://thinkcube.com'),)

DEFAULT_PAGINATION = 10

# Google Analytics
GOOGLE_ANALYTICS = 'UA-46141530-5'

STATIC_PATHS = ['images', 'content/extras/robots.txt']

EXTRA_PATH_METADATA = {
    'content/extras/robots.txt': {'path': 'robots.txt'},
}

# Uncomment following line if you want document-relative URLs when developing
# RELATIVE_URLS = True
