# -*- coding: utf-8 -*-

import os, sys, time
import logging
import json
import paho.mqtt.client as mqtt

from utils import path_helpers
from utils import datetime_helpers

logging.getLogger(__name__).setLevel(logging.INFO)

class VacuumCleanerClient():
    """A cloud.iO client connecting to a vacuum cleaner represented in the cloud.
    """

    log = logging.getLogger(__name__)

    def __init__(self, configFile):
        self._isConnected = False

        config = self.parseConfigFile(configFile)

        self._qos = int(config['cloudio']['qos'])

        self._endPointName = config['endpoint']['name']
        self._nodeName = config['node']['name']

        self.log.info('Starting MQTT client...')
        self._client = mqtt.Client()

        self._client.on_connect = self.onConnect
        self._client.on_disconnect = self.onDisconnect
        self._client.on_message = self.onMessage

        self._client.username_pw_set(config['cloudio']['username'], config['cloudio']['password'])
        self._client.connect(config['cloudio']['host'], port=int(config['cloudio']['port']), keepalive=60)
        self._client.loop_start()

    def close(self):
        self._client.loop_stop(force=True)

    def parseConfigFile(self, configFile):
        global config

        from configobj import ConfigObj

        config = None

        pathConfigFile = path_helpers.prettify(configFile)

        if pathConfigFile and os.path.isfile(pathConfigFile):
            config = ConfigObj(pathConfigFile)

        if config:
            # Check if most important configuration parameters are present
            assert config.has_key('cloudio'), 'Missing group \'cloudio\' in config file!'
            assert config.has_key('endpoint'), 'Missing group \'endpoint\' in config file!'
            assert config.has_key('node'), 'Missing group \'node\' in config file!'

            assert config['cloudio'].has_key('host'), 'Missing \'host\' parameter in cloudio group!'
            assert config['cloudio'].has_key('port'), 'Missing \'port\' parameter in cloudio group!'
            assert config['cloudio'].has_key('username'), 'Missing \'username\' parameter in cloudio group!'
            assert config['cloudio'].has_key('password'), 'Missing \'password\' parameter in cloudio group!'
            assert config['cloudio'].has_key('subscribe_topics'), 'Missing \'subscribe_topics\' parameter in cloudio group!'
            assert config['cloudio'].has_key('qos'), 'Missing \'qos\' parameter in cloudio group!'

            assert config['endpoint'].has_key('name'), 'Missing \'name\' parameter in endpoint group!'

            assert config['node'].has_key('name'), 'Missing \'name\' parameter in node group!'
        else:
            sys.exit(u'Error reading config file')

        return config

    def waitUntilConnected(self):
        while not self.isConnected():
            time.sleep(0.2)

    def isConnected(self):
        return self._isConnected

    def onConnect(self, client, userdata, flags, rc):
        if rc == 0:
            self._isConnected = True
            self.log.info(u'Connection to cloudio broker established.')
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

            if rc != 3: # Expect for 'server unavailable'
                # Close application
                exit(0)

    def onDisconnect(self, client, userdata, rc):
        self.log.info('Disconnect: ' + rc)

    def onMessage(mosq, obj, mqttMsg):
        pass

    def setIdentification(self, newIdentification):
        topic = '@set/' + self._endPointName + '/nodes/' + self._nodeName + '/objects/Parameters/attributes/setIdentification'

        payload = {}
        payload['timestamp'] = datetime_helpers.getCurrentTimestamp()
        payload['value'] = newIdentification
        self._client.publish(topic, json.dumps(payload), qos=self._qos)

    def setPowerOn(self, powerState=True):
        topic = '@set/' + self._endPointName + '/nodes/' + self._nodeName + '/objects/Parameters/attributes/setPowerOn'

        payload = {}
        payload['timestamp'] = datetime_helpers.getCurrentTimestamp()
        payload['value'] = powerState
        self._client.publish(topic, json.dumps(payload), qos=self._qos)

    def setThroughput(self, newThroughputValue):
        topic = '@set/' + self._endPointName + '/nodes/' + self._nodeName + '/objects/Parameters/attributes/setThroughput'

        payload = {}
        payload['timestamp'] = datetime_helpers.getCurrentTimestamp()
        payload['value'] = newThroughputValue
        self._client.publish(topic, json.dumps(payload), qos=self._qos)

    def setOperatingMode(self, newOperatingMode):
        topic = '@set/' + self._endPointName + '/nodes/' + self._nodeName + '/objects/Parameters/attributes/setOperatingMode'

        payload = {}
        payload['timestamp'] = datetime_helpers.getCurrentTimestamp()
        payload['value'] = newOperatingMode
        self._client.publish(topic, json.dumps(payload), qos=self._qos)