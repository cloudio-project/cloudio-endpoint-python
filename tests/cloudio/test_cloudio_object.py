#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import unittest
from cloudio.endpoint.object import CloudioObject
from tests.cloudio.paths import update_working_directory

update_working_directory()  # Needed when: 'pipenv run python -m unittest tests/cloudio/{this_file}.py'


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
        co = CloudObjectSpec()

    def test_getAttributesMethod(self):
        co = CloudObjectSpec()

        attributes = co._internal.get_attributes()
        self.assertTrue(len(attributes) > 0)


if __name__ == '__main__':

    # Enable logging
    logging.basicConfig(format='%(asctime)s.%(msecs)03d - %(name)s - %(levelname)s - %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S',
                        level=logging.INFO)

    unittest.main()
