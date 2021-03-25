#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest
from cloudio.cloudio_attribute import CloudioAttribute

class TestCloudioAttribute(unittest.TestCase):

    def test_objectCreation(self):
        cloudioAttribute = CloudioAttribute()

    def test_setValueMethod(self):
        clA1 = CloudioAttribute()
        clA1.setValue(10000)
        self.assertTrue(clA1.get_value() == 10000)

        clA2 = CloudioAttribute()
        clA2.setValue('The description of anything...')
        self.assertTrue(clA2.get_value() == 'The description of anything...')

        # Check integrity
        self.assertTrue(clA1.get_value() == 10000)
