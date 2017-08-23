# -*- coding: utf-8 -*-

__author__ = 'Thomas Sterren'
__version__ = '0.1.0'

# Tell python that there are more sub-packages present, physically located elsewhere.
# See: https://stackoverflow.com/questions/8936884/python-import-path-packages-with-the-same-name-in-different-folders
import pkgutil
__path__ = pkgutil.extend_path(__path__, __name__)