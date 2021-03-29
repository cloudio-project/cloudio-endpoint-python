# -*- coding: utf-8 -*-

class InvalidCloudioAttributeException(Exception):
    def __init__(self, value):

        if isinstance(value, str):
            message = value
            assert message != ''
            super(InvalidCloudioAttributeException, self).__init__(message)
        else:
            type = value
            super(InvalidCloudioAttributeException, self).__init__('Data type ' + str(type) + ' not supported by cloud.io!')