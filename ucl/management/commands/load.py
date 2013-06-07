from datetime import date
from django.core.management.base import BaseCommand, CommandError
from members.models import create_adult
from members.models import create_child
from members.models import create_doctor
from members.models import create_backup
from members.models import Session
from members.models import Attendance


from django.db import connection


class Command(BaseCommand):
    args = '<none>'
    help = 'Load data for Iffley'

    def handle(self, *args, **options):

        print "Loading"

        connection.close()
