# -*- coding: utf-8 -*-

from threading import Thread
import time
import logging
import traceback
import utils.timestamp as TimeStampProvider
from .mqtt_helpers import MqttAsyncClient, MqttConnectOptions, MqttClientPersistence
from .cloudio_node import CloudioNode
from .properties_endpoint_configuration import PropertiesEndpointConfiguration
from .interface.node_container import CloudioNodeContainer
from .interface.message_format import CloudioMessageFormat
from .message_format.factory import MessageFormatFactory
from exception.cloudio_modification_exception import CloudioModificationException
from utils.resource_loader import ResourceLoader
from message_format.json_format import JsonMessageFormat
from utils import path_helpers
from pending_update import PendingUpdate
from topicuuid import TopicUuid

# Enable logging
logging.basicConfig(format='%(asctime)s.%(msecs)03d - %(name)s - %(levelname)s - %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S',
                    level=logging.DEBUG)
logging.getLogger(__name__).setLevel(logging.CRITICAL)

class CloudioEndpoint(CloudioNodeContainer):
    """Internal Endpoint structure used by CloudioEndpoint.

    Contains among other things the mqtt client to talk to the cloudio broker.
    """

    # Constants ######################################################################################
    MQTT_HOST_URI_PROPERTY = u'ch.hevs.cloudio.endpoint.hostUri'

    CERT_AUTHORITY_FILE_PROPERTY = u'ch.hevs.cloudio.endpoint.ssl.authorityCert'

    ENDPOINT_IDENTITY_FILE_PROPERTY = u'ch.hevs.cloudio.endpoint.ssl.clientCert'        # PKCS12 based file (*.p12)
    ENDPOINT_IDENTITY_CERT_FILE_PROPERTY = u'ch.hevs.cloudio.endpoint.ssl.clientCert'   # (*.pem)
    ENDPOINT_IDENTITY_KEY_FILE_PROPERTY = u'ch.hevs.cloudio.endpoint.ssl.clientKey'     # (*.pem)

    log = logging.getLogger(__name__)

    def __init__(self, uuid, configuration=None):

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

        # Create persistence object.
        self.persistence = MqttClientPersistence()  # Temp

          # Check if 'host' property is present in config file
        host = configuration.getProperty(self.MQTT_HOST_URI_PROPERTY)
        if host == '':
            exit('Missing mandatory property "' + self.MQTT_HOST_URI_PROPERTY + '"')

        self.options = MqttConnectOptions()

        # Last will is a message with the UUID of the endpoint and no payload.
        willMessage = bytearray()
        willMessage += 'DEAD'
        self.options.setWill(u'@offline/' + uuid, willMessage, 1, False)

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
        # Register callback method to be called when receiving a message over MQTT
        self.mqtt.setOnMessageCallback(self._onMessageArrived)

        self.thread = Thread(target=self.run, name='cloudio-endpoint-' + self.uuid)
        # Close thread as soon as main thread exits
        self.thread.setDaemon(True)
        self.thread.start()

    def _onMessageArrived(self, client, userdata, msg):
        #print msg.topic + ': ' + str(msg.payload)
        try:
            # First determine the message format (first byte identifies the message format).
            messageFormat = MessageFormatFactory.messageFormat(msg.payload[0])
            if messageFormat == None:
                self.log.error('Message-format ' + msg.payload[0] + " not supported!")
                return

             # Create attribute location path stack.
            location = msg.topic.split('/')

            # Read the action tag from the topic
            action = location[0]
            if action == '@set':
                location.pop(0)
                self._set(msg.topic, location, messageFormat, msg.payload)
            else:
                self.log.error('Method \"' + location[0] + '\" not supported!')
        except Exception as exception:
            self.log.error(u'Exception :' + exception.message)
            traceback.print_exc()

    def subscribeToSetCommands(self):
        (result, mid) = self.mqtt.subscribe("@set/" + self.getUuid().toString() + "/#", 1)
        return True if result == self.mqtt.MQTT_ERR_SUCCESS else False

    def addNode(self, nodeName, clsOrObject):
        if nodeName != '' and clsOrObject != None:
            node = None

            self.log.debug('Adding node %s' % nodeName)

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
                    self.mqtt.publish(u'@nodeAdded/' + node.getUuid().toString(), data, 1, False)
                else:
                    self.log.info(u'Not sending \'@nodeAdded\' message. No connection to broker!')

    def getNode(self, nodeName):
        return self.nodes[nodeName]

    def _set(self, topic, location, messageFormat, data):
        pass

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

        messageSend = False
        if self.mqtt.isConnected():
            try:
                self.mqtt.publish(u'@update/' + attribute.getUuid().toString(), data, 1, False)
                messageSend = True
            except Exception as exception:
                self.log.error(u'Exception :' + exception.message)

        # If the message could not be send for any reason, add the message to the pending
        # updates persistence if available.
        if not messageSend and self.persistence:
            try:
                self.persistence.put("PendingUpdate-" + attribute.getUuid().toString().replace("/", ";")
                                        + "-" + TimeStampProvider.getTimeInMilliseconds(),
                                     PendingUpdate(data))
            except Exception as exception:
                self.log.error(u'Exception :' + exception.message)
                traceback.print_exc()

    def attributeHasChangedByCloud(self, attribute):
        self.attributeHasChangedByEndpoint(attribute)

    ######################################################################
    # Active part
    #
    def run(self):
        """Called by the internal thread"""

        print u'Cloudio endpoint thread running...'

        while not self.mqtt.isConnected():
            try:
                self.mqtt.connect(self.options)
            except Exception as exception:
                traceback.print_exc()
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

        self.log.info(u'Connected to cloud.iO broker')

        # Announce our presence to the broker
        #self.announce()

        success = self.subscribeToSetCommands()
        if not success:
            self.log.critical('Could not subscribe to @set topic!')

        # If we arrive here, we are online, so we can inform listeners about that and stop the connecting thread
#        self.mqtt.setCallback(self)

    def isOnline(self):
        return self.mqtt.isConnected()

    def announce(self):
        # Send birth message
        self.log.info(u'Sending birth message...')
        strMessage = self.messageFormat.serializeEndpoint(self)
        self.mqtt.publish(u'@online/' + self.uuid, strMessage, 1, True)
