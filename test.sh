#!/bin/bash
# source test.env
cd test
nosetests tests_chino.py --with-coverage --cover-html --stop --cover-package=chino 
say "test over"
osascript -e 'display notification "Done, good or bad?" with title "Test over"'
