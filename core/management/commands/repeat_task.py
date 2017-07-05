from django.core.management.base import BaseCommand

from core.datatools.repeat import Repeat


class Command(BaseCommand):

    def handle(self, *args, **options):
        try:
            scheduler = Repeat()
            scheduler.run()
        except KeyboardInterrupt:
            pass
