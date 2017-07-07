from django.core.management.base import BaseCommand

from core.datatools.fail_repeat import FailRepeater


class Command(BaseCommand):

    def handle(self, *args, **options):
        try:
            repeater = FailRepeater()
            repeater.run()
        except KeyboardInterrupt:
            pass
