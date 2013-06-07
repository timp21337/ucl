dropdb --user postgres ucll
createdb --user postgres ucll

./manage.py syncdb;
git push heroku master

heroku db:push --confirm ucll postgres://postgres:*@127.0.0.1:5432/ucll

