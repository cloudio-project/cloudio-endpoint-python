# -*- coding: utf-8 -*-

__author__ = 'Thomas Sterren'
__version__ = '0.2.7'

import six

if six.PY3:
    from .endpoint import CloudioEndpoint
    from .endpoint import version
else:
    from endpoint import CloudioEndpoint
    from endpoint import version
