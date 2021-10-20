# -*- coding: utf-8 -*-
from .cbor_format import CborMessageFormat
from .json_format import JsonMessageFormat


class MessageFormatFactory():
    """Provides the necessary MessageFormat converter in order to serialize/deserialize a message.

    Currently supported message formats are:
    - '{': json format
    - '0b101': cbor json format
    """

    formats = {}  # key: int, values: CloudioMessageFormat

    @classmethod
    def messageFormat(cls, messageFormatId):
        """Returns the MessageFormat needed to serialize/deserialize a message.
        :param messageFormatId The message format identifying the format of a message.
        """
        if messageFormatId in cls.formats:
            return cls.formats[messageFormatId]
        else:
            newFormat = None
            #123 = "{"
            if messageFormatId == 123:
                newFormat = JsonMessageFormat()
                cls.formats[messageFormatId] = newFormat
            elif (messageFormatId & 0b11100000) == 0b10100000:
                newFormat = CborMessageFormat()
                cls.formats[messageFormatId] = newFormat
            return newFormat
