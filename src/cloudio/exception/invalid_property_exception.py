# -*- coding: utf-8 -*-

class InvalidPropertyException(Exception):
    def __init__(self, value):
        message = value
        assert message != ''
        super(InvalidPropertyException, self).__init__(message)