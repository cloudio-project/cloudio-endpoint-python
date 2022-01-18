#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import unittest
from cloudio.common.utils import timestamp_helpers as timestamp_helpers
from cloudio.endpoint.attribute import CloudioAttribute
from cloudio.endpoint.interface.attribute_listener import CloudioAttributeListener
from cloudio.endpoint.exception.cloudio_modification_exception import CloudioModificationException
from cloudio.endpoint.exception.invalid_cloudio_attribute_exception import InvalidCloudioAttributeException
from tests.cloudio.paths import update_working_directory

update_working_directory()  # Needed when: 'pipenv run python -m unittest tests/cloudio/{this_file}.py'


class TestAttributeListener(CloudioAttributeListener):
    def attribute_has_changed(self, attribute, from_cloud: bool):
        pass


class TestCloudioAttribute(unittest.TestCase):

    def test_objectCreation(self):
        cloudio_attribute = CloudioAttribute()
        cloudio_attribute.set_name('digger')

    def test_setValueMethod(self):
        cl_a1 = CloudioAttribute()
        cl_a1.set_value(10000)
        self.assertTrue(cl_a1.get_value() == 10000)

        cl_a2 = CloudioAttribute()
        cl_a2.set_value('The description of anything...')
        self.assertTrue(cl_a2.get_value() == 'The description of anything...')

        # Check integrity
        self.assertTrue(cl_a1.get_value() == 10000)

    def test_addRemoveListener(self):
        c_attr = CloudioAttribute()
        a_listener01 = TestAttributeListener()
        timestamp = timestamp_helpers.get_time_in_milliseconds()

        c_attr.set_value_from_cloud(837602, timestamp)

        # Add and remove listener
        c_attr.add_listener(a_listener01)
        self.assertTrue(len(c_attr._listeners) == 1)
        c_attr.remove_listener(a_listener01)
        self.assertTrue(len(c_attr._listeners) == 0)

        # Give old timestamp
        c_attr.set_value_from_cloud(837603, timestamp - 1)

    def test_codeCoverage01(self):
        c_attr = CloudioAttribute()

        # Call get_type() without having it set
        c_attr.get_type()
        c_attr.get_type_as_string()

        # Set name twice
        c_attr.set_name('bananas')
        self.assertRaises(CloudioModificationException, c_attr.set_name, 'melons')

        # Set type twice
        c_attr.set_value(100)
        self.assertRaises(CloudioModificationException, c_attr.set_type, float)
        self.assertTrue(isinstance(c_attr.get_type(), int))

    def test_codeCoverage02(self):
        c_attr = CloudioAttribute()
        parent = CloudioAttribute()

        # Set bad type eq. 'dict'
        self.assertRaises(InvalidCloudioAttributeException, c_attr.set_type, dict)

        # Set parent twice
        c_attr.set_parent(parent)
        self.assertRaises(CloudioModificationException, c_attr.set_parent, parent)

        # Set constraint twice
        c_attr.set_constraint('static')
        self.assertRaises(CloudioModificationException, c_attr.set_constraint, 'static')


if __name__ == '__main__':
    # Enable logging
    logging.basicConfig(format='%(asctime)s.%(msecs)03d - %(name)s - %(levelname)s - %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S',
                        level=logging.INFO)

    unittest.main()
