
# [v0.2.0](https://github.com/cloudio-project/cloudio-endpoint-python/releases/tag/0.2.0) (2016-12-09)

### Features
* Added _**persistence in file**_ feature. Messages not able to be transmitted to the cloud can now be 
  stored locally on the endpoint. In contrast to the _persistance in memory_ feature, the 
  _persistence in file_ feature allows to persist data even after a power cycle.
  
  The feature can be enabled by setting the _ch.hevs.cloudio.endpoint.persistence_ parameter to _file_
  in the cloud.iO configuration file.
  
### Bug Fixes
* Attribute changes initiated from the cloud are no more thrown back to the cloud 

# [v0.1.2](https://github.com/cloudio-project/cloudio-endpoint-python/releases/tag/0.1.2) (2016-10-14)

### Features
* Added persistence in memory feature. Messages get queued in endpoint if cloud.iO is not present

### Bug Fixes
* Now no messages get lost if cloud.iO is down

# [v0.1.1](https://github.com/cloudio-project/cloudio-endpoint-python/releases/tag/0.1.1) (2016-10-07)

### Features
* Added @set action. Now commands can be send over cloud.iO to change properties of other devices