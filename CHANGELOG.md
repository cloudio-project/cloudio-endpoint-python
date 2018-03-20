# Changelog

## 0.2.5 - (2018-03-20)
### Fixed bugs:
- Updated MqttAsyncClient's `disconnect()` method. Added `force_client_disconnect` parameter

## 0.2.4 - (2018-03-12)
### Fixed bugs:
- Forcing to close MQTT client connection in case there is a problem during connection time    

## 0.2.3 - (2018-02-26)
### Fixed bugs:
- Now continuing to connect to cloud.iO even on error 

## 0.2.2 - (2018-02-25)
### Fixed bugs:
- Fixed problems with str und byte representations 
 
## 0.2.1 - (2018-02-19)
### Implemented enhancements:
- Improved python 3 compatibility
### Fixed bugs:
- Fixed bug in client's `publish()` method when connection was not 
  already established

## 0.2.0 - (2018-02-12)
### Implemented enhancements:
- Added InvalidCloudioAttributeTypeException class
- Optimized publish message algorithm
### Fixed bugs:
- Type of CloudioAttribute value is now consistent over lifetime 

## 0.1.1 - (2018-02-02)
### Fixed bugs:
- Correctly implemented **@online** message