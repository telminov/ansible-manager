import datetime
from time import sleep

from django.utils import timezone

from core import models
from core import consts


class FailRepeat:
    def run(self):
        while True:
            self.process_fails()
            sleep(60)

    def process_fails(self):
        template_tasks = models.TaskTemplate.objects.filter(repeat_settings__isnull=False).distinct()
        for template in template_tasks:
            last_task = template.tasks.all().last()
            repeat_queryset = template.repeat_settings.all()
            repeat_number = last_task.repeat_number

            if last_task.status != consts.FAIL:
                continue

            if not last_task.is_automatically_created:
                continue

            if repeat_number >= repeat_queryset.count():
                continue

            now = timezone.now()
            time_repeat = last_task.logs.last().dc + datetime.timedelta(minutes=repeat_queryset[repeat_number].pause)
            if now >= time_repeat:
                template.create_task(user=None, is_automatically_created=True, repeat_number=repeat_number + 1)
