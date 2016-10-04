# -*- coding: utf-8 -*-

import os, sys, time
import paho.mqtt.client as mqtt

from utils import path_helpers

class VacuumCleanerClient():
    """A cloud.iO client connecting to a vacuum cleaner represented in the cloud.
    """

    def __init__(self, configFile):
        self._isConnected = False

        config = self.parseConfigFile(configFile)

        print 'Starting MQTT client...'
        mqttc = mqtt.Client()

        mqttc.on_connect = self.onConnect
        mqttc.on_disconnect = self.onDisconnect
        mqttc.on_message = self.onMessage

        mqttc.username_pw_set(config['cloudio']['username'], config['cloudio']['password'])
        mqttc.connect(config['cloudio']['host'], port=int(config['cloudio']['port']), keepalive=60)
        mqttc.loop_start()

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

            assert config['cloudio'].has_key('host'), 'Missing \'host\' parameter in influxdb group!'
            assert config['cloudio'].has_key('port'), 'Missing \'port\' parameter in influxdb group!'
            assert config['cloudio'].has_key('username'), 'Missing \'username\' parameter in influxdb group!'
            assert config['cloudio'].has_key('password'), 'Missing \'password\' parameter in influxdb group!'
            assert config['cloudio'].has_key('topics'), 'Missing \'topic\' parameter in influxdb group!'
            assert config['cloudio'].has_key('qos'), 'Missing \'qos\' parameter in influxdb group!'
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

    def onMessage(mosq, obj, mqttMsg):
        pass

    def setIdentification(self, newIdentification):
        pass