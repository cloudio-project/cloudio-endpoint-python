#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import logging
import shutil
import unittest

from cloudio.mqtt_helpers import MqttDefaultFilePersistence
from utils import path_helpers
from cloudio.pending_update import PendingUpdate

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
        # Compare storage directory name
        self.assertEqual(self.persistenceFile._storageDirectory(), storageDirectory)
        # Directory must now exist
        self.assertTrue(os.path.exists(storageDirectory))

        # Tidy up on disk
        shutil.rmtree(testPresistenceDirectory)

    def test_putPersistable(self):
        testPresistenceDirectory = path_helpers.prettify('~/mqtt-test-persistence')
        self.persistenceFile = MqttDefaultFilePersistence(testPresistenceDirectory)

        self.persistenceFile.open('put-persistable', 'mqtt-test-server')

        data = self.keys[0] # Store the key as data
        self.persistenceFile.put(self.keys[0], data)

        keyFile = os.path.join(self.persistenceFile._storageDirectory(), self.keys[0])
        # Check if name of key file is right
        self.assertEqual(self.persistenceFile._keyFileName(self.keys[0]), keyFile)
        # Check if key file was created
        self.assertTrue(os.path.isfile(keyFile))
        # Check if file data is what we expect
        self.assertEqual(self._getFileContent(keyFile), data)

        # Tidy up on disk
        shutil.rmtree(testPresistenceDirectory)

    def _getFileContent(self, keyFile):
        """Returns the content of a key file.
        """
        with open(keyFile, mode='rb') as file:
            return file.read()

    def _getStorageFileNames(self):
        """Returns key file names stored in directory.
        :return The key file names.
        :type list
        """
        return next(os.walk(self.persistenceFile._storageDirectory()))[2]

    def test_putPersistableMultiple(self):
        keyNbrs = 3
        testPresistenceDirectory = path_helpers.prettify('~/mqtt-test-persistence')
        self.persistenceFile = MqttDefaultFilePersistence(testPresistenceDirectory)

        self.persistenceFile.open('put-persistable', 'mqtt-test-server')

        for idx, key in enumerate(self.keys):
            if idx >= keyNbrs:
                break
            data = key  # Store the key as data
            self.persistenceFile.put(key, data)

        fileNames = self._getStorageFileNames()

        self.assertEqual(keyNbrs, len(fileNames))

        # Tidy up on disk
        shutil.rmtree(testPresistenceDirectory)

    def test_putAndGetPersistable(self):
        keyNbrs = 10
        testPresistenceDirectory = path_helpers.prettify('~/mqtt-test-persistence')
        self.persistenceFile = MqttDefaultFilePersistence(testPresistenceDirectory)

        self.persistenceFile.open('put-persistable', 'mqtt-test-server')

        # Put some data
        for idx, key in enumerate(self.keys):
            if idx >= keyNbrs:
                break
            data = key  # Store the key as data
            self.persistenceFile.put(key, data)

        # Get data key[0]
        data = self.persistenceFile.get(self.keys[0])
        self.assertEqual(data.getHeaderBytes(), self.keys[0])

        # Get data key[9]
        data = self.persistenceFile.get(self.keys[9])
        self.assertEqual(data.getHeaderBytes(), self.keys[9])

        # Get data key[3]
        data = self.persistenceFile.get(self.keys[3])
        self.assertEqual(data.getHeaderBytes(), self.keys[3])

        # Get data key[8]
        data = self.persistenceFile.get(self.keys[8])
        self.assertEqual(data.getHeaderBytes(), self.keys[8])

        # Get none existing data
        data = self.persistenceFile.get(self.keys[keyNbrs + 1])
        self.assertEqual(data, None)

        # Tidy up on disk
        shutil.rmtree(testPresistenceDirectory)

    def test_putAndRemovePersistable(self):
        keyNbrs = 10
        testPresistenceDirectory = path_helpers.prettify('~/mqtt-test-persistence')
        self.persistenceFile = MqttDefaultFilePersistence(testPresistenceDirectory)

        self.persistenceFile.open('put-persistable', 'mqtt-test-server')

        # Put some data
        for idx, key in enumerate(self.keys):
            if idx >= keyNbrs:
                break
            data = key  # Store the key as data
            self.persistenceFile.put(key, data)

        # Remove in the middle
        self.persistenceFile.remove(self.keys[5])
        self.persistenceFile.remove(self.keys[6])
        # Check files left
        self.assertEqual(keyNbrs -2, len(self._getStorageFileNames()))

        # Remove first and last
        self.persistenceFile.remove(self.keys[0])
        self.persistenceFile.remove(self.keys[keyNbrs - 1])
        # Check files left
        self.assertEqual(keyNbrs - 4, len(self._getStorageFileNames()))

        # Check names of remaining key files
        fileNames = self._getStorageFileNames()
        self.assertTrue(self.keys[1] in fileNames)
        self.assertTrue(self.keys[2] in fileNames)
        self.assertTrue(self.keys[3] in fileNames)
        self.assertTrue(self.keys[4] in fileNames)
        self.assertTrue(self.keys[7] in fileNames)
        self.assertTrue(self.keys[8] in fileNames)

        # Tidy up on disk
        shutil.rmtree(testPresistenceDirectory)

    def test_containsKeys(self):
        keyNbrs = 5
        testPresistenceDirectory = path_helpers.prettify('~/mqtt-test-persistence')
        self.persistenceFile = MqttDefaultFilePersistence(testPresistenceDirectory)

        self.persistenceFile.open('put-persistable', 'mqtt-test-server')

        # Put some data
        for idx, key in enumerate(self.keys):
            if idx >= keyNbrs:
                break
            data = key  # Store the key as data
            self.persistenceFile.put(key, data)

        self.assertTrue(self.persistenceFile.containsKey(self.keys[0]))
        self.assertTrue(self.persistenceFile.containsKey(self.keys[1]))
        self.assertTrue(self.persistenceFile.containsKey(self.keys[3]))
        self.assertTrue(self.persistenceFile.containsKey(self.keys[4]))
        self.assertFalse(self.persistenceFile.containsKey(self.keys[5]))
        self.assertFalse(self.persistenceFile.containsKey(self.keys[10]))
        self.assertFalse(self.persistenceFile.containsKey(self.keys[20]))

        self.assertEqual(keyNbrs, len(self.persistenceFile.keys()))

        # Remove one key and check again
        self.assertTrue(self.persistenceFile.containsKey(self.keys[2]))     # Should be present
        self.persistenceFile.remove(self.keys[2])                           # Remove it
        self.assertFalse(self.persistenceFile.containsKey(self.keys[2]))    # Should be gone

        self.assertEqual(keyNbrs - 1, len(self.persistenceFile.keys()))

        # Get one key (not removing it) and check again
        self.assertTrue(self.persistenceFile.containsKey(self.keys[4]))     # Should be present
        self.persistenceFile.get(self.keys[4])                              # Get it
        self.assertTrue(self.persistenceFile.containsKey(self.keys[4]))     # Should be still there

        # Tidy up on disk
        shutil.rmtree(testPresistenceDirectory)

    def test_clearPresistence(self):
        keyNbrs = 5
        testPresistenceDirectory = path_helpers.prettify('~/mqtt-test-persistence')
        self.persistenceFile = MqttDefaultFilePersistence(testPresistenceDirectory)

        self.persistenceFile.open('put-persistable', 'mqtt-test-server')

        # Put some data
        for idx, key in enumerate(self.keys):
            if idx >= keyNbrs:
                break
            data = key  # Store the key as data
            self.persistenceFile.put(key, data)

        self.assertEqual(keyNbrs, len(self.persistenceFile.keys()))

        # Clear persistence
        self.persistenceFile.clear()

        self.assertEqual(0, len(self.persistenceFile.keys()))
        self.assertEqual(0, len(self._getStorageFileNames()))

        # Tidy up on disk
        shutil.rmtree(testPresistenceDirectory)

    def test_putPendingUpdate(self):
        testPresistenceDirectory = path_helpers.prettify('~/mqtt-test-persistence')
        self.persistenceFile = MqttDefaultFilePersistence(testPresistenceDirectory)

        self.persistenceFile.open('put-persistable', 'mqtt-test-server')

        self.persistenceFile.put(self.keys[8], PendingUpdate(self.keys[8]))

        self.assertEqual(self.persistenceFile.get(self.keys[8]).getHeaderBytes(), self.keys[8])