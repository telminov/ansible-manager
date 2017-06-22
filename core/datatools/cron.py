import datetime

from time import sleep
from croniter import croniter

from django.utils import timezone

from core.datatools.tasks import TaskManager
from core import models


class Scheduler:
    def run(self):
        while True:
            self.check_run_time()
            sleep(60)

    def check_run_time(self):
        now = timezone.now().astimezone(timezone.get_current_timezone())
        templates_task = models.TaskTemplate.objects.exclude(cron='')
        for template_task in templates_task:
            if template_task.have_uncompleted_task():
                continue

            if template_task.tasks.exists():
                last_time = template_task.tasks.last().logs.last().dc.astimezone(timezone.get_current_timezone())
            else:
                last_time = template_task.cron_dt.astimezone(timezone.get_current_timezone())
            next_time = croniter(template_task.cron, last_time).get_next(datetime.datetime).astimezone(timezone.get_current_timezone())
            if next_time <= now:
                self.run_task(template_task)

    def run_task(self, template_task):
        task = template_task.create_task(user=None, is_cron_created=True)
        manager = TaskManager()
        manager.run_task_process(task)
