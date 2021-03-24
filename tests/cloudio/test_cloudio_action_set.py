#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time
import logging
import unittest
from connector.vacuumcleaner_connector import VacuumCleanerConnector
from model.vacuum_cleaner import VacuumCleaner
from client.vacuumcleaner_client import VacuumCleanerClient

VACUUM_CLEANER_NAME = 'VacuumCleanerEndpoint'


class TestCloudioSetAction(unittest.TestCase):
    """Tests @set action with various attributes.
    """

    log = logging.getLogger(__name__)

    def setUp(self):
        self.connector = VacuumCleanerConnector(VACUUM_CLEANER_NAME)  # Searches for '<VACUUM_CLEANER_NAME>.properties'
        self.cloudioEndPoint = self.connector.endpoint

        # Wait until connected to cloud.iO
        self.log.info('Waiting to connect endpoint to cloud.iO...')
        while not self.cloudioEndPoint.isOnline():
            time.sleep(0.2)

        # Load cloud.iO endpoint model from file
        self.log.info('Creating cloud.iO model...')
        self.connector.createModel('../config/vacuum-cleaner-model.xml')

        # Get the cloud.iO representation of the vacuum cleaner
        cloudio_vacuum_cleaner = self.connector.endpoint.getNode(VACUUM_CLEANER_NAME)

        # Create vacuum cleaner object and associate cloud.iO reference to it
        self.vacuumCleaner = VacuumCleaner()
        self.vacuumCleaner.setCloudioBuddy(cloudio_vacuum_cleaner)

        # Create CloudioClient that sends the @set commands
        self.vacuumCleanerClient = VacuumCleanerClient('~/.config/cloud.io/client/vacuum-cleaner-client.config')
        self.log.info('Waiting to connect client to cloud.iO...')
        self.vacuumCleanerClient.waitUntilConnected()

        self.log.info('Setup finished')

    def tearDown(self):
        self.vacuumCleanerClient.close()
        self.connector.close()

    @staticmethod
    def _waitCloudioAttributeToChange(cloudio_attribute, new_value, wait_time=2.0, decr_value=.1):
        """Waits some time and checks that a cloud.iO attribute changes to a given value.
        """
        assert decr_value > 0
        assert wait_time > decr_value

        result = False

        while wait_time > 0:
            time.sleep(decr_value)
            wait_time -= decr_value
            if cloudio_attribute.getValue() == new_value:
                result = True
                break

        return result

    @staticmethod
    def _waitModelAttributeToChange(model_attribute, new_value, wait_time=2.0, decr_value=.1):
        """Waits some time and checks that a model attribute changes to a given value.
        """
        assert decr_value > 0
        assert wait_time > decr_value

        result = False

        while wait_time > 0:
            time.sleep(decr_value)
            wait_time -= decr_value
            if model_attribute == new_value:
                result = True
                break

        return result

    @unittest.skip('because adding a new test')
    def test_objectAttributes(self):
        self.assertTrue(hasattr(self.vacuumCleaner, '_identification'))

    #@unittest.skip('because adding a new test')
    def test_setActionWithStringParameter(self):
        # Create location stack and get the according cloud.iO attribute
        attrLocation = ['setIdentification', 'attributes', 'Parameters', 'objects']
        cloudioAttribute = self.cloudioEndPoint.getNode(VACUUM_CLEANER_NAME).findAttribute(attrLocation)

        # Change the vacuum cleaner's identification string
        # @set/test-vacuum-cleaner/nodes/VacuumCleaner/objects/Parameters/attributes/setIdentification
        newIdent = 'My first VC'
        self.vacuumCleanerClient.setIdentification(newIdent)

        # Wait a short time to let to new value propagate
        self._waitCloudioAttributeToChange(cloudioAttribute, newIdent)
        # Check if changes are updated in the cloud
        self.assertTrue(cloudioAttribute.getValue() == newIdent)            # Value not changed in the cloud
        # Wait for the model attribute to change
        self._waitModelAttributeToChange(self.vacuumCleaner._identification, newIdent)
        # Check if vacuum cleaner model gets notified upon the change
        self.assertEqual(self.vacuumCleaner._identification, newIdent)     # Value not changed in local model

        # Try with another value
        newIdent = 'My second VC'
        self.vacuumCleanerClient.setIdentification(newIdent)
        # Wait a short time to let to new value propagate
        self._waitCloudioAttributeToChange(cloudioAttribute, newIdent)
        # Check if changes are updated in the cloud
        self.assertTrue(cloudioAttribute.getValue() == newIdent)
        # Wait for the model attribute to change
        self._waitModelAttributeToChange(self.vacuumCleaner._identification, newIdent)
        # Check if vacuum cleaner model gets notified upon the change
        self.assertEqual(self.vacuumCleaner._identification, newIdent)

        # ... and one more
        newIdent = 'My only VC'
        self.vacuumCleanerClient.setIdentification(newIdent)
        # Wait a short time to let to new value propagate
        self._waitCloudioAttributeToChange(cloudioAttribute, newIdent)
        # Check if changes are updated in the cloud
        self.assertTrue(cloudioAttribute.getValue() == newIdent)
        # Wait for the model attribute to change
        self._waitModelAttributeToChange(self.vacuumCleaner._identification, newIdent)
        # Check if vacuum cleaner model gets notified upon the change
        self.assertEqual(self.vacuumCleaner._identification, newIdent)

        # TODO What to do if string is empty?
        # TODO What to do if string contains only spaces (non visible characters)?

    #@unittest.skip('because adding a new test')
    def test_setActionWithBooleanParameter(self):
        # Create location stack and get the according cloud.iO attribute
        attrLocation = ['setPowerOn', 'attributes', 'Parameters', 'objects']
        cloudioAttribute = self.cloudioEndPoint.getNode(VACUUM_CLEANER_NAME).findAttribute(attrLocation)

        # Change the vacuum cleaner's power state to 'false'
        newPowerStateValue = False
        self.vacuumCleanerClient.setPowerOn(newPowerStateValue)

        # Wait a short time to let to new value propagate
        self._waitCloudioAttributeToChange(cloudioAttribute, newPowerStateValue)
        # Check if changes are updated in the cloud
        self.assertTrue(cloudioAttribute.getValue() == newPowerStateValue)  # Value not changed in the cloud
        # Wait for the model attribute to change
        self._waitModelAttributeToChange(self.vacuumCleaner._powerOn, newPowerStateValue)
        # Check if vacuum cleaner model gets notified upon the change
        self.assertTrue(self.vacuumCleaner._powerOn == newPowerStateValue)  # Value not changed in local model

        # Change the vacuum cleaner's power state to 'true'
        newPowerStateValue = True
        self.vacuumCleanerClient.setPowerOn(newPowerStateValue)

        # Wait a short time to let to new value propagate
        self._waitCloudioAttributeToChange(cloudioAttribute, newPowerStateValue)
        # Check if changes are updated in the cloud
        self.assertTrue(cloudioAttribute.getValue() == newPowerStateValue)
        # Wait for the model attribute to change
        self._waitModelAttributeToChange(self.vacuumCleaner._powerOn, newPowerStateValue)
        # Check if vacuum cleaner model gets notified upon the change
        self.assertTrue(self.vacuumCleaner._powerOn == newPowerStateValue)

        # ... and again to 'false'
        newPowerStateValue = False
        self.vacuumCleanerClient.setPowerOn(newPowerStateValue)

        # Wait a short time to let to new value propagate
        self._waitCloudioAttributeToChange(cloudioAttribute, newPowerStateValue)
        # Check if changes are updated in the cloud
        self.assertTrue(cloudioAttribute.getValue() == newPowerStateValue)
        # Wait for the model attribute to change
        self._waitModelAttributeToChange(self.vacuumCleaner._powerOn, newPowerStateValue)
        # Check if vacuum cleaner model gets notified upon the change
        self.assertTrue(self.vacuumCleaner._powerOn == newPowerStateValue)

        # ... and what's with 1
        newPowerStateValue = 1
        self.vacuumCleanerClient.setPowerOn(newPowerStateValue)

        # Wait a short time to let to new value propagate
        self._waitCloudioAttributeToChange(cloudioAttribute, newPowerStateValue)
        # Check if changes are updated in the cloud
        self.assertTrue(cloudioAttribute.getValue() == newPowerStateValue)
        # Wait for the model attribute to change
        self._waitModelAttributeToChange(self.vacuumCleaner._powerOn, newPowerStateValue)
        # Check if vacuum cleaner model gets notified upon the change
        self.assertTrue(self.vacuumCleaner._powerOn == newPowerStateValue)

        # ... and with 0
        newPowerStateValue = 0
        self.vacuumCleanerClient.setPowerOn(newPowerStateValue)

        # Wait a short time to let to new value propagate
        self._waitCloudioAttributeToChange(cloudioAttribute, newPowerStateValue)
        # Check if changes are updated in the cloud
        self.assertTrue(cloudioAttribute.getValue() == newPowerStateValue)
        # Wait for the model attribute to change
        self._waitModelAttributeToChange(self.vacuumCleaner._powerOn, newPowerStateValue)
        # Check if vacuum cleaner model gets notified upon the change
        self.assertTrue(self.vacuumCleaner._powerOn == newPowerStateValue)

        # ... and what's with '1'
        newPowerStateValue = '1'
        self.vacuumCleanerClient.setPowerOn(newPowerStateValue)

        # Wait a short time to let to new value propagate
        self._waitCloudioAttributeToChange(cloudioAttribute, newPowerStateValue)
        # Check if changes are updated in the cloud
        self.assertTrue(cloudioAttribute.getValue() == bool(newPowerStateValue))
        # Wait for the model attribute to change
        self._waitModelAttributeToChange(self.vacuumCleaner._powerOn, newPowerStateValue)
        # Check if vacuum cleaner model gets notified upon the change
        self.assertTrue(self.vacuumCleaner._powerOn == bool(newPowerStateValue))

        # ... and with '0'
        newPowerStateValue = '0'
        self.vacuumCleanerClient.setPowerOn(newPowerStateValue)

        # Wait a short time to let to new value propagate
        self._waitCloudioAttributeToChange(cloudioAttribute, newPowerStateValue)
        # Check if changes are updated in the cloud
        comp_val = False if (newPowerStateValue == '0') else True
        self.assertTrue(cloudioAttribute.getValue() == comp_val)
        # Wait for the model attribute to change
        self._waitModelAttributeToChange(self.vacuumCleaner._powerOn, newPowerStateValue)
        # Check if vacuum cleaner model gets notified upon the change
        self.assertTrue(self.vacuumCleaner._powerOn == comp_val)

    @unittest.skip('because adding a new test')
    def test_setActionWithNumberParameter(self):
        # Create location stack and get the according cloud.iO attribute
        attrLocation = ['setThroughput', 'attributes', 'Parameters', 'objects']
        cloudioAttribute = self.cloudioEndPoint.getNode(VACUUM_CLEANER_NAME).findAttribute(attrLocation)

        # Values to test
        throughputs = [100.0, 981.7, 0.0, 200.0, -500.0, 1.0, 1.54, 1800]

        for newThroughput in throughputs:
            # Change the vacuum cleaner's throughput
            self.vacuumCleanerClient.setThroughput(newThroughput)

            # Wait a short time to let to new value propagate
            self._waitCloudioAttributeToChange(cloudioAttribute, newThroughput)
            # Check if changes are updated in the cloud
            self.assertEqual(cloudioAttribute.getValue(), newThroughput)       # Value not changed in the cloud
            # Wait for the model attribute to change
            self._waitModelAttributeToChange(self.vacuumCleaner._throughput, newThroughput)
            # Check if vacuum cleaner model gets notified upon the change
            self.assertEqual(self.vacuumCleaner._throughput, newThroughput)    # Value not changed in local model

    @unittest.skip('because adding a new test')
    def test_setActionWithIntegerParameter(self):
        # Create location stack and get the according cloud.iO attribute
        attrLocation = ['setOperatingMode', 'attributes', 'Parameters', 'objects']
        cloudioAttribute = self.cloudioEndPoint.getNode(VACUUM_CLEANER_NAME).findAttribute(attrLocation)

        # Values to test
        operationModes = [3, 5, 2, -1, 0, 10, 8, 2, -2, 1.0, 1800.1]

        for newOperationMode in operationModes:
            # Change the vacuum cleaner's operation mode
            self.vacuumCleanerClient.setOperatingMode(newOperationMode)

            # Wait a short time to let to new value propagate
            self._waitCloudioAttributeToChange(cloudioAttribute, newOperationMode)
            # Check if changes are updated in the cloud
            self.assertEqual(cloudioAttribute.getValue(), int(newOperationMode))
            # Wait for the model attribute to change
            self._waitModelAttributeToChange(self.vacuumCleaner._operatingMode, int(newOperationMode))
            # Check if vacuum cleaner model gets notified upon the change
            self.assertEqual(self.vacuumCleaner._operatingMode, int(newOperationMode))


if __name__ == '__main__':

    # Enable logging
    logging.basicConfig(format='%(asctime)s.%(msecs)03d - %(name)s - %(levelname)s - %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S',
                        level=logging.INFO)

    unittest.main()
