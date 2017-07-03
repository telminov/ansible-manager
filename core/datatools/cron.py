import datetime

from time import sleep
from croniter import croniter

from django.utils import timezone

from core import models
from core import consts

NOT_REPEAT = -1


class Scheduler:
    def run(self):
        while True:
            self.check_run_time()
            self.repeat_task()
            sleep(60)

    def check_run_time(self):
        now = timezone.now().astimezone(timezone.get_current_timezone())
        templates_task = models.TaskTemplate.objects.exclude(cron='')
        for template_task in templates_task:
            if template_task.have_uncompleted_task():
                continue

            last_time = template_task.cron_dt.astimezone(timezone.get_current_timezone())
            next_time = croniter(template_task.cron, last_time).get_next(datetime.datetime).astimezone(timezone.get_current_timezone())
            if next_time <= now:
                self.run_task(template_task)
                template_task.cron_dt = timezone.now()
                template_task.save()

    def run_task(self, template_task):
        template_task.create_task(user=None, is_cron_created=True)

    def repeat_task(self):
        templates_task = models.TaskTemplate.objects.filter(repeat_task__isnull=False).distinct()
        for template in templates_task:
            if template.repeat_iter == NOT_REPEAT:
                continue

            last_task = template.tasks.all().last()
            if last_task.status != consts.FAIL:
                continue

            now = timezone.now()
            repeat_queryset = models.RepeatTask.objects.filter(template=template)
            if template.repeat_iter < repeat_queryset.count():
                time_repeat = last_task.dc + datetime.timedelta(minutes=repeat_queryset[template.repeat_iter].pause)
                if now >= time_repeat:
                    self.run_task(template)
