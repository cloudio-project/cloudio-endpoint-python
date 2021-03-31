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
$ pipenv run coverage run --source=./src -m unittest discover -s tests/cloudio
$ pipenv run coverage report -m
```

### Update Coverage Badge Image
To update the coverage image shown on the readme page execute the following command:
```bash
$ pipenv run coverage-badge -f -o docs/images/coverage.svg
```

## Generate and Upload Distribution Package
Prior to upload a new Python package be sure to create first a new release
of the project:
 - Increment version number
 - Update changelog file
 - Push to master branch

```bash
$ cd <into project>

# Install package needed for deployment (setuptools and twine) 
$ pipenv install

# Build source distribution (dist/{<project-name>-x.y.z}.tar.gz file)
$ pipenv run setup.py sdist

# Optional: Send to test server
$ pipenv run twine upload --repository testpypi dist/*

# Upload to official server
$ pipenv run twine upload --repository pypi dist/{<project-name>-x.y.z}.tar.gz
```

## Link to Local Package
If you want to use for example the `cloudio-glue-python` package from your locally cloned 
git repository, use a command similar like:
```bash
$ pipenv install --dev -e ../cloudio-glue-python
```
If it does not work with a relative path, try with an absolute path. The folder you are 
referencing must contain a `setup.cfg` or `setup.py` file.
