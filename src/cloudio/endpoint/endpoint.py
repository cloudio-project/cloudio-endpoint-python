#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import os
from dataclasses import dataclass

import cloudio.common.mqtt as mqtt
import cloudio.common.utils.timestamp_helpers as TimeStampProvider
import time
from cloudio.common.core.threaded import Threaded
from cloudio.common.utils import path_helpers
from cloudio.common.utils.resource_loader import ResourceLoader
from cloudio.endpoint.exception.cloudio_modification_exception import CloudioModificationException
from cloudio.endpoint.exception.invalid_property_exception import InvalidPropertyException
from cloudio.endpoint.interface.message_format import CloudioMessageFormat
from cloudio.endpoint.interface.node_container import CloudioNodeContainer
from cloudio.endpoint.message_format.factory import MessageFormatFactory
from cloudio.endpoint.message_format.json_format import JsonMessageFormat
from cloudio.endpoint.properties_endpoint_configuration import PropertiesEndpointConfiguration
from cloudio.endpoint.topicuuid import TopicUuid

version = ''
# Get endpoint python version info from init file
with open(os.path.dirname(os.path.realpath(__file__)) + '/version.py') as vf:
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


@dataclass
class MqttMessage:
    """Data structure used internally by CloudioEndpoint class.
    """
    topic: str
    payload: str
    timestamp: int = 0  # Time in milliseconds
    qos: int = 1
    retain: bool = False


class CloudioEndpoint(Threaded, CloudioNodeContainer):
    """The cloud.iO endpoint.

    Contains among other things the mqtt client to talk to the cloudio broker.
    """

    # Constants ######################################################################################
    MQTT_HOST_URI_PROPERTY = 'ch.hevs.cloudio.endpoint.hostUri'
    MQTT_PERSISTENCE_MEMORY = 'memory'
    MQTT_PERSISTENCE_FILE = 'file'
    MQTT_PERSISTENCE_NONE = 'none'
    MQTT_PERSISTENCE_PROPERTY = 'ch.hevs.cloudio.endpoint.persistence'
    MQTT_PERSISTENCE_DEFAULT = MQTT_PERSISTENCE_FILE
    MQTT_PERSISTENCE_LOCATION = 'ch.hevs.cloudio.endpoint.persistenceLocation'

    CERT_AUTHORITY_FILE_PROPERTY = 'ch.hevs.cloudio.endpoint.ssl.authorityCert'
    ENDPOINT_IDENTITY_TLS_VERSION_PROPERTY = 'ch.hevs.cloudio.endpoint.ssl.version'  # tlsv1.0 or tlsv1.2
    ENDPOINT_IDENTITY_FILE_PROPERTY = 'ch.hevs.cloudio.endpoint.ssl.clientCert'  # PKCS12 based file (*.p12)
    ENDPOINT_IDENTITY_CERT_FILE_PROPERTY = 'ch.hevs.cloudio.endpoint.ssl.clientCert'  # (*.pem)
    ENDPOINT_IDENTITY_KEY_FILE_PROPERTY = 'ch.hevs.cloudio.endpoint.ssl.clientKey'  # (*.pem)

    log = logging.getLogger(__name__)

    def __init__(self, uuid, configuration=None, locations: str or list = None):
        super(CloudioEndpoint, self).__init__()

        from cloudio.endpoint.node import CloudioNode

        self._end_point_is_ready = False  # Set to true after connection and subscription

        self.uuid = uuid  # type: str
        self.nodes = {}  # type: dict[CloudioNode]
        self.clean_session = True
        self.message_format = None  # type: CloudioMessageFormat
        self.persistence = None  # type: MqttClientPersistence
        self._publish_message = list()  # type: list[MqttMessage]
        self._received_message = list()  # type: list[mqtt.MQTTMessage]

        # Used for debug/testing purpose only
        self._published_not_acknowledged_message = dict()  # type: dict[mqtt.MQTTMessageInfo]
        self._published_not_acknowledged_high_water_mark = 0

        self.log.debug('Creating Endpoint %s' % uuid)

        # Check if a configuration with properties is given
        if configuration is None:
            properties_file = self.uuid + '.properties'
            ext_locations = ['home:' + '/.config/cloud.io/', 'file:/etc/cloud.io/']
            if locations:
                if isinstance(locations, str):
                    ext_locations = [locations, ] + ext_locations
                else:
                    ext_locations = locations + ext_locations

            # Try to load properties using a config file
            properties = ResourceLoader.load_from_locations(properties_file,
                                                            ext_locations)
            if properties:
                configuration = PropertiesEndpointConfiguration(properties)
            else:
                message = 'Could not find properties file \'' + properties_file + '\' in the following locations:\n'
                for location in ext_locations:
                    message += ' - ' + location + '\n'
                exit(message)

        self._retry_interval = 10  # Connect retry interval in seconds
        self.message_format = JsonMessageFormat()

        # Check if 'host' property is present in config file
        host = configuration.get_property(self.MQTT_HOST_URI_PROPERTY)
        if host == '':
            exit('Missing mandatory property "' + self.MQTT_HOST_URI_PROPERTY + '"')

        # Create persistence object.
        persistence_type = configuration.get_property(self.MQTT_PERSISTENCE_PROPERTY, self.MQTT_PERSISTENCE_DEFAULT)
        if persistence_type == self.MQTT_PERSISTENCE_MEMORY:
            self.persistence = mqtt.MqttMemoryPersistence()
        elif persistence_type == self.MQTT_PERSISTENCE_FILE:
            persistenceLocation = configuration.get_property(self.MQTT_PERSISTENCE_LOCATION)
            self.persistence = mqtt.MqttDefaultFilePersistence(directory=persistenceLocation)
        elif persistence_type == self.MQTT_PERSISTENCE_NONE:
            self.persistence = None
        else:
            raise InvalidPropertyException('Unknown persistence implementation ' +
                                           '(ch.hevs.cloudio.endpoint.persistence): ' +
                                           '\'' + persistence_type + '\'')
        # Open peristence storage
        if self.persistence:
            self.persistence.open(client_id=self.uuid, server_uri=host)

        self.options = mqtt.MqttConnectOptions()

        # Last will is a message with the UUID of the endpoint and no payload.
        will_message = 'DEAD'
        self.options.set_will('@offline/' + uuid, will_message, 1, False)

        self.options.ca_file = configuration.get_property(self.CERT_AUTHORITY_FILE_PROPERTY, None)
        self.options.client_cert_file = configuration.get_property(self.ENDPOINT_IDENTITY_CERT_FILE_PROPERTY, None)
        self.options.client_key_file = configuration.get_property(self.ENDPOINT_IDENTITY_KEY_FILE_PROPERTY, None)
        self.options.username = configuration.get_property('username')
        self.options.password = configuration.get_property('password')
        self.options.tls_version = configuration.get_property(self.ENDPOINT_IDENTITY_TLS_VERSION_PROPERTY, 'tlsv1.2')

        # Make path usable
        self.options.ca_file = path_helpers.prettify(self.options.ca_file)
        self.options.client_cert_file = path_helpers.prettify(self.options.client_cert_file)
        self.options.client_key_file = path_helpers.prettify(self.options.client_key_file)

        self._client = mqtt.MqttReconnectClient(host,
                                                client_id=self.uuid + '-endpoint-',
                                                clean_session=self.clean_session,
                                                options=self.options)
        # Register callback method for connection established
        self._client.set_on_connected_callback(self._on_connected)
        # Register callback method to be called when receiving a message over MQTT
        self._client.set_on_message_callback(self._onMessageArrived)
        # Register callback method to get notified after message was published (received by the MQTT broker)
        self._client.set_on_message_published(self._on_message_published)
        # Start the client
        self._client.start()

        # Setup and start internal _thread
        self.setup_thread(name=uuid)
        self.start_thread()

    def _run(self):
        while self._thread_should_run:

            self._process_received_messages()
            self._process_publish_messages()

            self._check_published_not_acknowledged_container()
            self._check_presistent_data_store()

            # Wait until next interval begins
            if self._thread_should_run:
                self._thread_sleep_interval()

        self._thread_left_run_loop = True

    def close(self):
        # Stop Mqtt client
        self._client.stop()

    def _publish(self, topic, payload, timestamp=0, qos=1, retain=False):

        if timestamp == 0:
            timestamp = TimeStampProvider.get_time_in_milliseconds()

        msg = MqttMessage(topic, payload, timestamp=timestamp, qos=qos, retain=retain)
        self._publish_message.append(msg)

        # Wake up endpoint _thread. It will publish the queued message. See _process_publish_messages()
        self.wakeup_thread()

    def _process_publish_messages(self):
        """Processes message ready to be send to cloud.iO.

        In case the MQTT broker is not available, the messages are stored in the
        persistent data store.
        """
        while len(self._publish_message):
            # Get next message
            msg = self._publish_message.pop(0)

            # Publish message via the MQTT client
            message_info = self._client.publish(msg.topic, msg.payload, msg.qos, msg.retain)

            if message_info.rc == self._client.MQTT_ERR_SUCCESS:
                # Add message to published (but not acknowledged) messages
                self._published_not_acknowledged_message[message_info.mid] = msg
            else:
                # Could not transmit. Add it to data store
                self._put_persistent_data_store(msg.topic, msg.payload, msg.timestamp)

    def _check_published_not_acknowledged_container(self):
        msg_count = len(self._published_not_acknowledged_message)
        if msg_count > 0:
            self._published_not_acknowledged_high_water_mark = max(self._published_not_acknowledged_high_water_mark,
                                                                   msg_count)
            # if msg_count > 1:
            #     print('Not published messages: {} (max: {})'.format(msg_count,
            #                                                        self._published_not_acknowledged_high_water_mark))

    def _onMessageArrived(self, client, userdata, msg):
        # Called by the MQTT client _thread!

        # print(msg.topic + ': ' + str(msg.payload))

        self._received_message.append(msg)
        # Tell endpoint _thread it can process a message
        self.wakeup_thread()

    def _process_received_messages(self):
        while len(self._received_message):
            msg = self._received_message.pop(0)
            self._processReceivedMessage(msg)

    def _processReceivedMessage(self, msg) -> bool:
        try:
            # Need to convert from bytes to string
            payload = msg.payload.decode('utf-8')

            # First determine the message format (first byte identifies the message format).
            message_format = MessageFormatFactory.messageFormat(payload[0])
            if message_format == None:
                self.log.error('Message-format ' + payload[0] + " not supported!")
                return

            topic_levels = self.get_topic_levels(msg.topic)
            # Create attribute location path stack.
            location = []
            for topicLevel in topic_levels:
                location.insert(0, topicLevel)

            # Read the action tag from the topic
            action = topic_levels[0]
            if action == '@set':
                location.pop()
                self._set(msg.topic, location, message_format, payload)
            else:
                self.log.error('Method \"' + action + '\" not supported!')
        except Exception as exception:
            self.log.error(exception, exc_info=True)

    def _on_message_published(self, client, userdata, mid):
        # Called by the MQTT client _thread!

        # if mid % 100 == 0:
            # print('Msg #{} sent'.format(mid))

        # Remove the sent message from the list
        if mid in self._published_not_acknowledged_message:
            del self._published_not_acknowledged_message[mid]
        else:
            # print('Warning: #{} not in published msgs!'.format(mid))
            pass

        msg_count = len(self._published_not_acknowledged_message)
        if msg_count > 0:
            self._published_not_acknowledged_high_water_mark = max(self._published_not_acknowledged_high_water_mark,
                                                                   msg_count)

    def subscribe_to_set_commands(self):
        (result, mid) = self._client.subscribe('@set/' + self.get_uuid().to_string() + '/#', 1)
        return True if result == self._client.MQTT_ERR_SUCCESS else False

    def add_node(self, node_name, cls_or_object):
        from cloudio.endpoint.node import CloudioNode

        if node_name != '' and cls_or_object != None:
            node = None

            self.log.debug('Adding node %s' % node_name)

            # Add node to endpoint
            if isinstance(cls_or_object, CloudioNode):
                node = cls_or_object
                pass  # All right. We have the needed object
            else:
                raise RuntimeError('Wrong cloud.iO object type')

            if node:
                # We got an object
                node.set_name(node_name)
                node.set_parent_node_container(self)

                assert not node_name in self.nodes, 'Node with given name already present!'
                self.nodes[node_name] = node

                # If the endpoint is online, send node add message
                if self.is_online():
                    data = self.message_format.serialize_node(node)
                    self._publish('@nodeAdded/' + node.get_uuid().to_string(), data)
                else:
                    self.log.info('Not sending \'@nodeAdded\' message. No connection to broker!')

    def get_node(self, node_name):
        """Returns the node identified by the given name
        :param node_name The Name of the node
        :type node_name str
        """
        return self.nodes.get(node_name, None)

    def _set(self, topic, location, message_format, data):
        """Assigns a new value to a cloud.iO attribute.

        :param topic: Topic representing the attribute
        :param location: Location stack
        :type location list
        :param message_format: Message format according to the data parameter
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
                attribute = node.find_attribute(location)
                if attribute:
                    # Deserialize the message into the attribute
                    message_format.deserialize_attribute(data, attribute)
                else:
                    self.log.error('Attribute \"' + location[0] + '\" in node \"' + node.get_name() + '\" not found!')
            else:
                self.log.error('Node \"' + location.pop() + '\" not found!')
        else:
            self.log.error('Invalid topic: ' + topic)

    ######################################################################
    # Interface implementations
    #
    def get_uuid(self):
        return TopicUuid(self)

    def get_name(self):
        return self.uuid

    def set_name(self, name):
        raise CloudioModificationException('CloudioEndpoint name can not be changed!')

    def attribute_has_changed_by_endpoint(self, attribute):
        """
        :param attribute:
        :type attribute: CloudioAttribute
        """

        try:
            # Create the MQTT message using the given message format.
            topic = '@update/' + attribute.get_uuid().to_string()
            payload = self.message_format.serialize_attribute(attribute)

            self._publish(topic, payload, timestamp=attribute.get_timestamp())
        except Exception as exception:
            self.log.error(exception, exc_info=True)

    def attribute_has_changed_by_cloud(self, attribute):
        """Informs the endpoint that an underlying attribute has changed (initiated from the cloud).

        Attribute changes initiated from the cloud (@set) are directly received
        by the concerning cloud.iO attribute. The cloud.iO attribute forwards the information
        up to the parents till the endpoint.
        """
        pass

    def _on_connected(self):
        """This callback is called after the MQTT client has successfully connected to cloud.iO.
        """
        # Announce our presence to the broker
        # self.announce()
        # It is too early here because the endpoint model
        # is not loaded at this moment

        success = self.subscribe_to_set_commands()
        if not success:
            self.log.critical('Could not subscribe to @set topic!')

        # Try to send stored messages to cloud.iO
        # self._purgePersistentDataStore()
        # It may not be a good idea to send this data to cloud.iO using
        # the connection _thread!

        self._end_point_is_ready = True

        time.sleep(4)  # Give the clients time to connect to cloud.iO and to setup the mqtt queue

    def _on_connection_thread_finished(self):
        self.log.info('Connection _thread finished')
        self.thread = None

    def is_online(self):
        return self._client.is_connected() and self._end_point_is_ready

    def announce(self):
        # Send birth message
        self.log.info('Sending birth message...')
        str_message = self.message_format.serialize_endpoint(self)
        self._publish('@online/' + self.uuid, str_message, retain=True)

    @staticmethod
    def get_action(topic: str) -> str:
        """Extracts the action from a topic.

        Ex. topic: '@update/CrazyFrogEndpoint/nodes/CrazyFrog/objects/properties/attributes/_sinus'
        returns '@update'
        """
        topic_levels = topic.split('/')

        # Read the action tag from the topic
        action = topic_levels[0]
        return action

    @staticmethod
    def get_topic_levels(topic: str) -> list[str]:
        """Breaks the topic into its pieces.
        """
        topic_levels = topic.split('/')
        return topic_levels

    def _check_presistent_data_store(self):
        # Check if there are messages in the persistence store
        if self.is_online() and self.persistence and len(self.persistence.keys()) > 0:
            # Try to send stored messages to cloud.iO
            self._purgePersistentDataStore()

    def _put_persistent_data_store(self, topic, payload, timestamp):
        # If the message could not be send for any reason, add the message to the pending
        # updates persistence if available.
        if self.persistence:
            if timestamp == 0:
                timestamp = TimeStampProvider.get_time_in_milliseconds()

            action = self.get_action(topic)
            topic_levels = self.get_topic_levels(topic)
            topic_levels.pop(0)  # Remove action

            try:
                if action == '@update':
                    msg_id = 'PendingUpdate-' + ';'.join(topic_levels) + '-' + str(int(timestamp))
                    self.persistence.put(msg_id, mqtt.PendingUpdate(payload))
                elif action == '@nodeAdded':
                    msg_id = 'PendingNodeAdded-' + ';'.join(topic_levels) + '-' + str(int(timestamp))
                    self.persistence.put(msg_id, mqtt.PendingUpdate(payload))
                else:
                    raise Exception('Unknown action type!')
            except Exception as exception:
                    self.log.error(exception, exc_info=True)

    def _purgePersistentDataStore(self):
        """Tries to send stored messages to cloud.iO.
        """
        if self.persistence:
            print(str(len(self.persistence.keys())) + ' in persistence')

            action_map = {
                'PendingUpdate-': '@update',
                'PendingNodeAdded-': '@nodeAdded'}

            for key in self.persistence.keys():
                if self.is_online():
                    for pending_data_type, action in action_map.items():
                        # Check pending data type
                        if key.startswith(pending_data_type):
                            # Get the pending update persistent object from store
                            pending_update = self.persistence.get(key)

                            if pending_update is not None:
                                print('Copy pers: ' + key + ': ' + pending_update.get_data())

                                # Get the uuid of the endpoint
                                uuid = pending_update.get_uuid_from_persistence_key(key)

                                # Try to send the update to the broker and remove it from the storage
                                topic = action + '/' + uuid
                                self._publish(topic, pending_update.get_data())

                                # Remove key from store
                                self.persistence.remove(key)
                            break
                    time.sleep(0)  # Give other threads time to do its job
                else:
                    break


if __name__ == '__main__':
    pass
