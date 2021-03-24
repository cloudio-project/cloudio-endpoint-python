# Examples

## Vacuum Cleaner EndPoint Example
Please have a look into the _tests_ folder. There you will find a 
[`VacuumCleanerConnector`](../tests/cloudio/connector/vacuumcleaner_connector.py) 
class which is creating an endpoint for the `VacuumCleaner` model. 

The `VacuumCleaner` endpoint needs a configuration file named `test-vacuum-cleaner.properties` in either
of the following folders:
 - `<home>/.config/cloud.io/`
 - `/etc/cloud.io/`

The `<home>` equals to your user directory: Ex. `C:/Users/<username>`, `/home/<username>`, etc.

An example configuration file can be found [here](../tests/config/test-vacuum-cleaner-example.properties).

The endpoint configuration file contains connection parameters used by the endpoint to connect to cloud.io:
```
ch.hevs.cloudio.endpoint.hostUri=127.0.0.1
ch.hevs.cloudio.endpoint.ssl.authorityCert="~/.config/cloud.io/ca.pem"
ch.hevs.cloudio.endpoint.ssl.clientCert="~/.config/cloud.io/vacuum-cleaner-cert.pem"
ch.hevs.cloudio.endpoint.ssl.clientKey="~/.config/cloud.io/vacuum-cleaner-key.pem"
username=
password=
```

As usually an endpoint connects to cloud.io using a certificate, the parameters 
`username` and `password` may be empty.

## Vaccum Cleaner Client Example
Please have a look into the _tests_ folder. There you will find a [`VacuumCleanerClient`](../tests/cloudio/client/vacuumcleaner_client.py)
class showing how to connect to cloud.iO and access the EndPoint data.