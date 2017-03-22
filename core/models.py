import os

import datetime

from django.contrib.auth.models import User
from django.db import models

from core import consts
from core.datatools import ansible
from core.datatools import tasks


class TaskOperationsMixin:
    def get_actual_hosts(self) -> models.QuerySet:
        host_ids = list(self.hosts.values_list('id', flat=True))
        for group in self.host_groups.all():
            host_ids.extend(list(group.hosts.values_list('id', flat=True)))

        hosts = Host.objects.filter(id__in=set(host_ids))
        return hosts

    def get_playbook_name(self) -> str:
        return os.path.basename(self.playbook)

    def get_hosts_without_groups(self) -> models.QuerySet:
        return self.get_actual_hosts().exclude(groups__in=self.host_groups.all())


class Variable(models.Model):
    name = models.CharField(max_length=255)
    value = models.CharField(max_length=255)

    class Meta:
        permissions = (
            ('view_variable', 'View Variables'),
        )

    def __str__(self):
        return '%s: %s' % (self.name, self.value)


class HostGroup(models.Model):
    name = models.CharField(max_length=255)
    vars = models.ManyToManyField(Variable, related_name='host_groups')

    class Meta:
        permissions = (
            ('view_host_group', 'View Host Groups'),
        )

    def __str__(self):
        return self.name


class Host(models.Model):
    name = models.CharField(max_length=255, blank=True)
    address = models.GenericIPAddressField()
    groups = models.ManyToManyField(HostGroup, related_name='hosts')
    vars = models.ManyToManyField(Variable, related_name='hosts')

    class Meta:
        unique_together = ('name', 'address')
        permissions = (
            ('view_host', 'View Host'),
        )

    def __str__(self):
        return '%s (%s)' % (self.name, self.address) if self.name else self.address


class TaskTemplate(TaskOperationsMixin, models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    playbook = models.FilePathField()
    hosts = models.ManyToManyField(Host, related_name='task_templates')
    host_groups = models.ManyToManyField(HostGroup, related_name='task_templates')
    vars = models.ManyToManyField(Variable, related_name='task_templates')

    class Meta:
        permissions = (
            ('view_task_template', 'View Task Template'),
        )

    def __str__(self):
        return self.name

    def get_last_task(self):
        return self.tasks.last()

    def get_last_date(self) -> datetime.datetime:
        last_task = self.get_last_task()
        date = None
        if last_task:
            date = last_task.dc
        return date

    def get_last_status(self) -> str:
        last_task = self.get_last_task()
        status = None
        if last_task:
            status = last_task.status
        return status

    def run_task(self, user):
        in_progress = None
        running_tasks = self.tasks.filter(status=consts.IN_PROGRESS)

        if running_tasks.exists():
            task = running_tasks.last()
            in_progress = True
        else:
            task = Task.objects.create(
                template=self,
                playbook=self.playbook,
                user=user
            )
            task.vars.add(*self.vars.all())
            task.hosts.add(*self.hosts.all())
            task.host_groups.add(*self.host_groups.all())

        return task, in_progress


class Task(TaskOperationsMixin, models.Model):
    playbook = models.FilePathField()
    hosts = models.ManyToManyField(Host, related_name='tasks')
    host_groups = models.ManyToManyField(HostGroup, related_name='tasks')
    vars = models.ManyToManyField(Variable, related_name='tasks')
    template = models.ForeignKey(TaskTemplate, related_name='tasks', null=True)
    status = models.CharField(max_length=100, choices=consts.STATUS_CHOICES, default=consts.WAIT)
    pid = models.IntegerField(null=True)
    user = models.ForeignKey(User, related_name='tasks')

    dc = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('-dc', )
        permissions = (
            ('view_task', 'View Task'),
            ('stop_task', 'Stop Task'),
            ('run_task', 'Run Task'),
        )

    def __str__(self):
        return "%s %s" % (self.get_playbook_name(), self.status)

    def get_command(self, splited=False):
        return ansible.make_command(self, splited)

    def get_duration(self) -> datetime.timedelta:
        start_date = self.dc
        logs = self.logs.filter(status__in=consts.NOT_RUN_STATUSES)
        delta = None
        if logs.exists():
            finish_date = logs.last().dc
            raw_delta = finish_date - start_date
            days, minutes, seconds = raw_delta.days, raw_delta.seconds // 3600, raw_delta.seconds % 3600 / 60.0  # todo
            delta = datetime.timedelta(days=days, minutes=minutes, seconds=seconds)
        return delta

    def stop(self):
        tasks.TaskManager.stop_task(self)


class TaskLog(models.Model):
    task = models.ForeignKey(Task, related_name='logs')
    status = models.CharField(max_length=100, choices=consts.STATUS_CHOICES)
    output = models.TextField(blank=True)
    message = models.TextField(blank=True)
    dc = models.DateTimeField(auto_now_add=True)

    class Meta:
        permissions = (
            ('view_task_log', 'View Task Log'),
        )

    def __str__(self):
        return "%s %s" % (self.task.get_playbook_name(), self.dc)
