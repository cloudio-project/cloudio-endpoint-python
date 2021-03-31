#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time
import logging
import json
import unittest

from tests.cloudio.paths import update_working_directory
from connector.vacuumcleaner_connector import VacuumCleanerConnector
from model.vacuum_cleaner import VacuumCleaner
from client.vacuumcleaner_client import VacuumCleanerClient

update_working_directory()  # Needed when: 'pipenv run python -m unittest tests/cloudio/{this_file}.py'

VACUUM_CLEANER_NAME = 'VacuumCleanerEndpoint'


class VacuumCleanerTestClient(VacuumCleanerClient):
    """Fake client that hooks into the reception flow to count received messages.
    """
    def __init__(self, config_file, msgs_to_receive):
        VacuumCleanerClient.__init__(self, config_file)

        self.msgsToReceive = msgs_to_receive    # Amount of message the client should receive
        self.receivedMsgCounter = 0             # Received messages counter
        self.rxedMessages = {}

    def _subscribe_to_updated_commands(self):
        topic = '@update/' + self._endPointName + '/#'
        print('Subscribing to: ' + topic + ' messages')
        (result, mid) = self._client.subscribe(topic, 1)
        return True if result == self.MQTT_ERR_SUCCESS else False

    def on_message(self, client, userdata, msg):
        # The value of the received messages should go from 0 to msgs_to_receive
        # Values received are stored in rxedMessages
        if '@update' in msg.topic and 'set_throughput' in msg.topic:
            self.receivedMsgCounter += 1
            value = json.loads(msg.payload)['value']
            self.rxedMessages[value] = value
            # TODO What about multiples?

    def show_messages_summary(self):
        if self.receivedMsgCounter < self.msgsToReceive:
            for index in range(0, self.msgsToReceive):
                if index not in self.rxedMessages:
                    print('Error: Missing message %d' % index)
        elif self.receivedMsgCounter == self.msgsToReceive:
            print('The right amount of messages was received')
        else:
            print('Error: More messages then expected received!')


class TestCloudioPersistenceMemory(unittest.TestCase):
    """Tests persistence memory feature.
    """

    log = logging.getLogger(__name__)

    def setUp(self):
        self.connector = VacuumCleanerConnector(VACUUM_CLEANER_NAME)  # Searches file '<VACUUM_CLEANER_NAME>.properties'
        self.cloudioEndPoint = self.connector.endpoint
        self.msgToSend = 70     # How many messages to send

        # Wait until connected to cloud.iO
        self.log.info('Waiting to connect endpoint to cloud.iO...')
        while not self.cloudioEndPoint.is_online():
            time.sleep(0.2)

        # Load cloud.iO endpoint model from file
        self.log.info('Creating cloud.iO model...')
        self.connector.createModel('../config/vacuum-cleaner-model.xml')

        # Get the cloud.iO representation of the vacuum cleaner
        cloudio_vacuum_cleaner = self.connector.endpoint.get_node(VACUUM_CLEANER_NAME)

        # Create vacuum cleaner object and associate cloud.iO reference to it
        self.vacuumCleaner = VacuumCleaner()
        self.vacuumCleaner.set_cloudio_buddy(cloudio_vacuum_cleaner)

        # Create CloudioClient that sends the @set commands
        self.vacuumCleanerClient = VacuumCleanerTestClient('~/.config/cloud.io/client/vacuum-cleaner-client.config',
                                                           self.msgToSend)
        self.log.info('Waiting to connect client to cloud.iO...')
        self.vacuumCleanerClient.wait_until_connected()

        self.log.info('Setup finished')

    def tearDown(self):
        self.vacuumCleanerClient.close()
        self.connector.close()

    def test_persistenceMemory(self):
        # Create location stack and get the according cloud.iO attribute
        attr_location = ['set_throughput', 'attributes', 'Parameters', 'objects']
        cloudio_attribute = self.cloudioEndPoint.get_node(VACUUM_CLEANER_NAME).find_attribute(attr_location)

        for i in range(0, self.msgToSend):
            print('Sending update ' + str(i + 1))
            cloudio_attribute.set_value(i)
            time.sleep(.5)

        time.sleep(1)
        # Show summary about received messages
        self.vacuumCleanerClient.show_messages_summary()
        # Check if the update messages send are equal to the messages received by the client
        self.assertEqual(self.msgToSend, self.vacuumCleanerClient.receivedMsgCounter)


if __name__ == '__main__':

    # Enable logging
    logging.basicConfig(format='%(asctime)s.%(msecs)03d - %(name)s - %(levelname)s - %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S',
                        level=logging.INFO)

    unittest.main()
