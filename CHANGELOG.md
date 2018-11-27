# Changelog

## 0.2.8 - (2018-11-27)
### Fixed bugs:
- PersistenceDataStore now working in Python 3

## 0.2.7 - (2018-10-29)
### Implemented enhancements:
- Moved version string into _endpoint_ package
### Fixed bugs:
- In case client certificate is provided, username and password are no more needed
- @set actions now also working in Python 3

## 0.2.6 - (2018-10-02)
### Implemented enhancements:
- Logging now version info at startup

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
- Improved Python 3 compatibility
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