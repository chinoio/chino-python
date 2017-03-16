#!/bin/bash
source test.env
cd test
nosetests tests_chino.py --with-coverage --cover-html --cover-package=chino --stop
say "test over"
osascript -e 'display notification "Done, good or bad?" with title "Test over"'
#nosetests -s tests_chino_data.py
