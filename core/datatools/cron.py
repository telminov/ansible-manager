import datetime
import pytz

from time import sleep
from croniter import croniter

from django.utils import timezone
from django.contrib.auth.models import User

from core.datatools.tasks import TaskManager
from core import models
from core import consts


class Scheduler:
    def run(self):
        while True:
            self.check_run_time()
            sleep(60)

    def check_run_time(self):
        now = timezone.now()
        templates_task = models.TaskTemplate.objects.exclude(cron='')
        for template_task in templates_task:
            # проверяем запускался ли уже этот шаблон
            if template_task.tasks.all():
                # проверяем завершился ли последний таск
                if template_task.tasks.order_by('-id')[0].status != (consts.WAIT or consts.IN_PROGRESS):
                    delta = template_task.tasks.order_by('-id')[0].get_duration()
                    time = croniter(template_task.cron,
                                    template_task.tasks.order_by('-id')[0].dc + delta).get_next(datetime.datetime)
                    # проверяем подошло ли время
                    if time <= now:
                        self.run_task(template_task)
            elif template_task.datetime_cron:
                time = croniter(template_task.cron, template_task.datetime_cron).get_next(datetime.datetime)
                if time <= now:
                    self.run_task(template_task)

    def run_task(self,template_task):
        task = template_task.create_task(User.objects.get(id=1))
        manager = TaskManager()
        manager.run_task_process(task)
