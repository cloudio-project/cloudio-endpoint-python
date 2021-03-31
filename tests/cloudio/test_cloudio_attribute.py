#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import unittest
from cloudio.common.utils import timestamp as timestamp_helpers
from cloudio.endpoint.attribute import CloudioAttribute
from cloudio.endpoint.interface.attribute_listener import CloudioAttributeListener
from cloudio.endpoint.exception.cloudio_modification_exception import CloudioModificationException
from cloudio.endpoint.exception.invalid_cloudio_attribute_exception import InvalidCloudioAttributeException
from tests.cloudio.paths import update_working_directory

update_working_directory()  # Needed when: 'pipenv run python -m unittest tests/cloudio/{this_file}.py'


class TestAttributeListener(CloudioAttributeListener):
    def attribute_has_changed(self, attribute):
        pass


class TestCloudioAttribute(unittest.TestCase):

    def test_objectCreation(self):
        cloudioAttribute = CloudioAttribute()
        cloudioAttribute.set_name('digger')

    def test_setValueMethod(self):
        clA1 = CloudioAttribute()
        clA1.set_value(10000)
        self.assertTrue(clA1.get_value() == 10000)

        clA2 = CloudioAttribute()
        clA2.set_value('The description of anything...')
        self.assertTrue(clA2.get_value() == 'The description of anything...')

        # Check integrity
        self.assertTrue(clA1.get_value() == 10000)

    def test_addRemoveListener(self):
        cAttr = CloudioAttribute()
        aListener01 = TestAttributeListener()
        timestamp = timestamp_helpers.get_time_in_milliseconds()

        cAttr.set_value_from_cloud(837602, timestamp)

        # Add and remove listener
        cAttr.add_listener(aListener01)
        self.assertTrue(len(cAttr._listeners) == 1)
        cAttr.remove_listener(aListener01)
        self.assertTrue(len(cAttr._listeners) == 0)

        # Give old timestamp
        cAttr.set_value_from_cloud(837603, timestamp - 1)

    def test_codeCoverage01(self):
        cAttr = CloudioAttribute()

        # Call get_type() without having it set
        cAttr.get_type()
        cAttr.get_type_as_string()

        # Set name twice
        cAttr.set_name('bananas')
        self.assertRaises(CloudioModificationException, cAttr.set_name, 'melons')

        # Set type twice
        cAttr.set_value(100)
        self.assertRaises(CloudioModificationException, cAttr.set_type, float)
        self.assertTrue(isinstance(cAttr.get_type(), int))

    def test_codeCoverage02(self):
        cAttr = CloudioAttribute()
        parent = CloudioAttribute()

        # Set bad type eq. 'dict'
        self.assertRaises(InvalidCloudioAttributeException, cAttr.set_type, dict)

        # Set parent twice
        cAttr.set_parent(parent)
        self.assertRaises(CloudioModificationException, cAttr.set_parent, parent)

        # Set constraint twice
        cAttr.set_constraint('static')
        self.assertRaises(CloudioModificationException, cAttr.set_constraint, 'static')


if __name__ == '__main__':

    # Enable logging
    logging.basicConfig(format='%(asctime)s.%(msecs)03d - %(name)s - %(levelname)s - %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S',
                        level=logging.INFO)

    unittest.main()
