nosetests tests_chino.py --with-coverage --cover-html --cover-package=chino --stop
osascript -e 'display notification "Done, good or bad?" with title "Test over"'