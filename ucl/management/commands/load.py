from django.core.management.base import BaseCommand, CommandError


from django.db import connection


class Command(BaseCommand):
    args = '<none>'
    help = 'Load data for Iffley'

    def handle(self, *args, **options):

        print "Loading"

        connection.close()
