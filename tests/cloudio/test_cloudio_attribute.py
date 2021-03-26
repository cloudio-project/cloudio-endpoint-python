#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import unittest
from cloudio.cloudio_attribute import CloudioAttribute
from tests.cloudio.paths import update_working_directory

update_working_directory()  # Needed when: 'pipenv run python -m unittest tests/cloudio/{this_file}.py'


class TestCloudioAttribute(unittest.TestCase):

    def test_objectCreation(self):
        cloudioAttribute = CloudioAttribute()

    def test_setValueMethod(self):
        clA1 = CloudioAttribute()
        clA1.set_value(10000)
        self.assertTrue(clA1.get_value() == 10000)

        clA2 = CloudioAttribute()
        clA2.set_value('The description of anything...')
        self.assertTrue(clA2.get_value() == 'The description of anything...')

        # Check integrity
        self.assertTrue(clA1.get_value() == 10000)


if __name__ == '__main__':

    # Enable logging
    logging.basicConfig(format='%(asctime)s.%(msecs)03d - %(name)s - %(levelname)s - %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S',
                        level=logging.INFO)

    unittest.main()
