# -*- coding: utf-8 -*-

from threading import Thread, Lock
import time
import uuid
import types
from .mqtt_helpers import MqttAsyncClient, MqttConnectOptions
from cloudio.properties_endpoint_configuration import PropertiesEndpointConfiguration
from utils.resource_loader import ResourceLoader
from cloudio.cloudio_node import CloudioNode
from message_format.json_format import JsonMessageFormat
from utils import path_helpers

class CloudioEndpoint():
    """Internal Endpoint structure used by CloudioEndpoint.

    Contains among other things the mqtt client to talk to the cloudio broker.
    """

    # Constants ######################################################################################
    MQTT_HOST_URI_PROPERTY = u'ch.hevs.cloudio.endpoint.hostUri'

    CERT_AUTHORITY_FILE_PROPERTY = u'ch.hevs.cloudio.endpoint.ssl.authorityCert'

    ENDPOINT_IDENTITY_FILE_PROPERTY = u'ch.hevs.cloudio.endpoint.ssl.clientCert'        # PKCS12 based file (*.p12)
    ENDPOINT_IDENTITY_CERT_FILE_PROPERTY = u'ch.hevs.cloudio.endpoint.ssl.clientCert'   # (*.pem)
    ENDPOINT_IDENTITY_KEY_FILE_PROPERTY = u'ch.hevs.cloudio.endpoint.ssl.clientKey'     # (*.pem)

    def __init__(self, uuid, configuration=None):

        self.uuid = uuid            # type: str
        self.nodes = {}             # type: dict as CloudioNode
        self.cleanSession = True
        self.messageFormat = None   # type: CloudioMessageFormat

        # Check if a configuration with properties is given
        if configuration is None:
            # Try to load properties using a config file
            properties = ResourceLoader.loadFromLocations(self.uuid + '.properties',
                                                          ['home:' + '/.config/cloud.io/', 'file:/etc/cloud.io/'])
            configuration = PropertiesEndpointConfiguration(properties)

        self._retryInterval = 10    # Connect retry interval in seconds
        self.messageFormat = JsonMessageFormat()

        # Check if 'host' property is present in config file
        host = configuration.getProperty(self.MQTT_HOST_URI_PROPERTY)
        if host == '':
            exit('Missing mandatory property "' + self.MQTT_HOST_URI_PROPERTY + '"')

        self.options = MqttConnectOptions()

        self.options._caFile = configuration.getProperty(self.CERT_AUTHORITY_FILE_PROPERTY, None)
        self.options._clientCertFile = configuration.getProperty(self.ENDPOINT_IDENTITY_CERT_FILE_PROPERTY, None)
        self.options._clientKeyFile = configuration.getProperty(self.ENDPOINT_IDENTITY_KEY_FILE_PROPERTY, None)
        self.options._username = configuration.getProperty('username')
        self.options._password = configuration.getProperty('password')

        # Make path usable
        self.options._caFile = path_helpers.prettify(self.options._caFile)
        self.options._clientCertFile = path_helpers.prettify(self.options._clientCertFile)
        self.options._clientKeyFile = path_helpers.prettify(self.options._clientKeyFile)

        self.mqtt = MqttAsyncClient(host, clientId=self.uuid, clean_session=self.cleanSession)

        self.thread = Thread(target=self.run, name='cloudio-endpoint-' + self.uuid)
        # Close thread as soon as main thread exits
        self.thread.setDaemon(True)
        self.thread.start()

    def getName(self): return self.uuid

    def addNode(self, nodeName, clsOrObject):
        if nodeName != '' and clsOrObject != None:
            node = None

            # Add node to endpoint
#            if clsOrObject == types.InstanceType:
#                assert isinstance(clsOrObject, CloudioNode)
#                pass    # All right. We have our needed object
            if isinstance(clsOrObject, CloudioNode):
                node = clsOrObject
                pass  # All right. We have our needed object
            else:
                raise RuntimeError(u'Wrong cloud.iO object type')

            if node:
                # We got an object
                node.setName(nodeName)
                node.setParentNodeContainer(self)

                assert not self.nodes.has_key(nodeName), u'Node with given name already present!'
                self.nodes[nodeName] = node

                # If the endpoint is online, send node add message
                if self.isOnline():
                    data = self.messageFormat.serializeNode(node)
                    print data
                    self.mqtt.publish(u'@nodeAdded/' + node.getUuid().toString(), data, 1, False)


    def run(self):
        """Called by the internal thread"""

        print u'Cloudio endpoint thread running...'

        while not self.mqtt.isConnected():
            try:
                self.mqtt.connect(self.options)
            except:
                print u'Error during broker connect!'
                exit(1)

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

    def isOnline(self):
        return self.mqtt.isConnected()

    def announce(self):
        # Send birth message
        print u'Sending birth message...'
        strMessage = u'TBD'
        self.mqtt.publish(u'@online/' + self.uuid, strMessage, 1, True)
