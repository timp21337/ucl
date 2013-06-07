from django.db.models import signals

import ucl.models as models


def post_syncdb(signal, sender, app, created_models, **kwargs):
    # See http://solyaris.wordpress.com/2007/02/18/insert-initial-data-via-django-orm/
    # However https://docs.djangoproject.com/en/dev/ref/signals/
    # warns that this should not alter the db as this may clash with flush.
    # only run when our model has been created
    if (signal == signals.post_syncdb) and (app == models):
        models.initialise()


signals.post_syncdb.connect(post_syncdb)