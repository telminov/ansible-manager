import datetime
from time import sleep

from django.utils import timezone

from core import models
from core import consts


class Repeat:
    def run(self):
        while True:
            self.run_repeat_task()
            sleep(60)

    def run_repeat_task(self):
        templates_task = models.TaskTemplate.objects.filter(repeat_task__isnull=False).distinct()
        for template in templates_task:
            last_task = template.tasks.all().last()

            if last_task.status != consts.FAIL:
                continue

            if not last_task.is_created_automatically:
                continue

            if last_task.repeat_number:
                repeat_number = last_task.repeat_number
            else:
                repeat_number = 0
            now = timezone.now()
            repeat_queryset = models.RepeatSetting.objects.filter(template=template)
            if repeat_number < repeat_queryset.count():
                time_repeat = last_task.dc + datetime.timedelta(minutes=repeat_queryset[repeat_number].pause)
                if now >= time_repeat:
                    template.create_task(user=None, is_created_automatically=True, repeat_number=repeat_number + 1)
