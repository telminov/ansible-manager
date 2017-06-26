import mock
import os
import shutil

from django.contrib.auth.models import User
from django.test import TestCase

from core import models
from core.datatools import ansible, tasks


class Ansible(TestCase):

    def setUp(self):
        var = models.Variable.objects.create(
            name='Test_name',
            value='Test_var'
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
        test_path_inventory = '/tmp/test/inventory'
        create_inventory_mock.return_value = test_path_inventory

        self.assertEqual(models.Task.objects.get(playbook='/home/').get_ansible_command(),
                         '/usr/bin/ansible-playbook -i ' + test_path_inventory +
                         ' -u Serega -e "Test_name=Test_var " -v /home/')

    @mock.patch('core.datatools.ansible.tempfile.mkdtemp')
    def test_create_inventory(self, tempfile_mock):
        test_path_tempfile = '/tmp/test'
        tempfile_mock.return_value = test_path_tempfile
        os.mkdir(test_path_tempfile)

        self.assertEqual(ansible.create_inventory(models.Task.objects.get(playbook='/home/')),
                         test_path_tempfile + '/inventory')
        f = open(test_path_tempfile + '/inventory', 'r')
        inventory_file_content = ' '.join(''.join(f.read().split('\n')).split(' '))

        must_be_inventory_file_content = '192.168.59.44  Test_name=Test_var 192.168.128.20  Test_name=Test_var '

        self.assertEqual(inventory_file_content, must_be_inventory_file_content)

        f.close()
        shutil.rmtree(test_path_tempfile)

    def test_inventory_file_path(self):
        self.assertEqual(ansible.get_inventory_file_path('qwerty 12345 test some 55'), 'test')


class Tasks(TestCase):

    def setUp(self):
        self.user = User.objects.create(
            username='Serega',
            password='passwd'
        )

    def test_check_progress_tasks_not_pid(self):
        models.Task.objects.create(
            playbook='/home/',
            status='in_progress',
            user=self.user,
            pid=99999999,
        )

        task_manager = tasks.TaskManager()
        task_manager.check_in_progress_tasks()

        self.assertEqual(len(models.TaskLog.objects.filter(message='Task with pid 99999999 is not running')), 1)
