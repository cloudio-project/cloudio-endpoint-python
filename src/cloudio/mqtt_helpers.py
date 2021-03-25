# -*- coding: utf-8 -*-

import os
import time
from threading import Thread, RLock, Event, current_thread
import logging
import traceback
from abc import ABCMeta
import paho.mqtt.client as mqtt  # pip install paho-mqtt
import ssl
import uuid

from utils import path_helpers
from .pending_update import PendingUpdate

# Set logging level
logging.getLogger('cloudio.mqttasyncclient').setLevel(logging.INFO)  # DEBUG, INFO, WARNING, ERROR, CRITICAL
logging.getLogger('cloudio.mqttreconnectclient').setLevel(logging.INFO)  # DEBUG, INFO, WARNING, ERROR, CRITICAL


class MqttAsyncClient(object):
    """Mimic the behavior of the java.MqttAsyncClient class"""

    # Errors from mqtt module - mirrored into this class
    MQTT_ERR_SUCCESS = mqtt.MQTT_ERR_SUCCESS
    MQTT_ERR_NO_CONN = mqtt.MQTT_ERR_NO_CONN

    log = logging.getLogger('cloudio.mqttasyncclient')

    def __init__(self, host, client_id='', clean_session=True):
        self._isConnected = False
        self._host = host
        self._onConnectCallback = None
        self._onDisconnectCallback = None
        self._onMessageCallback = None
        self._client = None
        self._clientLock = RLock()  # Protects access to _client attribute

        # Store mqtt client parameter for potential later reconnection
        # to cloud.iO
        self._clientClientId = client_id
        self._clientCleanSession = clean_session

    def _create_mqtt_client(self):
        self._clientLock.acquire()
        if self._client is None:
            if self._clientClientId:
                self._client = mqtt.Client(client_id=self._clientClientId,
                                           clean_session=self._clientCleanSession)
            else:
                self._client = mqtt.Client()

            self._client.on_connect = self.on_connect
            self._client.on_disconnect = self.on_disconnect
            self._client.on_message = self.on_message
        self._clientLock.release()

    def set_on_connect_callback(self, on_connect_callback):
        self._onConnectCallback = on_connect_callback

    def set_on_disconnect_callback(self, on_disconnect_callback):
        self._onDisconnectCallback = on_disconnect_callback

    def set_on_message_callback(self, on_message_callback):
        self._onMessageCallback = on_message_callback

    def connect(self, options):
        port = options.port if options.port else 1883  # Default port without ssl

        if options.caFile:
            # Check if file exists
            if not os.path.isfile(options.caFile):
                raise RuntimeError(u'CA file \'%s\' does not exist!' % options.caFile)

        client_cert_file = None
        if options.clientCertFile:
            # Check if file exists
            if not os.path.isfile(options.clientCertFile):
                raise RuntimeError(u'Client certificate file \'%s\' does not exist!' % options.clientCertFile)
            else:
                client_cert_file = options.clientCertFile

        client_key_file = None
        if options.clientKeyFile:
            # Check if file exists
            if not os.path.isfile(options.clientKeyFile):
                raise RuntimeError(u'Client private key file \'%s\' does not exist!' % options.clientKeyFile)
            else:
                client_key_file = options.clientKeyFile

        # Check which TSL protocol version should be used
        try:
            tls_version = ssl.PROTOCOL_TLSv1_2
        except Exception:
            tls_version = ssl.PROTOCOL_TLSv1
        if options.tlsVersion:
            if options.tlsVersion.lower() in ('tlsv1', 'tlsv1.0'):
                tls_version = ssl.PROTOCOL_TLSv1

        self._clientLock.acquire()  # Protect _client attribute

        # Create MQTT client if necessary
        self._create_mqtt_client()

        if options.will:
            self._client.will_set(options.will['topic'],
                                  options.will['message'],
                                  options.will['qos'],
                                  options.will['retained'])
        if self._client:
            if options.caFile:
                port = options.port if options.port else 8883       # Default port with ssl
                self._client.tls_set(options.caFile,                # CA certificate
                                     certfile=client_cert_file,     # Client certificate
                                     keyfile=client_key_file,       # Client private key
                                     tls_version=tls_version,       # ssl.PROTOCOL_TLSv1, ssl.PROTOCOL_TLSv1_2
                                     ciphers=None)                  # None, 'ALL', 'TLSv1.2', 'TLSv1.0'
                self._client.tls_insecure_set(True)     # True: No verification of the server hostname in
                                                        # the server certificate
            else:
                self.log.error('No CA file provided. Connection attempt likely to fail!')

            # Check if username and password is provided
            if options.username:
                password = options.password
                if not options.password:
                    # paho client v1.3 and higher do no more accept '' as empty string. Need None
                    password = None
                self._client.username_pw_set(options.username, password=password)

            self._client.connect(self._host, port=port)
            self._client.loop_start()
        self._clientLock.release()
        time.sleep(1)  # Wait a bit for the callback on_connect to be called

    def disconnect(self, force_client_disconnect=True):
        """Disconnects MQTT client

        In case to let MQTT client die silently, call force_client_disconnect parameter with
        'false' value. In this case no disconnect callback method is called.

        ::param force_client_disconnect Set to true to call also MQTT clients disconnect method. Default: true
        :type force_client_disconnect bool
        :return None
        :rtype: None
        """
        self._clientLock.acquire()
        # Stop MQTT client if still running
        if self._client:
            if force_client_disconnect:
                self._client.on_disconnect = None  # Want get a disconnect callback call
                self._client.disconnect()
            self._client.loop_stop()
            self._client = None

        self._isConnected = False

        self._clientLock.release()

    def is_connected(self):
        return self._client and self._isConnected

    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            self._isConnected = True
            self.log.info(u'Connection to cloud.iO broker established')
            if self._onConnectCallback:
                self._onConnectCallback()
        else:
            if rc == 1:
                self.log.error(u'Connection refused - incorrect protocol version')
            elif rc == 2:
                self.log.error(u'Connection refused - invalid client identifier')
            elif rc == 3:
                self.log.error(u'Connection refused - server unavailable')
            elif rc == 4:
                self.log.error(u'Connection refused - bad username or password')
            elif rc == 5:
                self.log.error(u'Connection refused - not authorised')
            else:
                self.log.error(u'Connection refused - unknown reason')

    def on_disconnect(self, client, userdata, rc):
        self.log.info('Disconnect: %d' % rc)

        # Caution:
        # Do not call self.disconnect() here. It will kill the thread calling this
        # method and any subsequent code will not be executed!
        # self.disconnect()

        # Notify container class if disconnect callback
        # was registered.
        if self._onDisconnectCallback:
            self._onDisconnectCallback(rc)
        else:
            self.log.warning('On disconnect callback not set')

    def on_message(self, client, userdata, msg):
        # Delegate to container class
        if self._onMessageCallback:
            self._onMessageCallback(client, userdata, msg)

    def publish(self, topic, payload=None, qos=0, retain=False):
        if not self._client:
            return False

        timeout = 0.1
        message_info = self._client.publish(topic, payload, qos, retain)

        # Cannot use message_info.wait_for_publish() because it is blocking and
        # has no timeout parameter
        # message_info.wait_for_publish()
        #
        # Poll is_published() method
        while timeout > 0:
            if message_info.is_published():
                break
            timeout -= 0.005
            time.sleep(0.005)

        return message_info.rc == self.MQTT_ERR_SUCCESS

    def subscribe(self, topic, qos=0):
        if self._client:
            return self._client.subscribe(topic, qos)
        else:
            return self.MQTT_ERR_NO_CONN, None


class MqttReconnectClient(MqttAsyncClient):
    """Same as MqttAsyncClient, but adds reconnect feature.
    """

    log = logging.getLogger('cloudio.mqttreconnectclient')

    def __init__(self, host, client_id='', clean_session=True, options=None):
        MqttAsyncClient.__init__(self, host, client_id, clean_session)

        # options are not used by MqttAsyncClient store them in this class
        self._options = options
        self._onConnectedCallback = None
        self._onConnectionThreadFinishedCallback = None
        self._retryInterval = 10  # Connect retry interval in seconds
        self._autoReconnect = True
        self.thread = None
        self._connectTimeoutEvent = Event()
        self._connectionThreadLooping = True  # Set to false in case the connection thread should leave

        # Register callback method to be called when connection to cloud.iO gets established
        MqttAsyncClient.set_on_connect_callback(self, self._on_connect)

        # Register callback method to be called when connection to cloud.iO gets lost
        MqttAsyncClient.set_on_disconnect_callback(self, self._on_disconnect)

    def set_on_connect_callback(self, on_connect):
        assert False, u'Not allowed in this class!'

    def set_on_disconnect_callback(self, on_disconnect):
        assert False, u'Not allowed in this class!'

    def set_on_connected_callback(self, on_connected_callback):
        self._onConnectedCallback = on_connected_callback

    def set_on_connection_thread_finished_callback(self, on_connection_thread_finished_callback):
        self._onConnectionThreadFinishedCallback = on_connection_thread_finished_callback

    def start(self):
        self._start_connection_thread()

    def stop(self):
        self.log.info('Stopping MqttReconnectClient thread')
        self._autoReconnect = False
        self.disconnect()

    def _start_connection_thread(self):
        if self.thread is current_thread():
            # Do not restart myself!
            self.log.warning('Mqtt client connection thread is me! Not restarting myself!')
            return
        if self.thread and self.thread.is_alive():
            self.log.warning('Mqtt client connection thread already/still running!')
            return

        self._stop_connection_thread()

        self.log.info('Starting MqttReconnectClient thread')
        self.thread = Thread(target=self._run, name='mqtt-reconnect-client-' + self._clientClientId)
        # Close thread as soon as main thread exits
        self.thread.setDaemon(True)

        self._connectionThreadLooping = True
        self.thread.start()

    def _stop_connection_thread(self):
        self.log.info('Stopping MqttReconnectClient thread')
        if self.thread:
            try:
                self._connectionThreadLooping = False
                self.thread.join()
                self.thread = None
            except RuntimeError:
                self.log.error('Could not wait for connection thread')
                traceback.print_exc()

    def _on_connect(self):
        self._connectTimeoutEvent.set()  # Free the connection thread

    def _on_disconnect(self, rc):
        if self._autoReconnect:
            self._start_connection_thread()

    def _on_connected(self):
        if self._onConnectedCallback:
            self._onConnectedCallback()

    def _on_connection_thread_finished(self):
        if self._onConnectionThreadFinishedCallback:
            self._onConnectionThreadFinishedCallback()

    ######################################################################
    # Active part
    #
    def _run(self):
        """Called by the internal thread"""

        self.log.info(u'Mqtt client reconnect thread running...')

        # Close any previous connection
        self.disconnect()

        while not self.is_connected() and self._connectionThreadLooping:
            try:
                self._connectTimeoutEvent.clear()  # Reset connect timeout event prior to connect
                self.log.info(u'Trying to connect to cloud.iO...')
                self.connect(self._options)
            except Exception:
                traceback.print_exc()
                self.log.warning(u'Error during broker connect!')
                # Force disconnection of MQTT client
                self.disconnect(force_client_disconnect=False)
                # Do not exit here. Continue to try to connect

            # Check if thread should leave
            if not self._connectionThreadLooping:
                # Tell subscriber connection thread has finished
                self._on_connection_thread_finished()
                return

            if not self.is_connected():
                # If we should not retry, give up
                if self._retryInterval > 0:
                    # Wait until it is time for the next connect
                    self._connectTimeoutEvent.wait(self._retryInterval)

                # If we should not retry, give up
                if self._retryInterval == 0:
                    break

        self.log.info(u'Thread: Job done - leaving')

        if self.is_connected():
            self.log.info(u'Connected to cloud.iO broker')

            # Tell subscriber we are connected
            self._on_connected()

        # Tell subscriber connection thread has finished
        self._on_connection_thread_finished()


class MqttConnectOptions(object):
    def __init__(self):
        self.port = 8883    # Default port with ssl
        self.username = ''
        self.password = ''
        self.caFile = None  # type: str or None
        self.clientCertFile = None  # type: str or None
        self.clientKeyFile = None  # type: str or None
        self.tlsVersion = None  # type: str or None
        self.will = None  # type dict

    def set_will(self, topic, message, qos, retained):
        self.will = {
            'topic': topic,
            'message': message,
            'qos': qos,
            'retained': retained
        }


class MqttClientPersistence(object):
    """Mimic the behavior of the java.MqttClientPersistence interface.

    Compatible with MQTT v3.

    See: https://www.eclipse.org/paho/files/javadoc/org/eclipse/paho/client/mqttv3/MqttClientPersistence.html
    """

    __metaclass__ = ABCMeta

    def __init__(self):
        pass

    def clear(self):
        """Clears persistence, so that it no longer contains any persisted data.
        """
        pass

    def close(self):
        """Close the persistent store that was previously opened.
        """
        pass

    def contains_key(self, key):
        """Returns whether or not data is persisted using the specified key.

        :param key The key for data, which was used when originally saving it.
        :type key str
        :return True if key is present.
        """
        pass

    def get(self, key):
        """Gets the specified data out of the persistent store.

        :param key The key for the data to be removed from the store.
        :type key str
        :return The wanted data.
        """
        pass

    def keys(self):
        """Returns an Enumeration over the keys in this persistent data store.

        :return: generator
        """
        pass

    def open(self, client_id, server_uri):
        """Initialise the persistent store.

        Initialise the persistent store. If a persistent store exists for this client ID then open it,
        otherwise create a new one. If the persistent store is already open then just return. An application
        may use the same client ID to connect to many different servers, so the client ID in conjunction
        with the connection will uniquely identify the persistence store required.

        :param client_id The client for which the persistent store should be opened.
        :type client_id str
        :param server_uri The connection string as specified when the MQTT client instance was created.
        :type server_uri str
        """
        pass

    def put(self, key, persistable):
        """Puts the specified data into the persistent store.

        :param key The key for the data, which will be used later to retrieve it.
        :type key str
        :param persistable The data to persist.
        :type persistable bool
        """
        pass

    def remove(self, key):
        """Remove the data for the specified key.

        :param key The key associated to the data to remove.
        :type key str
        :return None
        """
        pass


class MemoryPersistence(MqttClientPersistence):
    """Persistance store that uses memory.
    """

    def __init__(self):
        super(MemoryPersistence, self).__init__()
        self._persistence = {}

    def open(self, client_id, server_uri):
        pass

    def close(self):
        self.clear()

    def put(self, key, persistable):
        self._persistence[key] = persistable

    def get(self, key):
        if key in self._persistence:
            return self._persistence[key]
        return None

    def contains_key(self, key):
        return True if key in self._persistence else False

    def keys(self):
        keys = []
        for key in self._persistence.keys():
            keys.append(key)
        return keys

    def remove(self, key):
        # Remove the key if it exist. If it does not exist
        # leave silently
        self._persistence.pop(key, None)

    def clear(self):
        self._persistence.clear()


class MqttDefaultFilePersistence(MqttClientPersistence):
    """Persistance store providing file based storage.
    """

    DEFAULT_DIRECTORY = '~/mqtt-persistence'

    def __init__(self, directory=None):
        """
        :param directory: Base directory where to store the persistent data
        """
        super(MqttDefaultFilePersistence, self).__init__()

        if directory is None or directory == '':
            directory = self.DEFAULT_DIRECTORY

        self._directory = path_helpers.prettify(directory)
        self._perClientIdAndServerUriDirectory = None  # type: str or None

        # Give a temporary unique storage name in case open() method does not get called
        self._perClientIdAndServerUriDirectory = str(uuid.uuid4())

        # Create base directory
        if not os.path.exists(self._directory):
            os.makedirs(self._directory)

    def open(self, client_id, server_uri):
        """Initialises the persistent store.

        :param client_id: MQTT client id
        :type client_id: str
        :param server_uri: Connection name to the server
        :type server_uri: str
        """
        self._perClientIdAndServerUriDirectory = client_id + '-' + server_uri

        # Remove some unwanted characters in sub-directory name
        self._perClientIdAndServerUriDirectory = self._perClientIdAndServerUriDirectory.replace('/', '')
        self._perClientIdAndServerUriDirectory = self._perClientIdAndServerUriDirectory.replace('\\', '')
        self._perClientIdAndServerUriDirectory = self._perClientIdAndServerUriDirectory.replace(':', '')
        self._perClientIdAndServerUriDirectory = self._perClientIdAndServerUriDirectory.replace(' ', '')

        # Create storage directory
        if not os.path.exists(self._storage_directory()):
            os.makedirs(self._storage_directory())

    def _storage_directory(self):
        return os.path.join(self._directory, self._perClientIdAndServerUriDirectory)

    def _key_file_name(self, key):
        return os.path.join(self._storage_directory(), key)

    def close(self):
        pass

    def put(self, key, persistable):
        """

        :param key:
        :param persistable:
        :type persistable: str or PendingUpdate
        :return:
        """

        # Convert string to PendingUpdate
        if isinstance(persistable, str):
            persistable = PendingUpdate(persistable)

        with open(self._key_file_name(key), mode='w') as file:
            # File is opened in binary mode. So bytes need to be stored
            # Convert str -> bytes
            file.write(persistable.get_data())

    def get(self, key):
        if os.path.exists(self._key_file_name(key)):
            with open(self._key_file_name(key), mode='r') as storage_file:
                return PendingUpdate(storage_file.read())
        return None

    def contains_key(self, key):
        return True if os.path.exists(self._key_file_name(key)) else False

    def keys(self):
        keys = next(os.walk(self._storage_directory()))[2]
        return keys

    def remove(self, key):
        # Remove the key if it exist. If it does not exist
        # leave silently
        key_file_name = self._key_file_name(key)
        try:
            if os.path.isfile(key_file_name):
                os.remove(key_file_name)
        except Exception:
            pass

    def clear(self):
        for key in os.listdir(self._storage_directory()):
            key_file_name = self._key_file_name(key)
            if os.path.isfile(key_file_name):
                os.remove(key_file_name)
