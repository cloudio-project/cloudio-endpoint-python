# -*- coding: utf-8 -*-

class CloudioModificationException(Exception):
    def __init__(self, message):
        super(CloudioModificationException, self).__init__(message)