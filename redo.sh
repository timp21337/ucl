dropdb --user postgres ucll
createdb --user postgres ucll

./manage.py syncdb
./manage.py load
./manage.py runserver
