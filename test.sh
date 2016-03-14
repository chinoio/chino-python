#!/bin/bash
cd test
nosetests . --with-coverage --cover-package=chino --logging-level=ERROR --stop