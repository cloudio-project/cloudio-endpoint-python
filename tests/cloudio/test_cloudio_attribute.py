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
        self.assertTrue(clA1.getValue() == 10000)

        clA2 = CloudioAttribute()
        clA2.setValue('The description of anything...')
        self.assertTrue(clA2.getValue() == 'The description of anything...')

        # Check integrity
        self.assertTrue(clA1.getValue() == 10000)
