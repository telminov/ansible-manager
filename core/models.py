import os

import datetime
from django.db import models


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


class TaskTemplate(models.Model):
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

    def get_actual_hosts(self) -> models.QuerySet:
        host_ids = list(self.hosts.values_list('id', flat=True))
        for group in self.host_groups.all():
            host_ids.extend(list(group.hosts.values_list('id', flat=True)))

        hosts = Host.objects.filter(id__in=set(host_ids))
        return hosts

    def get_tasks(self) -> models.QuerySet:
        # TODO task 3
        return None

    def get_playbook_name(self) -> str:
        return os.path.basename(self.playbook)

    def get_duration(self) -> int:
        # TODO task 3
        return 30  # min

    def get_last_date(self) -> datetime.datetime:
        # TODO task 3
        return datetime.datetime.now()

    def get_last_status(self) -> str:
        # TODO task 3
        return 'wait'
