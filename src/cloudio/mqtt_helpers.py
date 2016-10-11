# -*- coding: utf-8 -*-

import os, time
from threading import RLock
from abc import ABCMeta, abstractmethod
import paho.mqtt.client as mqtt     # pip install paho-mqtt
import ssl

class MqttAsyncClient():
    """Mimic the behavior of the java.MqttAsyncClient class"""

    # Errors from mqtt module - mirrored into this class
    MQTT_ERR_SUCCESS = mqtt.MQTT_ERR_SUCCESS

    def __init__(self, host, clientId='', clean_session=True):
        self._isConnected = False
        self._host = host
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
            self._client = mqtt.Client(client_id=self._clientClientId,
                                       clean_session=self._clientCleanSession)

            self._client.on_connect = self.onConnect
            self._client.on_disconnect = self.onDisconnect
            self._client.on_message = self.onMessage
        self._clientLock.release()

    def setOnDisconnectCallback(self, onDisconnectCallback):
        self._onDisconnectCallback = onDisconnectCallback

    def setOnMessageCallback(self, onMessageCallback):
        self._onMessageCallback = onMessageCallback

    def connect(self, options):

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

        self._clientLock.acquire()  # Protect _client attribute

        # Create MQTT client if necessary
        self._createMqttClient()

        if options.will:
            self._client.will_set(options.will['topic'],
                                  options.will['message'],
                                  options.will['qos'],
                                  options.will['retained'])
        if self._client:
            self._client.username_pw_set(options._username, password=options._password)
            self._client.tls_insecure_set(True)  # True: No verification of the server hostname in the server certificate
            self._client.tls_set(options._caFile,  # CA certificate
                                certfile=clientCertFile,  # Client certificate
                                keyfile=clientKeyFile,  # Client private key
                                tls_version=ssl.PROTOCOL_TLSv1,  # ssl.PROTOCOL_TLSv1, ssl.PROTOCOL_TLSv1_2
                                ciphers=None)      # None, 'ALL', 'TLSv1.2', 'TLSv1.0'

            try:
                self._client.connect(self._host, port=8883)
                self._client.loop_start()
                time.sleep(1)   # Wait a bit for the callback onConnect to be called
            except Exception as e:
                pass
        self._clientLock.release()

    def disconnect(self):
        """Disconnects MQTT client
        """
        self._clientLock.acquire()
        # Stop MQTT client if still running
        if self._client:
            self._client.loop_stop()
            self._client.disconnect()
            self._client = None
        self._clientLock.release()

    def isConnected(self):
        return self._isConnected

    def onConnect(self, client, userdata, flags, rc):
        if rc == 0:
            self._isConnected = True
            print u'Info: Connection to cloudio broker established.'
        else:
            if rc == 1:
                print u'Error: Connection refused - incorrect protocol version'
            elif rc == 2:
                print u'Error: Connection refused - invalid client identifier'
            elif rc == 3:
                print u'Error: Connection refused - server unavailable'
            elif rc == 4:
                print u'Error: Connection refused - bad username or password'
            elif rc == 5:
                print u'Error: Connection refused - not authorised'
            else:
                print u'Error: Connection refused - unknown reason'

    def onDisconnect(self, client, userdata, rc):
        print 'Disconnect: %d' % rc

        self._isConnected = False

        # Notify container class if disconnect callback
        # was registered.
        if self._onDisconnectCallback:
            self._onDisconnectCallback(rc)

        self.disconnect()

    def onMessage(self, client, userdata, msg):
        # Delegate to container class
        if self._onMessageCallback:
            self._onMessageCallback(client, userdata, msg)

    def publish(self, topic, payload, qos, retain):
        timeout = 2.0
        message_info = self._client.publish(topic, payload, qos, retain)

        # Cannot use message_info.wait_for_publish() because it is blocking and
        # has no timeout parameter
        #message_info.wait_for_publish()
        #
        # Poll is_published() method
        while timeout > 0:
            if message_info.is_published():
                break
            timeout -= 0.1
            time.sleep(0.1)

        return message_info.is_published()

    def subscribe(self, topic, qos=0):
        return self._client.subscribe(topic, qos)

class MqttConnectOptions():
    def __init__(self):
        self._username = ''
        self._password = ''
        self._caFile = None                 # type: str
        self._clientCertFile = None         # type: str
        self._clientKeyFile = None          # type: str
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
        if self._persistance.has_key(key):
            return self._persistance[key]

    def containsKey(self, key):
        return True if self._persistance.has_key(key) else False

    def keys(self):
        keys = []
        for key in self._persistance.iterkeys():
            keys.append(key)
        return keys

    def remove(self, key):
        # Remove the key if it exist. If it does not exist
        # leave silently
        self._persistance.pop(key, None)

    def clear(self):
        self._persistance.clear()