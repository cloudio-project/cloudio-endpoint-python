#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import logging
import shutil
import unittest

from cloudio.mqtt_helpers import MqttDefaultFilePersistence
from utils import path_helpers

class TestCloudioPersistanceFile(unittest.TestCase):
    """Tests persistence file feature.
    """

    log = logging.getLogger(__name__)

    def setUp(self):
        # Provide some updates as they are saved in MqttClientPersistence store
        self.keys = [
            'PendingUpdate-test-vacuum-cleaner;nodes;VacuumCleaner;objects;Parameters;attributes;setThroughput-1476111491023',
            'PendingUpdate-test-vacuum-cleaner;nodes;VacuumCleaner;objects;Parameters;attributes;setThroughput-1476163462733',
            'PendingUpdate-test-vacuum-cleaner;nodes;VacuumCleaner;objects;Parameters;attributes;setThroughput-1476163470654',
            'PendingUpdate-test-vacuum-cleaner;nodes;VacuumCleaner;objects;Parameters;attributes;setThroughput-1476163477170',
            'PendingUpdate-test-vacuum-cleaner;nodes;VacuumCleaner;objects;Parameters;attributes;setThroughput-1476163470153',
            'PendingUpdate-test-vacuum-cleaner;nodes;VacuumCleaner;objects;Parameters;attributes;setThroughput-1476163474666',
            'PendingUpdate-test-vacuum-cleaner;nodes;VacuumCleaner;objects;Parameters;attributes;setThroughput-1476163472659',
            'PendingUpdate-test-vacuum-cleaner;nodes;VacuumCleaner;objects;Parameters;attributes;setThroughput-1476163469652',
            'PendingUpdate-test-vacuum-cleaner;nodes;VacuumCleaner;objects;Parameters;attributes;setThroughput-1476163466257',
            'PendingUpdate-test-vacuum-cleaner;nodes;VacuumCleaner;objects;Parameters;attributes;setThroughput-1476163476169',
            'PendingUpdate-test-vacuum-cleaner;nodes;VacuumCleaner;objects;Parameters;attributes;setThroughput-1476163769338',
            'PendingUpdate-test-vacuum-cleaner;nodes;VacuumCleaner;objects;Parameters;attributes;setThroughput-1476163465383',
            'PendingUpdate-test-vacuum-cleaner;nodes;VacuumCleaner;objects;Parameters;attributes;setThroughput-1476163475166',
            'PendingUpdate-test-vacuum-cleaner;nodes;VacuumCleaner;objects;Parameters;attributes;setThroughput-1476163459950',
            'PendingUpdate-test-vacuum-cleaner;nodes;VacuumCleaner;objects;Parameters;attributes;setThroughput-1476163469152',
            'PendingUpdate-test-vacuum-cleaner;nodes;VacuumCleaner;objects;Parameters;attributes;setThroughput-1476163475667',
            'PendingUpdate-test-vacuum-cleaner;nodes;VacuumCleaner;objects;Parameters;attributes;setThroughput-1476163456301',
            'PendingUpdate-test-vacuum-cleaner;nodes;VacuumCleaner;objects;Parameters;attributes;setThroughput-1476163471155',
            'PendingUpdate-test-vacuum-cleaner;nodes;VacuumCleaner;objects;Parameters;attributes;setThroughput-1476163460861',
            'PendingUpdate-test-vacuum-cleaner;nodes;VacuumCleaner;objects;Parameters;attributes;setThroughput-1476163471656',
            'PendingUpdate-test-vacuum-cleaner;nodes;VacuumCleaner;objects;Parameters;attributes;setThroughput-1476163463614',
            'PendingUpdate-test-vacuum-cleaner;nodes;VacuumCleaner;objects;Parameters;attributes;setThroughput-1476163472157',
            'PendingUpdate-test-vacuum-cleaner;nodes;VacuumCleaner;objects;Parameters;attributes;setThroughput-1476163467255',
            'PendingUpdate-test-vacuum-cleaner;nodes;VacuumCleaner;objects;Parameters;attributes;setThroughput-1476163476669',
            ]

        self.persistenceFile = None

    def test_directoryCreation(self):
        #
        # Check default directory creation
        #
        directory = path_helpers.prettify(MqttDefaultFilePersistence.DEFAULT_DIRECTORY)
        self.persistenceFile = MqttDefaultFilePersistence()

        self.assertTrue(os.path.isdir(directory))   # Directory must now exist

        self.persistenceFile.open('theClientId', 'theUri')

        storageDirectory = os.path.join(directory, self.persistenceFile._perClientIdAndServerUriDirectory)
        self.assertTrue(os.path.isdir(storageDirectory))   # Sub-directory must now exist

        del self.persistenceFile

        #
        # Check custom directory creation
        #
        directory = path_helpers.prettify('~/mqtt-custom-persistence')

        self.persistenceFile = MqttDefaultFilePersistence(directory)
        self.assertTrue(os.path.isdir(directory))  # Directory must now exist

        # Tidy up on disk
        shutil.rmtree(directory)

    def test_storageDirectory(self):
        testPresistenceDirectory = path_helpers.prettify('~/mqtt-test-persistence')
        self.persistenceFile = MqttDefaultFilePersistence(testPresistenceDirectory)

        storageDirectoryName = 'theClientId-888-theServerUri'
        storageDirectory = os.path.join(self.persistenceFile._directory, storageDirectoryName)

        if os.path.exists(storageDirectory):
            os.rmdir(storageDirectory)
        self.assertTrue(not os.path.exists(storageDirectory))   # Directory must not exist before this test

        #
        # Check that '/', '\\', ':' and ' ' gets removed
        #
        self.persistenceFile.open('the Client/ Id-888', '\\the:Server:Uri ')

        # Check storage directory
        self.assertEqual(self.persistenceFile._perClientIdAndServerUriDirectory, storageDirectoryName)
        self.assertTrue(os.path.exists(storageDirectory))  # Directory must now exist

        # Tidy up on disk
        shutil.rmtree(testPresistenceDirectory)

