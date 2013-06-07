import os
import subprocess

from django.contrib.auth.models import User


PROJECT_ROOT = os.path.join(os.path.dirname(__file__), '../')


def initialise():
    admin = User.objects.create_superuser('admin', 'adam@example.org', 'admin')
    admin.first_name = "Adam"
    admin.last_name = "Admin"
    admin.save()
