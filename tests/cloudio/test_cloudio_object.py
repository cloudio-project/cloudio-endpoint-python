#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest
from cloudio.cloudio_object import CloudioObject
from cloudio.cloudio_attribute import CloudioAttribute

class CloudObjectSpec(CloudioObject):
    """A class derived from CloudioObject.

    Used for testing.
    """
    b = True
    f = 1.1
    c = CloudioObject()
    def __init__(self):
        self.a = 0
        CloudioObject.__init__(self)

class TestCloudioObject(unittest.TestCase):

    def test_objectCreation(self):
#        co1 = CloudioObject()
        c02 = CloudObjectSpec()

    def test_getAttributesMethod(self):
        co = CloudObjectSpec()

        attributes = co._internal.getAttributes()
        self.assertTrue(len(attributes) > 0)

        #for attribute in attributes:
        #        print(attribute)