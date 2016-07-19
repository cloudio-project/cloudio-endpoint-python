# -*- coding: utf-8 -*-

import time
import paho.mqtt.client as mqtt

class MqttAsyncClient():
    """Mimic the behavior of the java.MqttAsyncClient class"""

    def __init__(self, host):
        self._isConnected = False
        self._host = host
        self.client = mqtt.Client()

        self.client.on_connect = self.onConnect

    def connect(self, username, password):
        self.client.username_pw_set(username, password=password)
        self.client.connect(self._host)
        self.client.loop_start()
        time.sleep(1)   # Wait a bit for the callback onConnect to be called

    def isConnected(self):
        return self._isConnected

    def onConnect(self, client, userdata, flags, rc):
        self._isConnected = True

        print 'Info: Connection to cloudio broker established.'

    def publish(self, topic, payload, qos, retain):
        self.client.publish(topic, payload, qos, retain)

class MqttConnectOptions():
    def __init__(self):
        self._username = ''
        self._password = ''