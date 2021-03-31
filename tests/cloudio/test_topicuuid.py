#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import unittest
from cloudio.endpoint.interface.uuid import CloudioUuid
from cloudio.endpoint.topicuuid import TopicUuid
from tests.cloudio.paths import update_working_directory

update_working_directory()  # Needed when: 'pipenv run python -m unittest tests/cloudio/{this_file}.py'


class TestTopicUuid(unittest.TestCase):

    def test_objectCreation(self):
        topicUuid = TopicUuid()

    def test_checkAbstractClassRelation(self):
        # TopicUuid needs to implement the CloudioUuid interface
        self.assertTrue(issubclass(TopicUuid, CloudioUuid))

    def test_checkAbstractClassInstantiation(self):
        topicUuid = TopicUuid()
        # TopicUuid needs to implement the interface
        self.assertTrue(isinstance(topicUuid, CloudioUuid))

    def test_isValidMethod(self):
        t1 = TopicUuid()
        self.assertFalse(t1.is_valid())
        t1.topic = ''
        self.assertFalse(t1.is_valid())
        t1.topic = 'Some text'
        self.assertTrue(t1.is_valid())

    def test_equalsMethod(self):
        t1 = TopicUuid()
        t2 = TopicUuid()
        t1.topic = 'Some topic'
        t2.topic = 'Some topic - and more'
        self.assertFalse(t1.equals(t2))     # Check different
        self.assertTrue(t1.equals(t1))      # Check equal(self)

        # Only TopicUuid as parameter are allowed.
        # All other should return false
        self.assertFalse(t1.equals(''))
        self.assertFalse(t1.equals('other topic'))
        self.assertFalse(t1.equals('Some topic'))

        # Now set t2 to the same topic as t1
        t2.topic = 'Some topic'
        self.assertTrue(t1.equals(t2))
        self.assertTrue(t2.equals(t1))


if __name__ == '__main__':

    # Enable logging
    logging.basicConfig(format='%(asctime)s.%(msecs)03d - %(name)s - %(levelname)s - %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S',
                        level=logging.INFO)

    unittest.main()
