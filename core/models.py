import os

import datetime

from django.utils import timezone
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from django.db import models
from croniter import croniter, CroniterBadCronError, CroniterBadDateError, CroniterNotAlphaError

from core.forms.fields import CronFormField
from core import consts
from core.datatools import ansible
from core.datatools import tasks


def validate_cron(value):
    if value == '':
        return

    now = timezone.now()
    try:
        croniter(value, now)
    except (CroniterBadCronError, CroniterBadDateError, CroniterNotAlphaError):
        raise ValidationError('Invalid value cron')


class CronField(models.CharField):

    def __init__(self, *args, **kwargs):
        defaults = {
            'help_text': 'Minute Hour Day Month Weekday',
            'default': '',
            'max_length': 100,
        }
        defaults.update(kwargs)
        super(CronField, self).__init__(*args, **defaults)

    def formfield(self, **kwargs):

        defaults = {'form_class': CronFormField}
        defaults.update(kwargs)
        return super(CronField, self).formfield(**defaults)

    def validate(self, value, model_instance):
        super(CronField, self).validate(value, model_instance)
        if self.editable:  # Skip validation for non-editable fields.
            validate_cron(value)


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
        ordering = ('name', )

    def __str__(self):
        return self.name


class Host(models.Model):
    name = models.CharField(max_length=255, blank=True)
    address = models.CharField(max_length=255)
    groups = models.ManyToManyField(HostGroup, related_name='hosts')
    vars = models.ManyToManyField(Variable, related_name='hosts')

    class Meta:
        unique_together = ('name', 'address')
        permissions = (
            ('view_host', 'View Host'),
        )
        ordering = ('name', )

    def __str__(self):
        return '%s (%s)' % (self.name, self.address) if self.name else self.address

    def get_vars(self):
        host_vars = {}

        for group in self.groups.all():
            for group_var in group.vars.all():
                host_vars[group_var.name] = group_var

        for var in self.vars.all():
            host_vars[var.name] = var

        return host_vars.values()


class AnsibleUser(models.Model):
    name = models.CharField(max_length=255)

    class Meta:
        permissions = (
            ('view_ansible_user', 'View Ansible User'),
        )
        ordering = ('name', )

    def __str__(self):
        return self.name


class TaskTemplate(TaskOperationsMixin, models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    playbook = models.FilePathField()
    hosts = models.ManyToManyField(Host, related_name='task_templates')
    host_groups = models.ManyToManyField(HostGroup, related_name='task_templates')
    vars = models.ManyToManyField(Variable, related_name='task_templates')
    verbose = models.CharField(max_length=4, choices=consts.VERBOSE_CHOICES, default='', blank=True)
    ansible_user = models.ForeignKey(AnsibleUser, related_name='task_templates', null=True)
    cron = CronField(blank=True)
    cron_dt = models.DateTimeField(default=None, blank=True, null=True)
    repeat_iter = models.IntegerField(default=-1)

    class Meta:
        permissions = (
            ('view_task_template', 'View Task Template'),
        )

    def __str__(self):
        return self.name

    def create_task(self, user, is_cron_created=False):
        task = Task.objects.create(
            template=self,
            playbook=self.playbook,
            user=user,
            is_cron_created=is_cron_created,
            ansible_user=self.ansible_user,
        )
        task.vars.add(*self.vars.all())
        task.hosts.add(*self.hosts.all())
        task.host_groups.add(*self.host_groups.all())
        task = Task.objects.get(id=task.id)
        task.logs.create(
            status=consts.WAIT,
            message='Task created by user %s' % user
        )
        return task

    def have_uncompleted_task(self):
        if self.tasks.exists():
            return self.tasks.last().status in [consts.WAIT, consts.IN_PROGRESS]
        return False


class RepeatTask(models.Model):
    pause = models.IntegerField()
    template = models.ForeignKey(TaskTemplate, related_name='repeat_task', null=True)


class Task(TaskOperationsMixin, models.Model):
    playbook = models.FilePathField()
    hosts = models.ManyToManyField(Host, related_name='tasks')
    host_groups = models.ManyToManyField(HostGroup, related_name='tasks')
    vars = models.ManyToManyField(Variable, related_name='tasks')
    template = models.ForeignKey(TaskTemplate, related_name='tasks', null=True)
    status = models.CharField(max_length=100, choices=consts.STATUS_CHOICES, default=consts.WAIT)
    pid = models.IntegerField(null=True)
    user = models.ForeignKey(User, related_name='tasks', blank=True, null=True)
    is_cron_created = models.BooleanField(default=False)
    verbose = models.CharField(max_length=4, choices=consts.VERBOSE_CHOICES, default='v')
    ansible_user = models.ForeignKey(AnsibleUser, related_name='tasks', null=True)

    dc = models.DateTimeField(auto_now_add=True)

    class Meta:
        get_latest_by = ('id',)
        permissions = (
            ('view_task', 'View Task'),
            ('stop_task', 'Stop Task'),
            ('run_task', 'Run Task'),
            ('replay_task', 'Replay Task'),
            ('inventory_task', 'View Task Inventory'),
        )

    def __str__(self):
        name = self.get_playbook_name()
        if self.template:
            name = self.template.name
        return "#%s %s" % (self.id, name)

    def get_ansible_command(self):
        return ansible.make_command(self)

    def get_duration(self) -> datetime.timedelta:
        start_date = self.dc
        logs = self.logs.filter(status__in=consts.NOT_RUN_STATUSES)
        delta = None
        if logs.exists():
            finish_date = self.logs.last().dc
            delta = finish_date - start_date
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
        return "#%s %s" % (self.id, self.task.get_playbook_name())
