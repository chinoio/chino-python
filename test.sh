#!/bin/bash
cd test
nosetests . --with-coverage --cover-package=chino --logging-level=ERROR --stop
say "test over"
osascript -e 'display notification "Done, good or bad?" with title "Test over"'
