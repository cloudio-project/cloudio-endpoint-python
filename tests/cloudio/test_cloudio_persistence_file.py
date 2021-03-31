#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import logging
import shutil
import unittest

from tests.cloudio.paths import update_working_directory
from cloudio.common.utils import path_helpers
from cloudio.common.mqtt import MqttDefaultFilePersistence
from cloudio.common.mqtt import PendingUpdate

update_working_directory()  # Needed when: 'pipenv run python -m unittest tests/cloudio/{this_file}.py'


class TestCloudioPersistenceFile(unittest.TestCase):
    """Tests persistence file feature.
    """

    log = logging.getLogger(__name__)

    def setUp(self):
        # Provide some updates as they are saved in MqttClientPersistence store
        self.keys = [
            'PendingUpdate-test-vacuum-cleaner;nodes;VacuumCleaner;objects;Parameters;attributes;'
            'set_throughput-1476111491023',
            'PendingUpdate-test-vacuum-cleaner;nodes;VacuumCleaner;objects;Parameters;attributes;'
            'set_throughput-1476163462733',
            'PendingUpdate-test-vacuum-cleaner;nodes;VacuumCleaner;objects;Parameters;attributes;'
            'set_throughput-1476163470654',
            'PendingUpdate-test-vacuum-cleaner;nodes;VacuumCleaner;objects;Parameters;attributes;'
            'set_throughput-1476163477170',
            'PendingUpdate-test-vacuum-cleaner;nodes;VacuumCleaner;objects;Parameters;attributes;'
            'set_throughput-1476163470153',
            'PendingUpdate-test-vacuum-cleaner;nodes;VacuumCleaner;objects;Parameters;attributes;'
            'set_throughput-1476163474666',
            'PendingUpdate-test-vacuum-cleaner;nodes;VacuumCleaner;objects;Parameters;attributes;'
            'set_throughput-1476163472659',
            'PendingUpdate-test-vacuum-cleaner;nodes;VacuumCleaner;objects;Parameters;attributes;'
            'set_throughput-1476163469652',
            'PendingUpdate-test-vacuum-cleaner;nodes;VacuumCleaner;objects;Parameters;attributes;'
            'set_throughput-1476163466257',
            'PendingUpdate-test-vacuum-cleaner;nodes;VacuumCleaner;objects;Parameters;attributes;'
            'set_throughput-1476163476169',
            'PendingUpdate-test-vacuum-cleaner;nodes;VacuumCleaner;objects;Parameters;attributes;'
            'set_throughput-1476163769338',
            'PendingUpdate-test-vacuum-cleaner;nodes;VacuumCleaner;objects;Parameters;attributes;'
            'set_throughput-1476163465383',
            'PendingUpdate-test-vacuum-cleaner;nodes;VacuumCleaner;objects;Parameters;attributes;'
            'set_throughput-1476163475166',
            'PendingUpdate-test-vacuum-cleaner;nodes;VacuumCleaner;objects;Parameters;attributes;'
            'set_throughput-1476163459950',
            'PendingUpdate-test-vacuum-cleaner;nodes;VacuumCleaner;objects;Parameters;attributes;'
            'set_throughput-1476163469152',
            'PendingUpdate-test-vacuum-cleaner;nodes;VacuumCleaner;objects;Parameters;attributes;'
            'set_throughput-1476163475667',
            'PendingUpdate-test-vacuum-cleaner;nodes;VacuumCleaner;objects;Parameters;attributes;'
            'set_throughput-1476163456301',
            'PendingUpdate-test-vacuum-cleaner;nodes;VacuumCleaner;objects;Parameters;attributes;'
            'set_throughput-1476163471155',
            'PendingUpdate-test-vacuum-cleaner;nodes;VacuumCleaner;objects;Parameters;attributes;'
            'set_throughput-1476163460861',
            'PendingUpdate-test-vacuum-cleaner;nodes;VacuumCleaner;objects;Parameters;attributes;'
            'set_throughput-1476163471656',
            'PendingUpdate-test-vacuum-cleaner;nodes;VacuumCleaner;objects;Parameters;attributes;'
            'set_throughput-1476163463614',
            'PendingUpdate-test-vacuum-cleaner;nodes;VacuumCleaner;objects;Parameters;attributes;'
            'set_throughput-1476163472157',
            'PendingUpdate-test-vacuum-cleaner;nodes;VacuumCleaner;objects;Parameters;attributes;'
            'set_throughput-1476163467255',
            'PendingUpdate-test-vacuum-cleaner;nodes;VacuumCleaner;objects;Parameters;attributes;'
            'set_throughput-1476163476669',
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

        storage_directory = os.path.join(directory, self.persistenceFile._per_client_id_and_server_uri_directory)
        self.assertTrue(os.path.isdir(storage_directory))   # Sub-directory must now exist

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
        test_presistence_directory = path_helpers.prettify('~/mqtt-test-persistence')
        self.persistenceFile = MqttDefaultFilePersistence(test_presistence_directory)

        storage_directory_name = 'theClientId-888-theServerUri'
        storage_directory = os.path.join(self.persistenceFile._directory, storage_directory_name)

        if os.path.exists(storage_directory):
            os.rmdir(storage_directory)
        self.assertTrue(not os.path.exists(storage_directory))   # Directory must not exist before this test

        #
        # Check that '/', '\\', ':' and ' ' gets removed
        #
        self.persistenceFile.open('the Client/ Id-888', '\\the:Server:Uri ')

        # Check storage directory
        self.assertEqual(self.persistenceFile._per_client_id_and_server_uri_directory, storage_directory_name)
        # Compare storage directory name
        self.assertEqual(self.persistenceFile._storage_directory(), storage_directory)
        # Directory must now exist
        self.assertTrue(os.path.exists(storage_directory))

        # Tidy up on disk
        shutil.rmtree(test_presistence_directory)

    def test_putPersistable(self):
        test_persistence_directory = path_helpers.prettify('~/mqtt-test-persistence')
        self.persistenceFile = MqttDefaultFilePersistence(test_persistence_directory)

        self.persistenceFile.open('put-persistable', 'mqtt-test-server')

        data = self.keys[0]  # Store the key as data
        self.persistenceFile.put(self.keys[0], data)

        key_file = os.path.join(self.persistenceFile._storage_directory(), self.keys[0])
        # Check if name of key file is right
        self.assertEqual(self.persistenceFile._key_file_name(self.keys[0]), key_file)
        # Check if key file was created
        self.assertTrue(os.path.isfile(key_file))
        # Check if file data is what we expect
        self.assertEqual(self._getFileContent(key_file), data)

        # Tidy up on disk
        shutil.rmtree(test_persistence_directory)

    @staticmethod
    def _getFileContent(key_file):
        """Returns the content of a key file.
        """
        with open(key_file, mode='r') as file:
            return file.read()

    def _getStorageFileNames(self):
        """Returns key file names stored in directory.
        :return The key file names.
        """
        return next(os.walk(self.persistenceFile._storage_directory()))[2]

    def test_putPersistableMultiple(self):
        key_nbrs = 3
        test_presistence_directory = path_helpers.prettify('~/mqtt-test-persistence')
        self.persistenceFile = MqttDefaultFilePersistence(test_presistence_directory)

        self.persistenceFile.open('put-persistable', 'mqtt-test-server')

        for idx, key in enumerate(self.keys):
            if idx >= key_nbrs:
                break
            data = key  # Store the key as data
            self.persistenceFile.put(key, data)

        file_names = self._getStorageFileNames()

        self.assertEqual(key_nbrs, len(file_names))

        # Tidy up on disk
        shutil.rmtree(test_presistence_directory)

    def test_putAndGetPersistable(self):
        key_nbrs = 10
        test_presistence_directory = path_helpers.prettify('~/mqtt-test-persistence')
        self.persistenceFile = MqttDefaultFilePersistence(test_presistence_directory)

        self.persistenceFile.open('put-persistable', 'mqtt-test-server')

        # Put some data
        for idx, key in enumerate(self.keys):
            if idx >= key_nbrs:
                break
            data = key  # Store the key as data
            self.persistenceFile.put(key, data)

        # Get data key[0]
        data = self.persistenceFile.get(self.keys[0])
        self.assertEqual(data.get_data(), self.keys[0])

        # Get data key[9]
        data = self.persistenceFile.get(self.keys[9])
        self.assertEqual(data.get_data(), self.keys[9])

        # Get data key[3]
        data = self.persistenceFile.get(self.keys[3])
        self.assertEqual(data.get_data(), self.keys[3])

        # Get data key[8]
        data = self.persistenceFile.get(self.keys[8])
        self.assertEqual(data.get_data(), self.keys[8])

        # Get none existing data
        data = self.persistenceFile.get(self.keys[key_nbrs + 1])
        self.assertEqual(data, None)

        # Tidy up on disk
        shutil.rmtree(test_presistence_directory)

    def test_putAndRemovePersistable(self):
        key_nbrs = 10
        test_presistence_directory = path_helpers.prettify('~/mqtt-test-persistence')
        self.persistenceFile = MqttDefaultFilePersistence(test_presistence_directory)

        self.persistenceFile.open('put-persistable', 'mqtt-test-server')

        # Put some data
        for idx, key in enumerate(self.keys):
            if idx >= key_nbrs:
                break
            data = key  # Store the key as data
            self.persistenceFile.put(key, data)

        # Remove in the middle
        self.persistenceFile.remove(self.keys[5])
        self.persistenceFile.remove(self.keys[6])
        # Check files left
        self.assertEqual(key_nbrs - 2, len(self._getStorageFileNames()))

        # Remove first and last
        self.persistenceFile.remove(self.keys[0])
        self.persistenceFile.remove(self.keys[key_nbrs - 1])
        # Check files left
        self.assertEqual(key_nbrs - 4, len(self._getStorageFileNames()))

        # Check names of remaining key files
        file_names = self._getStorageFileNames()
        self.assertTrue(self.keys[1] in file_names)
        self.assertTrue(self.keys[2] in file_names)
        self.assertTrue(self.keys[3] in file_names)
        self.assertTrue(self.keys[4] in file_names)
        self.assertTrue(self.keys[7] in file_names)
        self.assertTrue(self.keys[8] in file_names)

        # Tidy up on disk
        shutil.rmtree(test_presistence_directory)

    def test_containsKeys(self):
        key_nbrs = 5
        test_presistence_directory = path_helpers.prettify('~/mqtt-test-persistence')
        self.persistenceFile = MqttDefaultFilePersistence(test_presistence_directory)

        self.persistenceFile.open('put-persistable', 'mqtt-test-server')

        # Put some data
        for idx, key in enumerate(self.keys):
            if idx >= key_nbrs:
                break
            data = key  # Store the key as data
            self.persistenceFile.put(key, data)

        self.assertTrue(self.persistenceFile.contains_key(self.keys[0]))
        self.assertTrue(self.persistenceFile.contains_key(self.keys[1]))
        self.assertTrue(self.persistenceFile.contains_key(self.keys[3]))
        self.assertTrue(self.persistenceFile.contains_key(self.keys[4]))
        self.assertFalse(self.persistenceFile.contains_key(self.keys[5]))
        self.assertFalse(self.persistenceFile.contains_key(self.keys[10]))
        self.assertFalse(self.persistenceFile.contains_key(self.keys[20]))

        self.assertEqual(key_nbrs, len(self.persistenceFile.keys()))

        # Remove one key and check again
        self.assertTrue(self.persistenceFile.contains_key(self.keys[2]))     # Should be present
        self.persistenceFile.remove(self.keys[2])                           # Remove it
        self.assertFalse(self.persistenceFile.contains_key(self.keys[2]))    # Should be gone

        self.assertEqual(key_nbrs - 1, len(self.persistenceFile.keys()))

        # Get one key (not removing it) and check again
        self.assertTrue(self.persistenceFile.contains_key(self.keys[4]))     # Should be present
        self.persistenceFile.get(self.keys[4])                              # Get it
        self.assertTrue(self.persistenceFile.contains_key(self.keys[4]))     # Should be still there

        # Tidy up on disk
        shutil.rmtree(test_presistence_directory)

    def test_clearPersistence(self):
        key_nbrs = 5
        test_presistence_directory = path_helpers.prettify('~/mqtt-test-persistence')
        self.persistenceFile = MqttDefaultFilePersistence(test_presistence_directory)

        self.persistenceFile.open('put-persistable', 'mqtt-test-server')

        # Put some data
        for idx, key in enumerate(self.keys):
            if idx >= key_nbrs:
                break
            data = key  # Store the key as data
            self.persistenceFile.put(key, data)

        self.assertEqual(key_nbrs, len(self.persistenceFile.keys()))

        # Clear persistence
        self.persistenceFile.clear()

        self.assertEqual(0, len(self.persistenceFile.keys()))
        self.assertEqual(0, len(self._getStorageFileNames()))

        # Tidy up on disk
        shutil.rmtree(test_presistence_directory)

    def test_putPendingUpdate(self):
        test_persistence_directory = path_helpers.prettify('~/mqtt-test-persistence')
        self.persistenceFile = MqttDefaultFilePersistence(test_persistence_directory)

        self.persistenceFile.open('put-persistable', 'mqtt-test-server')

        self.persistenceFile.put(self.keys[8], PendingUpdate(self.keys[8]))

        self.assertEqual(self.persistenceFile.get(self.keys[8]).get_data(), self.keys[8])


if __name__ == '__main__':

    # Enable logging
    logging.basicConfig(format='%(asctime)s.%(msecs)03d - %(name)s - %(levelname)s - %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S',
                        level=logging.INFO)

    unittest.main()
