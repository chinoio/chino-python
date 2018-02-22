cd test
nosetests tests_chino.py --with-coverage --cover-html --cover-package=chino --stop
cd ..
cscript PopupNotification.vbs
