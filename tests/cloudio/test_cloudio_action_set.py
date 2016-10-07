#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time
import logging
import unittest
from connector.vacuumcleaner_connector import VacuumCleanerConnector
from model.vacuum_cleaner import VacuumCleaner
from client.vacuumcleaner_client import VacuumCleanerClient

class TestCloudioSetAction(unittest.TestCase):
    """Tests @set action with various attributes.
    """

    log = logging.getLogger(__name__)

    def setUp(self):
        self.connector = VacuumCleanerConnector('test-vacuum-cleaner')  # Searches for file 'test-vacuum-cleaner.properties'
        self.cloudioEndPoint = self.connector.endpoint

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
        self.vacuumCleanerClient = VacuumCleanerClient('~/.config/cloud.io/client/vacuum-cleaner-client.config')
        self.log.info('Waiting to connect client to cloud.iO...')
        self.vacuumCleanerClient.waitUntilConnected()

        self.log.info('Setup finished')

    def tearDown(self):
        self.vacuumCleanerClient.close()
        self.connector.close()

    def _waitCloudioAttributeToChange(self, cloudioAttribute, newValue, waitTime=2.0, decrValue=.1):
        """Waits some time and checks that a cloud.iO attribute changes to a given value.
        """
        assert decrValue > 0
        assert waitTime > decrValue

        result = False

        while waitTime > 0:
            time.sleep(decrValue)
            waitTime -= decrValue
            if cloudioAttribute.getValue() == newValue:
                result = True
                break

        return result

    #@unittest.skip('because adding a new test')
    def test_objectAttributes(self):
        self.assertTrue(hasattr(self.vacuumCleaner, '_identification'))

    #@unittest.skip('because adding a new test')
    def test_setActionWithStringParameter(self):
        # Create location stack and get the according cloud.iO attribute
        attrLocation = ['setIdentification', 'attributes', 'Parameters', 'objects']
        cloudioAttribute = self.cloudioEndPoint.getNode(u'VacuumCleaner').findAttribute(attrLocation)

        # Change the vacuum cleaner's identification string
        newIdent = 'My first VC'
        self.vacuumCleanerClient.setIdentification(newIdent)

        # Wait a short time to let to new value propagate
        self._waitCloudioAttributeToChange(cloudioAttribute, newIdent)
        # Check if changes are updated in the cloud
        self.assertTrue(cloudioAttribute.getValue() == newIdent)            # Value not changed in the cloud
        # Check if vacuum cleaner model gets notified upon the change
        self.assertTrue(self.vacuumCleaner._identification == newIdent)     # Value not changed in local model

        # Try with an other value
        newIdent = 'My second VC'
        self.vacuumCleanerClient.setIdentification(newIdent)
        # Wait a short time to let to new value propagate
        self._waitCloudioAttributeToChange(cloudioAttribute, newIdent)
        # Check if changes are updated in the cloud
        self.assertTrue(cloudioAttribute.getValue() == newIdent)
        # Check if vacuum cleaner model gets notified upon the change
        self.assertTrue(self.vacuumCleaner._identification == newIdent)

        # ... and one more
        newIdent = 'My only VC'
        self.vacuumCleanerClient.setIdentification(newIdent)
        # Wait a short time to let to new value propagate
        self._waitCloudioAttributeToChange(cloudioAttribute, newIdent)
        # Check if changes are updated in the cloud
        self.assertTrue(cloudioAttribute.getValue() == newIdent)
        # Check if vacuum cleaner model gets notified upon the change
        self.assertTrue(self.vacuumCleaner._identification == newIdent)

        # TODO What to do if string is empty?
        # TODO What to do if string contains only spaces (non visible characters)?

    def test_setActionWithBooleanParameter(self):
        # Create location stack and get the according cloud.iO attribute
        attrLocation = ['setPowerOn', 'attributes', 'Parameters', 'objects']
        cloudioAttribute = self.cloudioEndPoint.getNode(u'VacuumCleaner').findAttribute(attrLocation)

        # Change the vacuum cleaner's power state to 'false'
        newPowerStateValue = False
        self.vacuumCleanerClient.setPowerOn(newPowerStateValue)

        # Wait a short time to let to new value propagate
        self._waitCloudioAttributeToChange(cloudioAttribute, newPowerStateValue)
        # Check if changes are updated in the cloud
        self.assertTrue(cloudioAttribute.getValue() == newPowerStateValue)  # Value not changed in the cloud
        # Check if vacuum cleaner model gets notified upon the change
        self.assertTrue(self.vacuumCleaner._powerOn == newPowerStateValue)  # Value not changed in local model

        # Change the vacuum cleaner's power state to 'true'
        newPowerStateValue = True
        self.vacuumCleanerClient.setPowerOn(newPowerStateValue)

        # Wait a short time to let to new value propagate
        self._waitCloudioAttributeToChange(cloudioAttribute, newPowerStateValue)
        # Check if changes are updated in the cloud
        self.assertTrue(cloudioAttribute.getValue() == newPowerStateValue)
        # Check if vacuum cleaner model gets notified upon the change
        self.assertTrue(self.vacuumCleaner._powerOn == newPowerStateValue)

        # ... and again to 'false'
        newPowerStateValue = False
        self.vacuumCleanerClient.setPowerOn(newPowerStateValue)

        # Wait a short time to let to new value propagate
        self._waitCloudioAttributeToChange(cloudioAttribute, newPowerStateValue)
        # Check if changes are updated in the cloud
        self.assertTrue(cloudioAttribute.getValue() == newPowerStateValue)
        # Check if vacuum cleaner model gets notified upon the change
        self.assertTrue(self.vacuumCleaner._powerOn == newPowerStateValue)

        # ... and what's with 1
        newPowerStateValue = 1
        self.vacuumCleanerClient.setPowerOn(newPowerStateValue)

        # Wait a short time to let to new value propagate
        self._waitCloudioAttributeToChange(cloudioAttribute, newPowerStateValue)
        # Check if changes are updated in the cloud
        self.assertTrue(cloudioAttribute.getValue() == newPowerStateValue)
        # Check if vacuum cleaner model gets notified upon the change
        self.assertTrue(self.vacuumCleaner._powerOn == newPowerStateValue)

        # ... and with 0
        newPowerStateValue = 0
        self.vacuumCleanerClient.setPowerOn(newPowerStateValue)

        # Wait a short time to let to new value propagate
        self._waitCloudioAttributeToChange(cloudioAttribute, newPowerStateValue)
        # Check if changes are updated in the cloud
        self.assertTrue(cloudioAttribute.getValue() == newPowerStateValue)
        # Check if vacuum cleaner model gets notified upon the change
        self.assertTrue(self.vacuumCleaner._powerOn == newPowerStateValue)

        # ... and what's with '1'
        newPowerStateValue = '1'
        self.vacuumCleanerClient.setPowerOn(newPowerStateValue)

        # Wait a short time to let to new value propagate
        self._waitCloudioAttributeToChange(cloudioAttribute, newPowerStateValue)
        # Check if changes are updated in the cloud
        self.assertTrue(cloudioAttribute.getValue() == bool(newPowerStateValue))
        # Check if vacuum cleaner model gets notified upon the change
        self.assertTrue(self.vacuumCleaner._powerOn == bool(newPowerStateValue))

        # ... and with '0'
        newPowerStateValue = '0'
        self.vacuumCleanerClient.setPowerOn(newPowerStateValue)

        # Wait a short time to let to new value propagate
        self._waitCloudioAttributeToChange(cloudioAttribute, newPowerStateValue)
        # Check if changes are updated in the cloud
        self.assertTrue(cloudioAttribute.getValue() == bool(newPowerStateValue))
        # Check if vacuum cleaner model gets notified upon the change
        self.assertTrue(self.vacuumCleaner._powerOn == bool(newPowerStateValue))


if __name__ == '__main__':

    # Enable logging
    logging.basicConfig(format='%(asctime)s.%(msecs)03d - %(name)s - %(levelname)s - %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S',
                        level=logging.INFO)

    unittest.main()
