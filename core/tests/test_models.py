from django.contrib.auth.models import User
from django.test import TestCase

from core import models


class ModelVariable(TestCase):

    def setUp(self):
        models.Variable.objects.create(
            name='qwer',
            value='asdf',
        )

    def test_str(self):
        variable = models.Variable.objects.get(name='qwer')

        self.assertEqual(str(variable), 'qwer: asdf')


class ModelHostGroup(TestCase):

    def setUp(self):
        models.HostGroup.objects.create(
            name='qwer',
        )

    def test_str(self):
        host_group = models.HostGroup.objects.get(name='qwer')

        self.assertEqual(str(host_group), 'qwer')


class ModelHost(TestCase):

    def setUp(self):
        models.Host.objects.create(
            name='qwer',
            address='192.168.12.20',
        )
        models.Host.objects.create(
            address='192.168.44.74'
        )

    def test_str(self):
        host_with_address = models.Host.objects.get(name='qwer')
        host_without_address = models.Host.objects.get(address='192.168.44.74')

        self.assertEqual(str(host_with_address), 'qwer (192.168.12.20)')
        self.assertEqual(str(host_without_address), '192.168.44.74')

    def test_get_vars(self):
        var = models.Variable.objects.create(
            name='test',
            value='value',
        )
        group = models.HostGroup.objects.create(
            name='test group'
        )
        group.vars.add(var)
        group.save()

        host = models.Host.objects.get(id=1)
        host.groups.add(group)
        host.save()

        self.assertEqual(list(host.get_vars()), [models.Variable.objects.get(id=1)])


class ModelAnsibleUser(TestCase):

    def setUp(self):
        models.AnsibleUser.objects.create(
            name='qwer'
        )

    def test_str(self):
        ansible_user = models.AnsibleUser.objects.get(name='qwer')

        self.assertEqual(str(ansible_user), 'qwer')


class ModelTaskTemplate(TestCase):

    def setUp(self):
        models.TaskTemplate.objects.create(
            name='qwer',
            playbook='/home/',
        )

    def test_str(self):
        task_template = models.TaskTemplate.objects.get(name='qwer')

        self.assertEqual(str(task_template), 'qwer')

    def test_create_task(self):
        task_template = models.TaskTemplate.objects.get(name='qwer')
        self.user = User.objects.create(
            username='Serega',
            password='passwd'
        )
        answer = task_template.create_task(self.user)

        self.assertEqual(models.Task.objects.all().count(), 1)
        self.assertEqual(models.Task.objects.get(template=task_template).playbook, '/home/')
        self.assertEqual(models.Task.objects.get(template=task_template).user, self.user)
        self.assertEqual(models.Task.objects.get(template=task_template).ansible_user, task_template.ansible_user)
        self.assertEqual(answer, models.Task.objects.get(template=task_template))
        self.assertEqual(models.TaskLog.objects.all().count(), 1)
        self.assertEqual(models.TaskLog.objects.get(message='Task created by user Serega').status, 'wait')

    def test_uncompleted_task_false(self):
        self.assertFalse(models.TaskTemplate.objects.get(id=1).have_uncompleted_task())

    def test_uncompleted_task_true(self):
        models.AnsibleUser.objects.create(
            name='Test'
        )
        models.Task.objects.create(
            playbook='/home/',
            template=models.TaskTemplate.objects.get(id=1),
            ansible_user=models.AnsibleUser.objects.get(id=1),
            status='wait'
        )

        self.assertTrue(models.TaskTemplate.objects.get(id=1).have_uncompleted_task())

    def test_get_hosts_without_group(self):
        host_without_group = models.Host.objects.create(
            name='test',
            address='192.168.19.19'
        )
        group = models.HostGroup.objects.create(
            name='group test'
        )
        host_with_group = models.Host.objects.create(
            name='test test',
            address='192.168.19.20',
        )
        host_with_group.groups.add(group)
        host_with_group.save()
        template = models.TaskTemplate.objects.get(id=1)
        template.hosts.add(host_with_group, host_without_group)
        template.host_groups.add(group)
        template.save()

        self.assertEqual(len(template.get_hosts_without_groups()), 1)


class ModelTask(TestCase):

    def setUp(self):
        ansible_user = models.AnsibleUser.objects.create(
            name='Serega'
        )
        self.user = User.objects.create(
            username='Serega',
            password='passwd'
        )
        task_template = models.TaskTemplate.objects.create(
            name='qwer',
            playbook='/home/',
        )
        models.Task.objects.create(
            playbook='/home/',
            template=task_template,
            user=self.user,
            ansible_user=ansible_user
        )
        models.Task.objects.create(
            playbook='/otherhome/image',
            user=self.user
        )

    def test_str(self):
        task_with_template_name = models.Task.objects.get(playbook='/home/')
        task_without_template_name = models.Task.objects.get(playbook='/otherhome/image')

        self.assertEqual(str(task_with_template_name), '#%s qwer' % task_with_template_name.id)
        self.assertEqual(str(task_without_template_name),
                         '#%s image' % task_without_template_name.id)

    def test_get_duration_date(self):
        models.TaskLog.objects.create(
            task=models.Task.objects.get(playbook='/home/'),
            status='fail',
        )

        self.assertEqual(models.Task.objects.get(playbook='/home/').get_duration(),
                         models.Task.objects.get(playbook='/home/').logs.last().dc -
                         models.Task.objects.get(playbook='/home/').dc)

    def test_get_duration_none(self):
        models.TaskLog.objects.create(
            task=models.Task.objects.get(playbook='/home/'),
            status='test',
        )

        self.assertEqual(models.Task.objects.get(playbook='/home/').get_duration(), None)

    def test_ansible_command(self):
        task = models.Task.objects.get(playbook='/home/')

        self.assertEqual(type(task.get_ansible_command()), str)


class ModelTaskLog(TestCase):

    def setUp(self):
        self.user = User.objects.create(
            username='Serega',
            password='passwd',
        )
        task = models.Task.objects.create(
            playbook='/home/image',
            user=self.user,
        )
        models.TaskLog.objects.create(
            task=task,
            status='fail',
        )

    def test_str(self):
        task_log = models.TaskLog.objects.get(id=1)

        self.assertEqual(str(task_log), '#%s image' % task_log.id)
