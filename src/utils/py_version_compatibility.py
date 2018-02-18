# -*- coding: utf-8 -*-

import six
if six.PY2:
    import types

#
# In python 3 there standard type representations BooleanType, etc.
# were removed from types packages. They are represented with its native
# expression.
#
# Links:
# - http://www.diveintopython3.net/porting-code-to-python-3-with-2to3.html#types

if six.PY2:
    BooleanType = types.BooleanType
    IntType = types.IntType
    LongType = types.LongType
    FloatType = types.FloatType
    StringType = types.StringType
else:
    BooleanType = bool
    IntType = int
    LongType = int
    FloatType = float
    StringType = bytes