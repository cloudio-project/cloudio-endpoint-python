# -*- coding: utf-8 -*-

from cloudio.exception.invalid_cloudio_attribute_type_exception import InvalidCloudioAttributeTypeException
import utils.py_version_compatibility as types

class CloudioAttributeType():
    """Identifies the different data types of attributes currently supported by cloud.io.
    """
    Invalid = 0     # Invalid data type
    Boolean = 1     # The attribute's value is of type boolean
    Integer = 2     # The attribute's value is of type short, int or long
    Number  = 3     # The attribute's value is of type float or double
    String  = 4     # The attribute's value is of type String

    def __init__(self, cloudioAttributeType):
        # Check if parameter is valid and yell otherwise
        if cloudioAttributeType in (self.Invalid, self.Boolean, self.Integer, self.Number, self.String):
            self._type = cloudioAttributeType
        else:
            raise InvalidCloudioAttributeTypeException(cloudioAttributeType)

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
        elif isinstance(rawType, str) or rawType in (types.StringType, types.UnicodeType):
            return cls.String
        else:
            return cls.Invalid

    @classmethod
    def fromRawTypeToString(cls, rawType):
        """Converts a standard type to a string.
        :return The type represented as a string.
        :type str
        """
        if isinstance(rawType, bool) or rawType == types.BooleanType:
            return 'Boolean'
        elif isinstance(rawType, types.IntType) or rawType == types.IntType:
            return 'Integer'
        elif isinstance(rawType, float) or rawType == types.FloatType:
            return 'Number'
        elif isinstance(rawType, str) or rawType in (types.StringType, types.UnicodeType):
            return 'String'
        else:
            return 'Invalid'

    @property
    def type(self):
        return self._type

    def toString(self):
        """Converts CloudioAttributeType to string.
        :return The type in string format
        :type str
        """
        if self._type == self.Boolean:
            return 'Boolean'
        elif self._type == self.Integer:
            return 'Integer'
        elif self._type == self.Number:
            return 'Number'
        elif self._type == self.String:
            return 'String'
        else:
            return 'Invalid'

    def __eq__(self, other):
        """== operator to work with cloudio attribute types."""
        if isinstance(other, int):
            return self._type == other
        else:
            raise InvalidCloudioAttributeTypeException(other)

    def __ne__(self, other):
        """!= operator to work with cloudio attribute types."""
        return not self.__eq__(other)