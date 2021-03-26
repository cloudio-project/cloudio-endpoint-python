#!/usr/bin/env python
# -*- coding: utf-8 -*-


import logging
import unittest
from cloudio.cloudio_runtime_node import CloudioRuntimeNode
from cloudio.cloudio_object import CloudioObject
from tests.cloudio.paths import update_working_directory

update_working_directory()  # Needed when: 'pipenv run python -m unittest tests/cloudio/{this_file}.py'


class CloudObjectSpec(CloudioObject):
    """A class derived from CloudioObject.
    """
    c = CloudioObject()

    def __init__(self):
        CloudioObject.__init__(self)


class TestCloudioRuntimeNode(unittest.TestCase):

    def test_addObject(self):
        rNode = CloudioRuntimeNode()
        rNode.add_object('firstObject', CloudObjectSpec)
        self.assertTrue(len(rNode.objects) == 1)

        # Check that only on object with the same name can
        # be added
        with self.assertRaises(AssertionError):
            rNode.add_object('firstObject', CloudObjectSpec)


if __name__ == '__main__':

    # Enable logging
    logging.basicConfig(format='%(asctime)s.%(msecs)03d - %(name)s - %(levelname)s - %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S',
                        level=logging.INFO)

    unittest.main()
