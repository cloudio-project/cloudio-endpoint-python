#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time
import logging
import unittest
from tests.cloudio.paths import update_working_directory
from connector.vacuumcleaner_connector import VacuumCleanerConnector
from model.vacuum_cleaner import VacuumCleaner
from client.vacuumcleaner_client import VacuumCleanerClient

update_working_directory()  # Needed when: 'pipenv run python -m unittest tests/cloudio/{this_file}.py'

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
        self.vacuumCleaner.set_cloudio_buddy(cloudio_vacuum_cleaner)

        # Create CloudioClient that sends the @set commands
        self.vacuumCleanerClient = VacuumCleanerClient('~/.config/cloud.io/client/vacuum-cleaner-client.config')
        self.log.info('Waiting to connect client to cloud.iO...')
        self.vacuumCleanerClient.wait_until_connected()

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
            if cloudio_attribute.get_value() == new_value:
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

    # @unittest.skip('because adding a new test')
    def test_objectAttributes(self):
        self.assertTrue(hasattr(self.vacuumCleaner, '_identification'))

    # @unittest.skip('because adding a new test')
    def test_setActionWithStringParameter(self):
        # Create location stack and get the according cloud.iO attribute
        attr_location = ['set_identification', 'attributes', 'Parameters', 'objects']
        cloudio_attribute = self.cloudioEndPoint.getNode(VACUUM_CLEANER_NAME).find_attribute(attr_location)

        # Change the vacuum cleaner's identification string
        # @set/test-vacuum-cleaner/nodes/VacuumCleaner/objects/Parameters/attributes/set_identification
        new_ident = 'My first VC'
        self.vacuumCleanerClient.set_identification(new_ident)

        # Wait a short time to let to new value propagate
        self._waitCloudioAttributeToChange(cloudio_attribute, new_ident)
        # Check if changes are updated in the cloud
        self.assertTrue(cloudio_attribute.get_value() == new_ident)            # Value not changed in the cloud
        # Wait for the model attribute to change
        self._waitModelAttributeToChange(self.vacuumCleaner._identification, new_ident)
        # Check if vacuum cleaner model gets notified upon the change
        self.assertEqual(self.vacuumCleaner._identification, new_ident)     # Value not changed in local model

        # Try with another value
        new_ident = 'My second VC'
        self.vacuumCleanerClient.set_identification(new_ident)
        # Wait a short time to let to new value propagate
        self._waitCloudioAttributeToChange(cloudio_attribute, new_ident)
        # Check if changes are updated in the cloud
        self.assertTrue(cloudio_attribute.get_value() == new_ident)
        # Wait for the model attribute to change
        self._waitModelAttributeToChange(self.vacuumCleaner._identification, new_ident)
        # Check if vacuum cleaner model gets notified upon the change
        self.assertEqual(self.vacuumCleaner._identification, new_ident)

        # ... and one more
        new_ident = 'My only VC'
        self.vacuumCleanerClient.set_identification(new_ident)
        # Wait a short time to let to new value propagate
        self._waitCloudioAttributeToChange(cloudio_attribute, new_ident)
        # Check if changes are updated in the cloud
        self.assertTrue(cloudio_attribute.get_value() == new_ident)
        # Wait for the model attribute to change
        self._waitModelAttributeToChange(self.vacuumCleaner._identification, new_ident)
        # Check if vacuum cleaner model gets notified upon the change
        self.assertEqual(self.vacuumCleaner._identification, new_ident)

        # TODO What to do if string is empty?
        # TODO What to do if string contains only spaces (non visible characters)?

    # @unittest.skip('because adding a new test')
    def test_setActionWithBooleanParameter(self):
        # Create location stack and get the according cloud.iO attribute
        attr_location = ['set_power_on', 'attributes', 'Parameters', 'objects']
        cloudio_attribute = self.cloudioEndPoint.getNode(VACUUM_CLEANER_NAME).find_attribute(attr_location)

        # Change the vacuum cleaner's power state to 'false'
        new_power_state_value = False
        self.vacuumCleanerClient.set_power_on(new_power_state_value)

        # Wait a short time to let to new value propagate
        self._waitCloudioAttributeToChange(cloudio_attribute, new_power_state_value)
        # Check if changes are updated in the cloud
        self.assertTrue(cloudio_attribute.get_value() == new_power_state_value)  # Value not changed in the cloud
        # Wait for the model attribute to change
        self._waitModelAttributeToChange(self.vacuumCleaner._powerOn, new_power_state_value)
        # Check if vacuum cleaner model gets notified upon the change
        self.assertTrue(self.vacuumCleaner._powerOn == new_power_state_value)  # Value not changed in local model

        # Change the vacuum cleaner's power state to 'true'
        new_power_state_value = True
        self.vacuumCleanerClient.set_power_on(new_power_state_value)

        # Wait a short time to let to new value propagate
        self._waitCloudioAttributeToChange(cloudio_attribute, new_power_state_value)
        # Check if changes are updated in the cloud
        self.assertTrue(cloudio_attribute.get_value() == new_power_state_value)
        # Wait for the model attribute to change
        self._waitModelAttributeToChange(self.vacuumCleaner._powerOn, new_power_state_value)
        # Check if vacuum cleaner model gets notified upon the change
        self.assertTrue(self.vacuumCleaner._powerOn == new_power_state_value)

        # ... and again to 'false'
        new_power_state_value = False
        self.vacuumCleanerClient.set_power_on(new_power_state_value)

        # Wait a short time to let to new value propagate
        self._waitCloudioAttributeToChange(cloudio_attribute, new_power_state_value)
        # Check if changes are updated in the cloud
        self.assertTrue(cloudio_attribute.get_value() == new_power_state_value)
        # Wait for the model attribute to change
        self._waitModelAttributeToChange(self.vacuumCleaner._powerOn, new_power_state_value)
        # Check if vacuum cleaner model gets notified upon the change
        self.assertTrue(self.vacuumCleaner._powerOn == new_power_state_value)

        # ... and what's with 1
        new_power_state_value = 1
        self.vacuumCleanerClient.set_power_on(new_power_state_value)

        # Wait a short time to let to new value propagate
        self._waitCloudioAttributeToChange(cloudio_attribute, new_power_state_value)
        # Check if changes are updated in the cloud
        self.assertTrue(cloudio_attribute.get_value() == new_power_state_value)
        # Wait for the model attribute to change
        self._waitModelAttributeToChange(self.vacuumCleaner._powerOn, new_power_state_value)
        # Check if vacuum cleaner model gets notified upon the change
        self.assertTrue(self.vacuumCleaner._powerOn == new_power_state_value)

        # ... and with 0
        new_power_state_value = 0
        self.vacuumCleanerClient.set_power_on(new_power_state_value)

        # Wait a short time to let to new value propagate
        self._waitCloudioAttributeToChange(cloudio_attribute, new_power_state_value)
        # Check if changes are updated in the cloud
        self.assertTrue(cloudio_attribute.get_value() == new_power_state_value)
        # Wait for the model attribute to change
        self._waitModelAttributeToChange(self.vacuumCleaner._powerOn, new_power_state_value)
        # Check if vacuum cleaner model gets notified upon the change
        self.assertTrue(self.vacuumCleaner._powerOn == new_power_state_value)

        # ... and what's with '1'
        new_power_state_value = '1'
        self.vacuumCleanerClient.set_power_on(new_power_state_value)

        # Wait a short time to let to new value propagate
        self._waitCloudioAttributeToChange(cloudio_attribute, new_power_state_value)
        # Check if changes are updated in the cloud
        self.assertTrue(cloudio_attribute.get_value() == bool(new_power_state_value))
        # Wait for the model attribute to change
        self._waitModelAttributeToChange(self.vacuumCleaner._powerOn, new_power_state_value)
        # Check if vacuum cleaner model gets notified upon the change
        self.assertTrue(self.vacuumCleaner._powerOn == bool(new_power_state_value))

        # ... and with '0'
        new_power_state_value = '0'
        self.vacuumCleanerClient.set_power_on(new_power_state_value)

        # Wait a short time to let to new value propagate
        self._waitCloudioAttributeToChange(cloudio_attribute, new_power_state_value)
        # Check if changes are updated in the cloud
        comp_val = False if (new_power_state_value == '0') else True
        self.assertTrue(cloudio_attribute.get_value() == comp_val)
        # Wait for the model attribute to change
        self._waitModelAttributeToChange(self.vacuumCleaner._powerOn, new_power_state_value)
        # Check if vacuum cleaner model gets notified upon the change
        self.assertTrue(self.vacuumCleaner._powerOn == comp_val)

    # @unittest.skip('because adding a new test')
    def test_setActionWithNumberParameter(self):
        # Create location stack and get the according cloud.iO attribute
        attr_location = ['set_throughput', 'attributes', 'Parameters', 'objects']
        cloudio_attribute = self.cloudioEndPoint.getNode(VACUUM_CLEANER_NAME).find_attribute(attr_location)

        # Values to test
        throughputs = [100.0, 981.7, 0.0, 200.0, -500.0, 1.0, 1.54, 1800]

        for newThroughput in throughputs:
            # Change the vacuum cleaner's throughput
            self.vacuumCleanerClient.set_throughput(newThroughput)

            # Wait a short time to let to new value propagate
            self._waitCloudioAttributeToChange(cloudio_attribute, newThroughput)
            # Check if changes are updated in the cloud
            self.assertEqual(cloudio_attribute.get_value(), newThroughput)       # Value not changed in the cloud
            # Wait for the model attribute to change
            self._waitModelAttributeToChange(self.vacuumCleaner._throughput, newThroughput)
            # Check if vacuum cleaner model gets notified upon the change
            self.assertEqual(self.vacuumCleaner._throughput, newThroughput)    # Value not changed in local model

    # @unittest.skip('because adding a new test')
    def test_setActionWithIntegerParameter(self):
        # Create location stack and get the according cloud.iO attribute
        attr_location = ['set_operating_mode', 'attributes', 'Parameters', 'objects']
        cloudio_attribute = self.cloudioEndPoint.getNode(VACUUM_CLEANER_NAME).find_attribute(attr_location)

        # Values to test
        operation_modes = [3, 5, 2, -1, 0, 10, 8, 2, -2, 1.0, 1800.1]

        for newOperationMode in operation_modes:
            # Change the vacuum cleaner's operation mode
            self.vacuumCleanerClient.set_operating_mode(newOperationMode)

            # Wait a short time to let to new value propagate
            self._waitCloudioAttributeToChange(cloudio_attribute, newOperationMode)
            # Check if changes are updated in the cloud
            self.assertEqual(cloudio_attribute.get_value(), int(newOperationMode))
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
