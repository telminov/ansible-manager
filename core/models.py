from django.db import models


class Variable(models.Model):
    name = models.CharField(max_length=255, verbose_name='Name')
    value = models.CharField(max_length=255, verbose_name='Value')

    def __str__(self):
        return '%s=%s' % (self.name, self.value)


class HostGroup(models.Model):
    name = models.CharField(max_length=255, verbose_name='Name')
    vars = models.ManyToManyField(Variable, verbose_name='Variables', related_name='host_groups')

    def __str__(self):
        return self.name


class Host(models.Model):
    name = models.CharField(max_length=255, verbose_name='Name', blank=True)
    address = models.IPAddressField(verbose_name='IP address')
    group = models.ManyToManyField(HostGroup, verbose_name='Groups', related_name='hosts')
    vars = models.ManyToManyField(Variable, verbose_name='Variables', related_name='hosts')

    def __str__(self):
        return '%s (%s)' % (self.name, self.address) if self.name else self.address
