from django.core.management.base import BaseCommand

from core.datatools.fail_repeat import FailRepeat


class Command(BaseCommand):

    def handle(self, *args, **options):
        try:
            scheduler = FailRepeat()
            scheduler.run()
        except KeyboardInterrupt:
            pass
