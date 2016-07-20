# -*- coding: utf-8 -*-

from threading import Thread, Lock
import time
import uuid
from .mqtt_helpers import MqttAsyncClient, MqttConnectOptions
from cloudio.properties_endpoint_configuration import PropertiesEndpointConfiguration
from utils.resource_loader import ResourceLoader

class CloudioEndpoint():
    def __init__(self, uuidStr):
        if isinstance(uuidStr, uuid.UUID):
            uuidStr = str(uuidStr)
        self.internal = _InternalEndpoint(uuidStr)

class _InternalEndpoint():
    """Internal Endpoint structure used by CloudioEndpoint.

    Contains among other things the mqtt client to talk to the cloudio broker.
    """

    # Constants ######################################################################################
    MQTT_HOST_URI_PROPERTY = 'ch.hevs.cloudio.endpoint.hostUri'

    def __init__(self, uuid, configuration=None):

        self.uuid = uuid

        # Check if a configuration with properties is given
        if configuration is None:
            # Try to load properties using a config file
            properties = ResourceLoader.loadFromLocations(self.uuid + '.properties',
                                                          ['home:' + '/.config/cloud.io/', 'file:/etc/cloud.io/'])
            configuration = PropertiesEndpointConfiguration(properties)

        self._retryInterval = 10    # Connect retry interval in seconds

        # Check if 'host' property is present in config file
        host = configuration.getProperty(self.MQTT_HOST_URI_PROPERTY)
        if host == '':
            exit('Missing mandatory property "' + self.MQTT_HOST_URI_PROPERTY + '"')

        self.options = MqttConnectOptions()

        # TODO: Remove _username and _password
        self.options._username = configuration.getProperty('username')
        self.options._password = configuration.getProperty('password')

        self.mqtt = MqttAsyncClient(host)

        self.thread = Thread(target=self.run, name='cloudio-endpoint-' + self.uuid)
        # Close thread as soon as main thread exits
        self.thread.setDaemon(True)
        self.thread.start()

    def run(self):
        """Called by the internal thread"""

        print 'Cloudio endpoint thread running...'

        while not self.mqtt.isConnected():
            try:
                self.mqtt.connect(self.options._username, self.options._password)
            except:
                pass

            if not self.mqtt.isConnected():
                # If we should not retry, give up
                if self._retryInterval == 0:
                    # TODO Do I need to stop the thread here?!
                    return

                time.sleep(self._retryInterval)

                # Again, if we should not retry, give up
                if self._retryInterval == 0:
                    # TODO Do I need to stop the thread here?!
                    return

        # Announce our presence to the broker
        self.announce()

        # If we arrive here, we are online, so we can inform listeners about that and stop the connecting thread
#        self.mqtt.setCallback(self)

    def announce(self):
        # Send birth message
        print 'Sending birth message...'
        strMessage = 'TBD'
        self.mqtt.publish('@online/' + self.uuid, strMessage, 1, True)
