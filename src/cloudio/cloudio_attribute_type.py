# -*- coding: utf-8 -*-

import types

class CloudioAttributeType():
    """Identifies the different data types of attributes currently supported by cloud.io.
    """
    Invalid = 0     # Invalid data type
    Boolean = 1     # The attribute's value is of type boolean
    Integer = 2     # The attribute's value is of type short, int or long
    Number  = 3     # The attribute's value is of type float or double
    String  = 4     # The attribute's value is of type String

    @classmethod
    def fromRawType(cls, rawType):
        """Converts a standard type to its cloud.iO type representation.
        :return The corresponding cloud.iO type.
        :type CloudioAttributeType
        """
        if isinstance(rawType, bool) or rawType == types.BooleanType:
            return cls.Boolean
        elif isinstance(rawType, types.IntType) or rawType == types.IntType:
            return cls.Integer
        elif isinstance(rawType, float) or rawType == types.FloatType:
            return cls.Number
        elif isinstance(rawType, str) or rawType == types.StringType:
            return cls.String
        else:
            return cls.Invalid
