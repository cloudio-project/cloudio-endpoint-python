#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest
from cloudio.cloudio_object import CloudioObject

class CloudObjectDeriv(CloudioObject):
    b = 1.0
    c = CloudioObject()
    def __init__(self):
        self.a = 0
        CloudioObject.__init__(self)

class TestCloudioObject(unittest.TestCase):

    def test_objectCreation(self):
#        co1 = CloudioObject()
        c02 = CloudObjectDeriv()