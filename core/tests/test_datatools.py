import mock
import os
import shutil

from django.contrib.auth.models import User
from django.test import TestCase

from core import models
from core.datatools import ansible


class Ansible(TestCase):

    def setUp(self):
        var = models.Variable.objects.create(
            name='Test name',
            value='Test var'
        )
        host_group = models.HostGroup.objects.create(
            name='Test host_group',
        )
        host_group.vars.add(var)
        host = models.Host.objects.create(
            name='Test host',
            address='192.168.59.44',
        )
        host.groups.add(host_group)
        host.vars.add(var)
        other_host = models.Host.objects.create(
            name='Test №2 host',
            address='192.168.128.20',
        )
        other_host.vars.add(var)
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
        task = models.Task.objects.create(
            playbook='/home/',
            template=task_template,
            user=self.user,
            ansible_user=ansible_user,
        )
        task.host_groups.add(host_group)
        task.hosts.add(host)
        task.hosts.add(other_host)
        task.vars.add(var)

    @mock.patch('core.datatools.ansible.create_inventory')
    def test_make_command(self, create_inventory_mock):
        create_inventory_mock.return_value = '/tmp/test/inventory'

        self.assertEqual(models.Task.objects.get(playbook='/home/').get_ansible_command(),
                         '/usr/bin/ansible-playbook -i /tmp/test/inventory -u Serega -v /home/')

    @mock.patch('core.datatools.ansible.tempfile.mkdtemp')
    def test_create_inventory(self, tempfile_mock):

        tempfile_mock.return_value = '/tmp/test'
        os.mkdir('/tmp/test')

        self.assertEqual(ansible.create_inventory(models.Task.objects.get(playbook='/home/')),
                         '/tmp/test/inventory')
        self.assertEqual(
            ' '.join(''.join(open('/tmp/test/inventory', 'r').read().split('\n')).split(' ')),
            '192.168.128.20 Test name=Test var [Test host_group]192.168.59.44[Test host_group:'
            'vars]Test name=Test var[all:vars]Test name=Test varTest name=Test var')

        shutil.rmtree('/tmp/test')

    def test_inventory_file_path(self):
        self.assertEqual(ansible.get_inventory_file_path('qwerty 12345 test test 55'), 'test')


class Tasks(TestCase):

    def setUp(self):
        models.Task.objects.create(
            playbook='/home/',
            status='in_progress',
        )

