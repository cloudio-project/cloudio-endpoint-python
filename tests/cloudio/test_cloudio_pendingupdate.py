#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import unittest

from cloudio.pending_update import PendingUpdate
from tests.cloudio.paths import update_working_directory

update_working_directory()  # Needed when: 'pipenv run python -m unittest tests/cloudio/{this_file}.py'


class TestCloudioPendingUpdate(unittest.TestCase):
    """Tests PendingUpdate class.
    """

    log = logging.getLogger(__name__)

    def setUp(self):
        # Provide some updates as they are saved in MqttClientPersistence store
        self.keys = ['PendingUpdate-test-vacuum-cleaner;nodes;VacuumCleaner;objects;Parameters;attributes'
                     ';set_throughput-1476111491023',
                     'PendingUpdate-test-vacuum-cleaner;nodes;VacuumCleaner;objects;Parameters;attributes'
                     ';set_throughput-1476163462733',
                     'PendingUpdate-test-vacuum-cleaner;nodes;VacuumCleaner;objects;Parameters;attributes'
                     ';set_throughput-1476163470654',
                     'PendingUpdate-test-vacuum-cleaner;nodes;VacuumCleaner;objects;Parameters;attributes'
                     ';set_throughput-1476163477170',
                     'PendingUpdate-test-vacuum-cleaner;nodes;VacuumCleaner;objects;Parameters;attributes'
                     ';set_throughput-1476163470153',
                     'PendingUpdate-test-vacuum-cleaner;nodes;VacuumCleaner;objects;Parameters;attributes'
                     ';set_throughput-1476163474666',
                     'PendingUpdate-test-vacuum-cleaner;nodes;VacuumCleaner;objects;Parameters;attributes'
                     ';set_throughput-1476163472659',
                     'PendingUpdate-test-vacuum-cleaner;nodes;VacuumCleaner;objects;Parameters;attributes'
                     ';set_throughput-1476163469652',
                     'PendingUpdate-test-vacuum-cleaner;nodes;VacuumCleaner;objects;Parameters;attributes'
                     ';set_throughput-1476163466257',
                     'PendingUpdate-test-vacuum-cleaner;nodes;VacuumCleaner;objects;Parameters;attributes'
                     ';set_throughput-1476163476169',
                     'PendingUpdate-test-vacuum-cleaner;nodes;VacuumCleaner;objects;Parameters;attributes'
                     ';set_throughput-1476163769338',
                     'PendingUpdate-test-vacuum-cleaner;nodes;VacuumCleaner;objects;Parameters;attributes'
                     ';set_throughput-1476163465383',
                     'PendingUpdate-test-vacuum-cleaner;nodes;VacuumCleaner;objects;Parameters;attributes'
                     ';set_throughput-1476163475166',
                     'PendingUpdate-test-vacuum-cleaner;nodes;VacuumCleaner;objects;Parameters;attributes'
                     ';set_throughput-1476163459950',
                     'PendingUpdate-test-vacuum-cleaner;nodes;VacuumCleaner;objects;Parameters;attributes'
                     ';set_throughput-1476163469152',
                     'PendingUpdate-test-vacuum-cleaner;nodes;VacuumCleaner;objects;Parameters;attributes'
                     ';set_throughput-1476163475667',
                     'PendingUpdate-test-vacuum-cleaner;nodes;VacuumCleaner;objects;Parameters;attributes'
                     ';set_throughput-1476163456301',
                     'PendingUpdate-test-vacuum-cleaner;nodes;VacuumCleaner;objects;Parameters;attributes'
                     ';set_throughput-1476163471155',
                     'PendingUpdate-test-vacuum-cleaner;nodes;VacuumCleaner;objects;Parameters;attributes'
                     ';set_throughput-1476163460861',
                     'PendingUpdate-test-vacuum-cleaner;nodes;VacuumCleaner;objects;Parameters;attributes'
                     ';set_throughput-1476163471656',
                     'PendingUpdate-test-vacuum-cleaner;nodes;VacuumCleaner;objects;Parameters;attributes'
                     ';set_throughput-1476163463614',
                     'PendingUpdate-test-vacuum-cleaner;nodes;VacuumCleaner;objects;Parameters;attributes'
                     ';set_throughput-1476163472157',
                     'PendingUpdate-test-vacuum-cleaner;nodes;VacuumCleaner;objects;Parameters;attributes'
                     ';set_throughput-1476163467255',
                     'PendingUpdate-test-vacuum-cleaner;nodes;VacuumCleaner;objects;Parameters;attributes'
                     ';set_throughput-1476163476669',
                     ]

    def test_pendingUpdateDecoding(self):
        """Tests the getUuidFromPersistenceKey() method of the PendingUpdate class.
        """
        compUuid = 'test-vacuum-cleaner/nodes/VacuumCleaner/objects/Parameters/attributes/set_throughput'
        for key in self.keys:
            uuid = PendingUpdate.get_uuid_from_persistence_key(key)
            self.assertEqual(uuid, compUuid)


if __name__ == '__main__':

    # Enable logging
    logging.basicConfig(format='%(asctime)s.%(msecs)03d - %(name)s - %(levelname)s - %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S',
                        level=logging.INFO)

    unittest.main()
