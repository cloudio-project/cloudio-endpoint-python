#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import time
import logging
import traceback
import six
import utils.timestamp as TimeStampProvider
import cloudio.mqtt_helpers as mqtt
from cloudio.cloudio_node import CloudioNode
from cloudio.properties_endpoint_configuration import PropertiesEndpointConfiguration
from cloudio.interface.node_container import CloudioNodeContainer
from cloudio.interface.message_format import CloudioMessageFormat
from cloudio.message_format.factory import MessageFormatFactory
from cloudio.exception.cloudio_modification_exception import CloudioModificationException
from cloudio.exception.invalid_property_exception import InvalidPropertyException
from utils.resource_loader import ResourceLoader
from cloudio.message_format.json_format import JsonMessageFormat
from utils import path_helpers
from cloudio.pending_update import PendingUpdate
from cloudio.topicuuid import TopicUuid

version = ''
# Get endpoint python version info from init file
with open(os.path.dirname(os.path.realpath(__file__)) + '/__init__.py') as vf:
    content = vf.readlines()
    for line in content:
        if '__version__' in line:
            values = line.split('=')
            version = values[1]
            version = version.strip('\n')
            version = version.strip('\r')
            version = version.replace('\'', '')
            version = version.strip(' ')
            break

# Enable logging
logging.basicConfig(format='%(asctime)s.%(msecs)03d - %(name)s - %(levelname)s - %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S',
                    level=logging.DEBUG)
logging.getLogger(__name__).setLevel(logging.INFO)    # DEBUG, INFO, WARNING, ERROR, CRITICAL

logging.getLogger(__name__).info('cloudio-endpoint-python version: %s' % version)

class CloudioEndpoint(CloudioNodeContainer):
    """The cloud.iO endpoint.

    Contains among other things the mqtt client to talk to the cloudio broker.
    """

    # Constants ######################################################################################
    MQTT_HOST_URI_PROPERTY    = u'ch.hevs.cloudio.endpoint.hostUri'
    MQTT_PERSISTENCE_MEMORY   = u'memory'
    MQTT_PERSISTENCE_FILE     = u'file'
    MQTT_PERSISTENCE_NONE     = u'none'
    MQTT_PERSISTENCE_PROPERTY = u'ch.hevs.cloudio.endpoint.persistence'
    MQTT_PERSISTENCE_DEFAULT  = MQTT_PERSISTENCE_FILE
    MQTT_PERSISTENCE_LOCATION = u'ch.hevs.cloudio.endpoint.persistenceLocation'

    CERT_AUTHORITY_FILE_PROPERTY = u'ch.hevs.cloudio.endpoint.ssl.authorityCert'
    ENDPOINT_IDENTITY_TLS_VERSION_PROPERTY = u'ch.hevs.cloudio.endpoint.ssl.version'    # tlsv1.0 or tlsv1.2
    ENDPOINT_IDENTITY_FILE_PROPERTY = u'ch.hevs.cloudio.endpoint.ssl.clientCert'        # PKCS12 based file (*.p12)
    ENDPOINT_IDENTITY_CERT_FILE_PROPERTY = u'ch.hevs.cloudio.endpoint.ssl.clientCert'   # (*.pem)
    ENDPOINT_IDENTITY_KEY_FILE_PROPERTY = u'ch.hevs.cloudio.endpoint.ssl.clientKey'     # (*.pem)

    log = logging.getLogger(__name__)

    def __init__(self, uuid, configuration=None):
        self._endPointIsReady = False               # Set to true after connection and subscription

        self.uuid = uuid            # type: str
        self.nodes = {}             # type: dict as CloudioNode
        self.cleanSession = True
        self.messageFormat = None   # type: CloudioMessageFormat
        self.persistence = None     # type MqttClientPersistence

        self.log.debug('Creating Endpoint %s' % uuid)

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

        # Create persistence object.
        persistenceType = configuration.getProperty(self.MQTT_PERSISTENCE_PROPERTY, self.MQTT_PERSISTENCE_DEFAULT)
        if persistenceType == self.MQTT_PERSISTENCE_MEMORY:
            self.persistence = mqtt.MemoryPersistence()
        elif persistenceType == self.MQTT_PERSISTENCE_FILE:
            persistenceLocation = configuration.getProperty(self.MQTT_PERSISTENCE_LOCATION)
            self.persistence = mqtt.MqttDefaultFilePersistence(directory=persistenceLocation)
        elif persistenceType == self.MQTT_PERSISTENCE_NONE:
            self.persistence = None
        else:
            raise InvalidPropertyException('Unknown persistence implementation ' +
                                           '(ch.hevs.cloudio.endpoint.persistence): ' +
                                           '\'' + persistenceType + '\'')
        # Open peristence storage
        if self.persistence:
            self.persistence.open(clientId=self.uuid, serverUri=host)

        self.options = mqtt.MqttConnectOptions()

        # Last will is a message with the UUID of the endpoint and no payload.
        willMessage = 'DEAD'
        self.options.setWill(u'@offline/' + uuid, willMessage, 1, False)

        self.options._caFile = configuration.getProperty(self.CERT_AUTHORITY_FILE_PROPERTY, None)
        self.options._clientCertFile = configuration.getProperty(self.ENDPOINT_IDENTITY_CERT_FILE_PROPERTY, None)
        self.options._clientKeyFile = configuration.getProperty(self.ENDPOINT_IDENTITY_KEY_FILE_PROPERTY, None)
        self.options._username = configuration.getProperty('username')
        self.options._password = configuration.getProperty('password')
        self.options._tlsVersion = configuration.getProperty(self.ENDPOINT_IDENTITY_TLS_VERSION_PROPERTY, 'tlsv1.2')

        # Make path usable
        self.options._caFile = path_helpers.prettify(self.options._caFile)
        self.options._clientCertFile = path_helpers.prettify(self.options._clientCertFile)
        self.options._clientKeyFile = path_helpers.prettify(self.options._clientKeyFile)

        self._client = mqtt.MqttReconnectClient(host,
                                                clientId=self.uuid + '-endpoint-',
                                                clean_session=self.cleanSession,
                                                options=self.options)
        # Register callback method for connection established
        self._client.setOnConnectedCallback(self._onConnected)
        # Register callback method to be called when receiving a message over MQTT
        self._client.setOnMessageCallback(self._onMessageArrived)
        # Start the client
        self._client.start()

    def close(self):
        # Stop Mqtt client
        self._client.stop()

    def _onMessageArrived(self, client, userdata, msg):
        #print(msg.topic + ': ' + str(msg.payload))
        try:
            if six.PY3:
                # Need to convert from bytes to string
                payload = msg.payload.decode('utf-8')
            else:
                payload = msg.payload

            # First determine the message format (first byte identifies the message format).
            messageFormat = MessageFormatFactory.messageFormat(payload[0])
            if messageFormat == None:
                self.log.error('Message-format ' + payload[0] + " not supported!")
                return

            topicLevels = msg.topic.split('/')
            # Create attribute location path stack.
            location = []
            for topicLevel in topicLevels:
                location.insert(0, topicLevel)

            # Read the action tag from the topic
            action = topicLevels[0]
            if action == '@set':
                location.pop()
                self._set(msg.topic, location, messageFormat, payload)
            else:
                self.log.error('Method \"' + action + '\" not supported!')
        except Exception as exception:
            self.log.error(u'Exception :' + exception.message)
            traceback.print_exc()

    def subscribeToSetCommands(self):
        (result, mid) = self._client.subscribe(u'@set/' + self.getUuid().toString() + '/#', 1)
        return True if result == self._client.MQTT_ERR_SUCCESS else False

    def addNode(self, nodeName, clsOrObject):
        if nodeName != '' and clsOrObject != None:
            node = None

            self.log.debug('Adding node %s' % nodeName)

            # Add node to endpoint
            if isinstance(clsOrObject, CloudioNode):
                node = clsOrObject
                pass  # All right. We have the needed object
            else:
                raise RuntimeError(u'Wrong cloud.iO object type')

            if node:
                # We got an object
                node.setName(nodeName)
                node.setParentNodeContainer(self)

                assert not nodeName in self.nodes, u'Node with given name already present!'
                self.nodes[nodeName] = node

                # If the endpoint is online, send node add message
                if self.isOnline():
                    data = self.messageFormat.serializeNode(node)
                    self._client.publish(u'@nodeAdded/' + node.getUuid().toString(), data, 1, False)
                else:
                    self.log.info(u'Not sending \'@nodeAdded\' message. No connection to broker!')

    def getNode(self, nodeName):
        """Returns the node identified by the given name
        :param nodeName The Name of the node
        :type nodeName str
        """
        return self.nodes.get(nodeName, None)

    def _set(self, topic, location, messageFormat, data):
        """Assigns a new value to a cloud.iO attribute.

        :param topic: Topic representing the attribute
        :param location: Location stack
        :type location list
        :param messageFormat: Message format according to the data parameter
        :param data: Contains among other things the value to be assigned
        :return:
        """
        # The path to the location must be start with the actual UUID of the endpoint.
        if location and self.uuid == location.pop() and \
           location and 'nodes' == location.pop() and \
           location:
            # Get the node with the name according to the topic
            node = self.nodes.get(location[-1])
            if node:
                location.pop()
                # Get the attribute reference
                attribute = node.findAttribute(location)
                if attribute:
                    # Deserialize the message into the attribute
                    messageFormat.deserializeAttribute(data, attribute)
                else:
                    self.log.error('Attribute \"' + location[0] + '\" in node \"' + node.getName() + '\" not found!')
            else:
                self.log.error('Node \"' + location.pop() + '\" not found!')
        else:
            self.log.error('Invalid topic: ' + topic)

    ######################################################################
    # Interface implementations
    #
    def getUuid(self):
        return TopicUuid(self)

    def getName(self):
        return self.uuid

    def setName(self, name):
        raise CloudioModificationException(u'CloudioEndpoint name can not be changed!')

    def attributeHasChangedByEndpoint(self, attribute):
        """
        :param attribute:
        :type attribute: CloudioAttribute
        :return:
        """
        # Create the MQTT message using the given message format.
        data = self.messageFormat.serializeAttribute(attribute)

        messageQueued = False
        if self.isOnline():
            try:
                messageQueued = self._client.publish(u'@update/' + attribute.getUuid().toString(), data, 1, False)
            except Exception as exception:
                self.log.error(u'Exception :' + exception.message)

        # If the message could not be send for any reason, add the message to the pending
        # updates persistence if available.
        if not messageQueued and self.persistence:
            try:
                self.persistence.put('PendingUpdate-' + attribute.getUuid().toString().replace('/', ';')
                                     + '-' + str(TimeStampProvider.getTimeInMilliseconds()),
                                     PendingUpdate(data))
            except Exception as exception:
                self.log.error(u'Exception :' + exception.message)
                traceback.print_exc()

        # Check if there are messages in the persistence store to send
        if messageQueued and self.persistence and len(self.persistence.keys()) > 0:
            # Try to send stored messages to cloud.iO
            self._purgePersistentDataStore()

    def attributeHasChangedByCloud(self, attribute):
        """Informs the endpoint that an underlying attribute has changed (initiated from the cloud).

        Attribute changes initiated from the cloud (@set) are directly received
        by the concerning cloud.iO attribute. The cloud.iO attribute forwards the information
        up to the parents till the endpoint.
        """
        pass

    def _onConnected(self):
        """This callback is called after the MQTT client has successfully connected to cloud.iO.
        """
        # Announce our presence to the broker
        # self.announce()
        # It is too early here because the endpoint model
        # is not loaded at this moment

        success = self.subscribeToSetCommands()
        if not success:
            self.log.critical('Could not subscribe to @set topic!')

        # Try to send stored messages to cloud.iO
        # self._purgePersistentDataStore()
        # It may not be a good idea to send this data to cloud.iO using
        # the connection thread!

        self._endPointIsReady = True

        time.sleep(4)  # Give the clients time to connect to cloud.iO and to setup the mqtt queue

    def _onConnectionThreadFinished(self):
        self.log.info('Connection thread finished')
        self.thread = None

    def isOnline(self):
        return self._client.isConnected() and self._endPointIsReady

    def announce(self):
        # Send birth message
        self.log.info(u'Sending birth message...')
        strMessage = self.messageFormat.serializeEndpoint(self)
        self._client.publish(u'@online/' + self.uuid, strMessage, 1, True)

    def _purgePersistentDataStore(self):
        """Tries to send stored messages to cloud.iO.
        """
        if self.persistence:
            print(str(len(self.persistence.keys())) + ' in persistence')
            for key in self.persistence.keys():
                if self.isOnline():
                    # Is it a pending update?
                    if key.startswith('PendingUpdate-'):
                        # Get the pending update persistent object from store
                        pendingUpdate = self.persistence.get(key)

                        if pendingUpdate is not None:
                            print('Copy pers: ' + key + ': ' + pendingUpdate.get_header_bytes())

                            # Get the uuid of the endpoint
                            uuid = pendingUpdate.get_uuid_from_persistence_key(key)

                            # Try to send the update to the broker and remove it from the storage
                            if self._client.publish(u'@update/' + uuid, pendingUpdate.get_header_bytes(), 1, False):
                                # Remove key from store
                                self.persistence.remove(key)
                    time.sleep(0)   # Give other threads time to do its job
                else:
                    break


if __name__ == '__main__':
    pass
