from django.core.management.base import BaseCommand

from core.datatools.tasks import TaskManager


class Command(BaseCommand):
    help = "Check and management tasks command"

    def handle(self, *args, **kwargs):
        try:
            manager = TaskManager()
            manager.run()
        except KeyboardInterrupt:
            pass
