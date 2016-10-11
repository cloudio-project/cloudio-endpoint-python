#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time
import logging
import unittest
from connector.vacuumcleaner_connector import VacuumCleanerConnector
from model.vacuum_cleaner import VacuumCleaner
from client.vacuumcleaner_client import VacuumCleanerClient

class VacuumCleanerTestClient(VacuumCleanerClient):
    """Fake client that hooks into the reception flow to count received messages.
    """
    def __init__(self, configFile):
        VacuumCleanerClient.__init__(self, configFile)

        self.receivedMsgCounter = 0

    def _subscribeToUpdatedCommands(self):
        topic = u'@update/' + self._endPointName + '/#'
        print 'Subscribing to: ' + topic + ' messages'
        (result, mid) = self._client.subscribe(topic, 1)
        return True if result == self.MQTT_ERR_SUCCESS else False

    def onMessage(self, client, userdata, msg):
        if '@update' in msg.topic and 'setThroughput' in msg.topic:
            self.receivedMsgCounter += 1

class TestCloudioPersistanceMemory(unittest.TestCase):
    """Tests persistence memory feature.
    """

    log = logging.getLogger(__name__)

    def setUp(self):
        self.connector = VacuumCleanerConnector('test-vacuum-cleaner')  # Searches for file 'test-vacuum-cleaner.properties'
        self.cloudioEndPoint = self.connector.endpoint
        msgToSend = 100     # How many messages to send

        # Wait until connected to cloud.iO
        self.log.info('Waiting to connect endpoint to cloud.iO...')
        while not self.cloudioEndPoint.isOnline():
            time.sleep(0.2)

        # Load cloud.iO endpoint model from file
        self.log.info('Creating cloud.iO model...')
        self.connector.createModel('../config/vacuum-cleaner-model.xml')

        # Get the cloud.iO representation of the vaccum cleaner
        cloudioVacuumCleaner = self.connector.endpoint.getNode(u'VacuumCleaner')

        # Create vacuum cleaner object and associate cloud.iO reference to it
        self.vacuumCleaner = VacuumCleaner()
        self.vacuumCleaner.setCloudioBuddy(cloudioVacuumCleaner)

        # Create CloudioClient that sends the @set commands
        self.vacuumCleanerClient = VacuumCleanerTestClient('~/.config/cloud.io/client/vacuum-cleaner-client.config')
        self.log.info('Waiting to connect client to cloud.iO...')
        self.vacuumCleanerClient.waitUntilConnected()

        self.log.info('Setup finished')

    def tearDown(self):
        self.vacuumCleanerClient.close()
        self.connector.close()

    def test_persistanceMemory(self):
        # Create location stack and get the according cloud.iO attribute
        attrLocation = ['setThroughput', 'attributes', 'Parameters', 'objects']
        cloudioAttribute = self.cloudioEndPoint.getNode(u'VacuumCleaner').findAttribute(attrLocation)

        for i in range(0, self.msgToSend):
            print 'Sending update ' + str(i)
            self.cloudioEndPoint.attributeHasChangedByEndpoint(cloudioAttribute)
            time.sleep(.5)

        time.sleep(1)
        # Check if the update messages send are equal to the messages received by the client
        self.assertEqual(self.msgToSend, self.vacuumCleanerClient.receivedMsgCounter)


if __name__ == '__main__':

    # Enable logging
    logging.basicConfig(format='%(asctime)s.%(msecs)03d - %(name)s - %(levelname)s - %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S',
                        level=logging.INFO)

    unittest.main()