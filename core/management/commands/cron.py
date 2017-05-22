from django.core.management.base import BaseCommand

from core.datatools.cron import Scheduler


class Command(BaseCommand):

    def handle(self, *args, **options):
        try:
            scheduler = Scheduler()
            scheduler.run()
        except KeyboardInterrupt:
            pass
