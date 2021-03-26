# Development

[Home](../README.md)

This section contains information for developers. In case you want to improve, debug, 
extend the project you may find here some useful information.

## Running Tests
To run a particular test execute a command similar like this:
```bash
$ pipenv run python -m unittest tests/cloudio/test_cloudio_attribute.py
```

To execute all tests:
```bash
$ pipenv run python -m unittest discover -s tests/cloudio
```

## Running Test Coverage
To run the test coverage execute the following commands:
```bash
$ pipenv run coverage --source=./src run -m unittest discover -s tests/cloudio
$ pipenv run coverage report -m
```

## Link to Local Package
If you want to use for example the `cloudio-glue-python` package from your locally cloned 
git repository use a command similar like:
```bash
$ pipenv install --dev -e ../cloudio-glue-python
```
If it does not work with a relative path, try with an absolute path. The folder you are 
referencing must contain a `setup.py` file.
