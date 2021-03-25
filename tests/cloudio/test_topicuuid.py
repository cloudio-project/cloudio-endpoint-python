#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest
from cloudio.interface.uuid import Uuid
from cloudio.topicuuid import TopicUuid

class TestTopicUuid(unittest.TestCase):

    def test_objectCreation(self):
        topicUuid = TopicUuid()

    def test_checkAbstractClassRelation(self):
        # TopicUuid needs to implement the Uuid interface
        self.assertTrue(issubclass(TopicUuid, Uuid))

    def test_checkAbstractClassInstantiation(self):
        topicUuid = TopicUuid()
        # TopicUuid needs to implement the interface
        self.assertTrue(isinstance(topicUuid, Uuid))

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
        # All other sould return false
        self.assertFalse(t1.equals(''))
        self.assertFalse(t1.equals('other topic'))
        self.assertFalse(t1.equals('Some topic'))

        # Now set t2 to the same topic as t1
        t2.topic = 'Some topic'
        self.assertTrue(t1.equals(t2))
        self.assertTrue(t2.equals(t1))

if __name__ == '__main__':
    unittest.main()
