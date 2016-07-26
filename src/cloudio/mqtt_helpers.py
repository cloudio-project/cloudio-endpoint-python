# -*- coding: utf-8 -*-

import os, time
import paho.mqtt.client as mqtt
import ssl

class MqttAsyncClient():
    """Mimic the behavior of the java.MqttAsyncClient class"""

    def __init__(self, host, clientId='', clean_session=True):
        self._isConnected = False
        self._host = host
        self.client = mqtt.Client(client_id=clientId, clean_session=clean_session)

        self.client.on_connect = self.onConnect

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

    def publish(self, topic, payload, qos, retain):
        self.client.publish(topic, payload, qos, retain)

class MqttConnectOptions():
    def __init__(self):
        self._username = ''
        self._password = ''
        self._caFile = None                 # type: str
        self._clientCertFile = None         # type: str
        self._clientKeyFile = None          # type: str