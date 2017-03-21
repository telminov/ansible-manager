from django.core.management.base import BaseCommand

from core.datatools.tasks import TaskChecker


class Command(BaseCommand):
    help = "Check and management tasks command"

    def handle(self, *args, **kwargs):
        try:
            checker = TaskChecker()
            checker.run()
        except KeyboardInterrupt:
            pass
