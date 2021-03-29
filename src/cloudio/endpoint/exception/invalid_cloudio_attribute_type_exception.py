# -*- coding: utf-8 -*-

class InvalidCloudioAttributeTypeException(Exception):
    def __init__(self, type):
        super(InvalidCloudioAttributeTypeException, self).__init__(str(type) + ' is not a valid cloud.io attribute type!')