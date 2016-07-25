#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest
from cloudio.cloudio_runtime_node import CloudioRuntimeNode
from cloudio.cloudio_object import CloudioObject

class CloudObjectSpec(CloudioObject):
    """A class derived from CloudioObject.
    """
    c = CloudioObject()
    def __init__(self):
        CloudioObject.__init__(self)

class TestCloudioRuntimeNode(unittest.TestCase):

    def test_addObject(self):
        rNode = CloudioRuntimeNode()
        rNode.addObject('firstObject', CloudObjectSpec)
        self.assertTrue(len(rNode.objects) == 1)

        # Check that only on object with the same name can
        # be added
        with self.assertRaises(AssertionError):
            rNode.addObject('firstObject', CloudObjectSpec)


if __name__ == '__main__':
    unittest.main()
