# -*- coding: utf-8 -*-

from .json_format import JsonMessageFormat
from .jsonzip_format import JsonZipMessageFormat


class MessageFormatFactory():
    """Provides the necessary MessageFormat converter in order to serialize/deserialize a message.

    Currently supported message formats are:
    - '{': json format
    - 'z': zipped json format
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
            if messageFormatId == '{':
                newFormat = JsonMessageFormat()
                cls.formats[messageFormatId] = newFormat
            if messageFormatId == 'z':
                newFormat = JsonZipMessageFormat()
                cls.formats[messageFormatId] = newFormat

            return newFormat
