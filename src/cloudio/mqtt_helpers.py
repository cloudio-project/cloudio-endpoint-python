# -*- coding: utf-8 -*-

import os, time
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
        self.client = mqtt.Client(client_id=clientId, clean_session=clean_session)

        self.client.on_connect = self.onConnect
        self.client.on_disconnect = self.onDisconnect

    def setOnMessageCallback(self, onMessageCallback):
        self.client.on_message = onMessageCallback

    def connect(self, options):

        if options.will:
            self.client.will_set(options.will['topic'],
                                 options.will['message'],
                                 options.will['qos'],
                                 options.will['retained'])

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

        self.client.username_pw_set(options._username, password=options._password)
        self.client.tls_insecure_set(True)  # True: No verification of the server hostname in the server certificate
        self.client.tls_set(options._caFile,    # CA certificate
                            certfile=clientCertFile,  # Client certificate
                            keyfile=clientKeyFile,    # Client private key
                            tls_version=ssl.PROTOCOL_TLSv1,                     # ssl.PROTOCOL_TLSv1, ssl.PROTOCOL_TLSv1_2
                            ciphers=None)      # None, 'ALL', 'TLSv1.2', 'TLSv1.0'

        self.client.connect(self._host, port=8883)
        self.client.loop_start()
        time.sleep(1)   # Wait a bit for the callback onConnect to be called

    def disconnect(self):
        """Disconnects MQTT client
        """
        # Stop MQTT client if still running
        if self.client:
            self.client.loop_stop()
            self.client.disconnect()
            self.client = None

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

            if rc != 3: # Expect for 'server unavailable'
                # Close application
                exit(0)

    def onDisconnect(self, client, userdata, rc):
        print 'Disconnect: %d' % rc

    def publish(self, topic, payload, qos, retain):
        self.client.publish(topic, payload, qos, retain)

    def subscribe(self, topic, qos=0):
        return self.client.subscribe(topic, qos)

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