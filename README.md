# cloudio-endpoint-python
![python-version](https://img.shields.io/badge/python-3.x-blue.svg?style=flat)
![version](https://img.shields.io/pypi/v/cloudio-endpoint-python.svg)
![](docs/images/coverage.svg)

Python endpoint (IoT device) library for [cloud.iO](https://cloudio.hevs.ch).

The endpoint has been tested with python version 3.x. Support for python version 2.7.x 
has been removed since v1.0.0. If you still run python v2.x, please use version v0.2.15 
of this library.

## Introduction

This software allows to represent an IoT device in cloud.iO (the cloud). 

To use this software library you need first to understand cloud.iO's network topology. If 
you don't know exactly the therms (or the difference between) `endpoint` and `client` you
should first read the introduction to cloud.iO. 

Next you need a server on which cloud.iO is running. It is necessary to connect your future IoT
device to it. Then you have to get a certificate issued to your IoT device. The connection
established between your IoT device and the cloud.iO server is secured. The certificate is
needed to authenticate your device through the secure connection.

If the cloud.iO server is already set up you need to contact the system administrator to 
receive an endpoint certificate. In case you have to set up yourself a cloud.iO server you 
should jump to 
[How to set up a cloud.iO Server](https://github.com/cloudio-project/cloudio-documentation/blob/master/ServerSetup.md).

## Download and Install
The library is available on python's package distribution system [PyPi](https://pypi.python.org/).

From the console you can download and install it using the following command:

```
   pip install cloudio-endpoint-python
```

## Development Starting Point

This endpoint library provides you with classes allowing you to store variables or 
attributes of objects in the cloud. Of course, the other way round is also possible. 
Means you can change this values in the cloud and they are automatically send to your
IoT device.
 
This library is not a framework - means there is not a part of the library which takes
control and executes you code. It is up to you to provide the main function for your
software and to instantiate the class objects needed.

The basic idea here is to allow the developer to integrate the cloudio-endpoint library
in an existing project and hence allow to extend it with "cloud functionality".

So a good starting point to discover the content of this library is the 
[CloudioEndpoint](https://github.com/cloudio-project/cloudio-documentation/blob/master/ServerSetup.md)
class. It represents "the door" to cloud.iO seen from within your software. The 
`CloudioEndpoint` class (or the instance created from it) establishes and maintains 
the connection to the cloud.iO server. It holds also the object (attribute) 
structure of the endpoint. This data structure needs to be set up by the endpoint 
developer accordingly. It is up to the developer to provide it hard coded or via a
file containing the data model.

## Endpoint Data Meta-Model
As described in the cloud.iO introduction the object meta-structure is given as 
follows: 
 - An EndPoint can have CloudioNodes
 - CloudioNodes can have CloudObjects
 - CloudObjects can have CloudioObjects and/or CloudioAttributes

The 
[CloudioAttribute](https://github.com/cloudio-project/cloudio-endpoint-python/blob/master/src/cloudio/cloudio_attribute.py)
objects represent the leafs in the data structure. 

A `CloudioAttribute` is responsible to synchronize a variable or an attribute to
the cloud. Hence it gets informed if the attribute changes in the cloud.

To set up your endpoint data model you should first think about how you would like to 
show up your IoT device in the cloud, keeping in mind the _EndPoint->Node->Object->Attribute_
meta-structure implied.

We encourage you to provide the data model using an [XML](https://en.wikipedia.org/wiki/XML) or 
[JSON](https://en.wikipedia.org/wiki/JSON) based file. The file needs
then to be parsed and the CloudioEndpoints object structure set up accordingly. Our course
of action is to provide a `Connector` class which is responsible to do this job. You can
find in the `tests` folder the 
[VacuumCleanerConnector](https://github.com/cloudio-project/cloudio-endpoint-python/blob/master/tests/cloudio/connector/vacuumcleaner_connector.py)
class as an example on how this job me be done.

## Links to Internal Documentation
- [Developer](./docs/development.md) Section

### TODO
- [] Explain the `Model2CloudConnector` class
- [] Explain the `@cloudio_attribute` decorator
