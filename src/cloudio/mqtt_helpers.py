# -*- coding: utf-8 -*-

from six import iterkeys
import os
import time
from threading import Thread, RLock, Event, current_thread
import logging
import traceback
from abc import ABCMeta, abstractmethod
import paho.mqtt.client as mqtt     # pip install paho-mqtt
import ssl
import uuid


from utils import path_helpers
from .pending_update import PendingUpdate

# Set logging level
logging.getLogger('cloudio.mqttasyncclient').setLevel(logging.INFO)         # DEBUG, INFO, WARNING, ERROR, CRITICAL
logging.getLogger('cloudio.mqttreconnectclient').setLevel(logging.INFO)     # DEBUG, INFO, WARNING, ERROR, CRITICAL

class MqttAsyncClient():
    """Mimic the behavior of the java.MqttAsyncClient class"""

    # Errors from mqtt module - mirrored into this class
    MQTT_ERR_SUCCESS = mqtt.MQTT_ERR_SUCCESS
    MQTT_ERR_NO_CONN = mqtt.MQTT_ERR_NO_CONN

    log = logging.getLogger('cloudio.mqttasyncclient')

    def __init__(self, host, clientId='', clean_session=True, options=None):
        self._isConnected = False
        self._host = host
        self._onConnectCallback = None
        self._onDisconnectCallback = None
        self._onMessageCallback = None
        self._client = None
        self._clientLock = RLock()   # Protects access to _client attribute

        # Store mqtt client parameter for potential later reconnection
        # to cloud.iO
        self._clientClientId = clientId
        self._clientCleanSession = clean_session

    def _createMqttClient(self):
        self._clientLock.acquire()
        if self._client is None:
            if self._clientClientId:
                self._client = mqtt.Client(client_id=self._clientClientId,
                                           clean_session=self._clientCleanSession)
            else:
                self._client = mqtt.Client()

            self._client.on_connect = self.onConnect
            self._client.on_disconnect = self.onDisconnect
            self._client.on_message = self.onMessage
        self._clientLock.release()

    def setOnConnectCallback(self, onConnectCallback):
        self._onConnectCallback = onConnectCallback

    def setOnDisconnectCallback(self, onDisconnectCallback):
        self._onDisconnectCallback = onDisconnectCallback

    def setOnMessageCallback(self, onMessageCallback):
        self._onMessageCallback = onMessageCallback

    def connect(self, options):
        port = 1883 # Default port without ssl

        if options._caFile:
            # Check if file exists
            if not os.path.isfile(options._caFile):
                raise RuntimeError(u'CA file \'%s\' does not exist!' % options._caFile)

        clientCertFile = None
        if options._clientCertFile:
            # Check if file exists
            if not os.path.isfile(options._clientCertFile):
                raise RuntimeError(u'Client certificate file \'%s\' does not exist!' % options._clientCertFile)
            else:
                clientCertFile = options._clientCertFile

        clientKeyFile = None
        if options._clientKeyFile:
            # Check if file exists
            if not os.path.isfile(options._clientKeyFile):
                raise RuntimeError(u'Client private key file \'%s\' does not exist!' % options._clientKeyFile)
            else:
                clientKeyFile = options._clientKeyFile

        # Check which TSL protocol version should be used
        try:
            tlsVersion = ssl.PROTOCOL_TLSv1_2
        except:
            tlsVersion = ssl.PROTOCOL_TLSv1
        if options._tlsVersion:
            if options._tlsVersion.lower() in ('tlsv1', 'tlsv1.0'):
                tlsVersion = ssl.PROTOCOL_TLSv1

        self._clientLock.acquire()  # Protect _client attribute

        # Create MQTT client if necessary
        self._createMqttClient()

        if options.will:
            self._client.will_set(options.will['topic'],
                                  options.will['message'],
                                  options.will['qos'],
                                  options.will['retained'])
        if self._client:
            if options._caFile:
                port = 8883 # Port with ssl
                self._client.tls_set(options._caFile,  # CA certificate
                                     certfile=clientCertFile,   # Client certificate
                                     keyfile=clientKeyFile,     # Client private key
                                     tls_version=tlsVersion,    # ssl.PROTOCOL_TLSv1, ssl.PROTOCOL_TLSv1_2
                                     ciphers=None)              # None, 'ALL', 'TLSv1.2', 'TLSv1.0'
                self._client.tls_insecure_set(True)  # True: No verification of the server hostname in the server certificate
            else:
                self.log.error('No CA file provided. Connection attempt likely to fail!')

            # Check if username and password is provided
            if options._username:
                password = options._password
                if not options._password:
                    # paho client v1.3 and higher do no more accept '' as empty string. Need None
                    password = None
                self._client.username_pw_set(options._username, password=password)

            self._client.connect(self._host, port=port)
            self._client.loop_start()
        self._clientLock.release()
        time.sleep(1)  # Wait a bit for the callback onConnect to be called

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
                self._client.on_disconnect = None   # Want get a disconnect callback call
                self._client.disconnect()
            self._client.loop_stop()
            self._client = None

        self._isConnected = False

        self._clientLock.release()

    def isConnected(self):
        return self._client and self._isConnected

    def onConnect(self, client, userdata, flags, rc):
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

    def onDisconnect(self, client, userdata, rc):
        self.log.info('Disconnect: %d' % rc)

        # Caution:
        # Do not call self.disconnect() here. It will kill the thread calling this
        # method and any subsequent code will not be executed!
        #self.disconnect()

        # Notify container class if disconnect callback
        # was registered.
        if self._onDisconnectCallback:
            self._onDisconnectCallback(rc)
        else:
            self.log.warning('On disconnect callback not set')

    def onMessage(self, client, userdata, msg):
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
        #message_info.wait_for_publish()
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
            return (self.MQTT_ERR_NO_CONN, None)


class MqttReconnectClient(MqttAsyncClient):
    """Same as MqttAsyncClient, but adds reconnect feature.
    """

    log = logging.getLogger('cloudio.mqttreconnectclient')

    def __init__(self, host, clientId='', clean_session=True, options=None):
        MqttAsyncClient.__init__(self, host, clientId, clean_session, options)

        # options are not used by MqttAsyncClient store them in this class
        self._options = options
        self._onConnectedCallback = None
        self._onConnectionThreadFinishedCallback = None
        self._retryInterval = 10                # Connect retry interval in seconds
        self._autoReconnect = True
        self.thread = None
        self._connectTimeoutEvent = Event()
        self._connectionThreadLooping = True    # Set to false in case the connection thread should leave

        # Register callback method to be called when connection to cloud.iO gets established
        MqttAsyncClient.setOnConnectCallback(self, self._onConnect)

        # Register callback method to be called when connection to cloud.iO gets lost
        MqttAsyncClient.setOnDisconnectCallback(self, self._onDisconnect)

    def setOnConnectCallback(self, onConnect):
        assert False, u'Not allowed in this class!'

    def setOnDisconnectCallback(self, onDisconnect):
        assert False, u'Not allowed in this class!'

    def setOnConnectedCallback(self, onConnectedCallback):
        self._onConnectedCallback = onConnectedCallback

    def setOnConnectionThreadFinishedCallback(self, onConnectionThreadFinishedCallback):
        self._onConnectionThreadFinishedCallback = onConnectionThreadFinishedCallback

    def start(self):
        self._startConnectionThread()

    def stop(self):
        self.log.info('Stopping MqttReconnectClient thread')
        self._autoReconnect = False
        self.disconnect()

    def _startConnectionThread(self):
        if self.thread is current_thread():
            # Do not restart myself!
            self.log.warning('Mqtt client connection thread is me! Not restarting myself!')
            return
        if self.thread and self.thread.isAlive():
            self.log.warning('Mqtt client connection thread already/still running!')
            return

        self._stopConnectionThread()

        self.log.info('Starting MqttReconnectClient thread')
        self.thread = Thread(target=self._run, name='mqtt-reconnect-client-' + self._clientClientId)
        # Close thread as soon as main thread exits
        self.thread.setDaemon(True)

        self._connectionThreadLooping = True
        self.thread.start()

    def _stopConnectionThread(self):
        self.log.info('Stopping MqttReconnectClient thread')
        if self.thread:
            try:
                self._connectionThreadLooping = False
                self.thread.join()
                self.thread = None
            except RuntimeError:
                self.log.error('Could not wait for connection thread')
                traceback.print_exc()

    def _onConnect(self):
        self._connectTimeoutEvent.set() # Free the connection thread

    def _onDisconnect(self, rc):
        if self._autoReconnect:
            self._startConnectionThread()

    def _onConnected(self):
        if self._onConnectedCallback:
            self._onConnectedCallback()

    def _onConnectionThreadFinished(self):
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

        while not self.isConnected() and self._connectionThreadLooping:
            try:
                self._connectTimeoutEvent.clear() # Reset connect timeout event prior to connect
                self.log.info(u'Trying to connect to cloud.iO...')
                self.connect(self._options)
            except Exception as exception:
                traceback.print_exc()
                self.log.warning(u'Error during broker connect!')
                # Force disconnection of MQTT client
                self.disconnect(force_client_disconnect=False)
                # Do not exit here. Continue to try to connect

            # Check if thread should leave
            if not self._connectionThreadLooping:
                # Tell subscriber connection thread has finished
                self._onConnectionThreadFinished()
                return

            if not self.isConnected():
                # If we should not retry, give up
                if self._retryInterval > 0:
                    # Wait until it is time for the next connect
                    self._connectTimeoutEvent.wait(self._retryInterval)

                # If we should not retry, give up
                if self._retryInterval == 0:
                    break

        self.log.info(u'Thread: Job done - leaving')

        if self.isConnected():
            self.log.info(u'Connected to cloud.iO broker')

            # Tell subscriber we are connected
            self._onConnected()

        # Tell subscriber connection thread has finished
        self._onConnectionThreadFinished()


class MqttConnectOptions():
    def __init__(self):
        self._username = ''
        self._password = ''
        self._caFile = None                 # type: str
        self._clientCertFile = None         # type: str
        self._clientKeyFile = None          # type: str
        self._tlsVersion = None             # type: str
        self.will = None                    # type dict

    def setWill(self, topic, message, qos, retained):
        self.will = {}
        self.will['topic'] = topic
        self.will['message'] = message
        self.will['qos'] = qos
        self.will['retained'] = retained

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

    def containsKey(self, key):
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
        :type bytearray
        """
        pass

    def keys(self):
        """Returns an Enumeration over the keys in this persistent data store.

        :return: generator
        """
        pass

    def open(self, clientId, serverUri):
        """Initialise the persistent store.

        Initialise the persistent store. If a persistent store exists for this client ID then open it,
        otherwise create a new one. If the persistent store is already open then just return. An application
        may use the same client ID to connect to many different servers, so the client ID in conjunction
        with the connection will uniquely identify the persistence store required.

        :param clientId The client for which the persistent store should be opened.
        :type clientId str
        :param serverUri The connection string as specified when the MQTT client instance was created.
        :type serverUri str
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
        self._persistance = {}

    def open(self, clientId, serverUri):
        pass

    def close(self):
        self.clear()

    def put(self, key, persistable):
        self._persistance[key] = persistable

    def get(self, key):
        if key in self._persistance:
            return self._persistance[key]
        return None

    def containsKey(self, key):
        return True if key in self._persistance else False

    def keys(self):
        keys = []
        for key in iterkeys(self._persistance):
            keys.append(key)
        return keys

    def remove(self, key):
        # Remove the key if it exist. If it does not exist
        # leave silently
        self._persistance.pop(key, None)

    def clear(self):
        self._persistance.clear()

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
        self._perClientIdAndServerUriDirectory = None           # type: str

        # Give a temporary unique storage name in case open() method does not get called
        self._perClientIdAndServerUriDirectory = str(uuid.uuid4())

        # Create base directory
        if not os.path.exists(self._directory):
            os.makedirs(self._directory)

    def open(self, clientId, serverUri):
        """Initialises the persistent store.

        :param clientId: MQTT client id
        :type clientId: str
        :param serverUri: Connection name to the server
        :type serverUri: str
        """
        self._perClientIdAndServerUriDirectory = clientId + '-' + serverUri

        # Remove some unwanted characters in sub-directory name
        self._perClientIdAndServerUriDirectory = self._perClientIdAndServerUriDirectory.replace('/', '')
        self._perClientIdAndServerUriDirectory = self._perClientIdAndServerUriDirectory.replace('\\', '')
        self._perClientIdAndServerUriDirectory = self._perClientIdAndServerUriDirectory.replace(':', '')
        self._perClientIdAndServerUriDirectory = self._perClientIdAndServerUriDirectory.replace(' ', '')

        # Create storage directory
        if not os.path.exists(self._storageDirectory()):
            os.makedirs(self._storageDirectory())

    def _storageDirectory(self): return os.path.join(self._directory, self._perClientIdAndServerUriDirectory)
    def _keyFileName(self, key): return os.path.join(self._storageDirectory(), key)

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

        with open(self._keyFileName(key), mode='wb') as file:
            file.write(persistable.get_header_bytes())

    def get(self, key):
        if os.path.exists(self._keyFileName(key)):
            with open(self._keyFileName(key), mode='rb') as file:
                return PendingUpdate(file.read())
        return None

    def containsKey(self, key):
        return True if os.path.exists(self._keyFileName(key)) else False

    def keys(self):
        keys = next(os.walk(self._storageDirectory()))[2]
        return keys

    def remove(self, key):
        # Remove the key if it exist. If it does not exist
        # leave silently
        keyFileName = self._keyFileName(key)
        try:
            if os.path.isfile(keyFileName):
                os.remove(keyFileName)
        except Exception as e:
            pass

    def clear(self):
        for key in os.listdir(self._storageDirectory()):
            keyFileName = self._keyFileName(key)
            if os.path.isfile(keyFileName):
                os.remove(keyFileName)