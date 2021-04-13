# Changelog

## 1.1.0 - (2021-04-13)
- Updated to `cloudio-common-python` v0.3.0

## 1.0.1 - (2021-03-31)
- Updated homepage link

## 1.0.0 - (2021-03-31)
- Added a thread to `CloudioEndpoint` class to decouple MQTT client calls 
- Removed Python2 support
- Reformatted code according to [PEP 8](https://www.python.org/dev/peps/pep-0008/)
- Extended `CloudioAttributeListener` interface

## 0.2.14 - (2020-07-08)
- Bugfix in attributeHasChangedByEndpoint() with PendingUpdate
- Python3 compatibility

## 0.2.13 - (2018-05-24)
- Small improvements and bug fixes

## 0.2.12 - (2018-02-06)
### Implemented enhancements:
- Changed behaviour when Endpoint is ready. Speeds up connection
### Fixed bugs:
- Bugfix in utils.ResourceLoader

## 0.2.11 - (2018-12-30)
### Fixed bugs:
- Improved reconnection procedure. Related to issue [#16](https://github.com/cloudio-project/cloudio-endpoint-python/issues/16)

## 0.2.10 - (2018-12-22)
### Fixed bugs:
- Better fix for issue [#16](https://github.com/cloudio-project/cloudio-endpoint-python/issues/16)

## 0.2.9 - (2018-12-20)
### Fixed bugs:
- Fixed issue [#16](https://github.com/cloudio-project/cloudio-endpoint-python/issues/16)
### Other changes:
- Allowing again to provide username (with/without password) even if 
  client certificate is provided

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
