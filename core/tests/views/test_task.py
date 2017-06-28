import os
import mock

from django.contrib.auth import settings
from django.test import TestCase, override_settings
from django.urls import reverse
from django.contrib.auth.models import User
from django.contrib.auth.models import Permission

from core import models
from core.views import task
from core.tests import factories
from core.tests.mixins import TestDefaultMixin


class SearchTaskView(TestDefaultMixin, TestCase):

    def setUp(self):
        self.user = User.objects.create(
            username='Serega',
            password='passwd',
        )
        self.pem = 'view_task'
        self.url = reverse('task_search')
        self.user.user_permissions.add(Permission.objects.get(codename='view_task'))

    def test_smoke(self):
        self.client.force_login(user=self.user)
        response = self.client.get(reverse('task_search'), {'sort': 'dc'})

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'core/task/search.html')

    @override_settings(ANSIBLE_PLAYBOOKS_PATH='/tmp/playbooks')
    def test_get_queryset(self):
        factories.create_data_for_search_task()

        path = settings.ANSIBLE_PLAYBOOKS_PATH
        os.mkdir(path)

        f = open(path + '/test.yml', 'w')
        f.write('- hosts: all\n'
                '  roles:\n'
                '   - preconf\n'
                '  tags: preconf')
        f.close()

        self.client.force_login(user=self.user)
        response = self.client.get(reverse('task_search'),
                                   {'template': '2', 'playbook': path + '/test.yml',
                                    'status': 'fail', 'sort': 'dc'})

        self.assertEqual(len(response.context['object_list']), 1)

        os.remove(path + '/test.yml')
        os.rmdir(path)

    def test_paginate(self):
        factories.create_data_for_search_task()

        self.client.force_login(user=self.user)
        response = self.client.get(reverse('task_search'), {'paginate_by': '1', 'sort': 'dc'})

        self.assertEqual(len(response.context['object_list']), 1)

    def test_paginate_all(self):
        factories.create_data_for_search_task()

        self.client.force_login(user=self.user)
        response = self.client.get(reverse('task_search'), {'paginate_by': '-1', 'sort': 'dc'})

        self.assertEqual(len(response.context['object_list']), 2)

    def test_context(self):
        self.client.force_login(user=self.user)
        response = self.client.get(reverse('task_search'), {'sort': 'dc'})

        self.assertEqual(response.context['breadcrumbs'][0], ('Home', reverse('index')))
        self.assertEqual(response.context['breadcrumbs'][1], (task.Search.title, ''))


class CreateTaskView(TestDefaultMixin, TestCase):

    def setUp(self):
        self.user = User.objects.create(
            username='Serega',
            password='passwd',
        )
        self.pem = 'add_task'
        self.url = reverse('task_create')
        self.user.user_permissions.add(Permission.objects.get(codename='add_task'))
        factories.AnsibleUserFactory.create()
        group_with_test = factories.HostGroupFactory.create()
        host_with_test = factories.HostFactory.create(groups=(group_with_test,))
        tsk_tmlt_wth_tst = factories.TaskTemplateFactory.create(hosts=(host_with_test,), host_groups=(group_with_test,))
        factories.TaskFactory.create(hosts=(host_with_test,), host_groups=(group_with_test,),
                                     template=tsk_tmlt_wth_tst, playbook='/home/pc/ansible/playbooks/test.yml')

    @override_settings(ANSIBLE_PLAYBOOKS_PATH='/tmp/playbooks')
    def test_create(self):
        self.user.user_permissions.add(Permission.objects.get(codename='view_task'))

        path = settings.ANSIBLE_PLAYBOOKS_PATH
        os.mkdir(path)

        f = open(path + '/test.yml', 'w')
        f.write('- hosts: all\n'
                '  roles:\n'
                '   - preconf\n'
                '  tags: preconf')
        f.close()

        self.client.force_login(user=self.user)
        self.client.post(reverse('task_create'),
                         {'template': '1', 'playbook': path + '/test.yml', 'verbose': 'v',
                          'ansible_user': '1', 'form-INITIAL_FORMS': '0', 'form-MAX_NUM_FORMS': '1000',
                          'form-MIN_NUM_FORMS': '0', 'form-TOTAL_FORMS': '1'})
        task = models.Task.objects.get(id=2)

        self.assertEqual(task.playbook, '/tmp/playbooks/test.yml')
        self.assertEqual(str(task.template), 'Test name task template')
        self.assertEqual(task.verbose, 'v')
        self.assertEqual(str(task.ansible_user), 'Test name')

        os.remove(path + '/test.yml')
        os.rmdir(path)

    def test_create_invalid(self):
        self.client.force_login(user=self.user)
        response = self.client.post(reverse('task_create'),
                                    {'template': '1', 'playbook': '/home/pc/ansible/playbooks/main.yml', 'verbose': '',
                                     'ansible_user': '1', 'form-INITIAL_FORMS': '0', 'form-MAX_NUM_FORMS': '1000',
                                     'form-MIN_NUM_FORMS': '0', 'form-TOTAL_FORMS': '1'})

        self.assertContains(response, 'This field is required.')

    def test_context(self):
        self.client.force_login(user=self.user)
        response = self.client.get(reverse('task_create'))

        self.assertEqual(response.context['breadcrumbs'][0], ('Home', reverse('index')))
        self.assertEqual(response.context['breadcrumbs'][1], (task.Search.title, reverse('task_search')))
        self.assertEqual(response.context['breadcrumbs'][2], (task.Create.title_create, ''))


class StopTaskView(TestDefaultMixin, TestCase):

    def setUp(self):
        self.user = User.objects.create(
            username='Serega',
            password='passwd',
        )
        self.pem = 'stop_task'
        self.url = reverse('task_stop', args='1')
        self.user.user_permissions.add(Permission.objects.get(codename='stop_task'))
        factories.AnsibleUserFactory.create()
        group_with_test = factories.HostGroupFactory.create()
        host_with_test = factories.HostFactory.create(groups=(group_with_test,))
        tsk_tmlt_wth_tst = factories.TaskTemplateFactory.create(hosts=(host_with_test,), host_groups=(group_with_test,))
        factories.TaskFactory.create(
            hosts=(host_with_test,),
            host_groups=(group_with_test,),
            template=tsk_tmlt_wth_tst,
            playbook='/home/pc/ansible/playbooks/main.yml',
            status='in_progress'
        )

    @mock.patch('os.kill')
    def test_stop(self, mock_kill):
        mock_kill.return_value = True
        self.client.force_login(user=self.user)
        self.client.post(reverse('task_stop', args=['1']))
        task_status = models.Task.objects.get(id=1).status

        self.assertEqual(task_status, 'stopped')

    def test_stop_fail(self):
        self.user.user_permissions.add(Permission.objects.get(codename='view_task'))
        task = models.Task.objects.get(id=1)
        task.status = 'stopped'
        task.save()
        self.client.force_login(user=self.user)
        response = self.client.post(reverse('task_stop', args=['1']))
        response = self.client.get(response.url, {'sort': 'dc'})

        self.assertContains(response, 'Task is not run')


class ReplayTaskView(TestCase):

    def setUp(self):
        self.user = User.objects.create(
            username='Serega',
            password='passwd',
        )
        self.user.user_permissions.add(Permission.objects.get(codename='replay_task'))
        factories.AnsibleUserFactory.create()
        group_with_test = factories.HostGroupFactory.create()
        host_with_test = factories.HostFactory.create(groups=(group_with_test,))
        tsk_tmlt_wth_tst = factories.TaskTemplateFactory.create(hosts=(host_with_test,), host_groups=(group_with_test,))
        factories.TaskFactory.create(
            hosts=(host_with_test,),
            host_groups=(group_with_test,),
            template=tsk_tmlt_wth_tst,
            playbook='/home/pc/ansible/playbooks/main.yml',
            status='completed'
        )

    def test_auth(self):
        response = self.client.get(reverse('task_replay', args=['1']))
        redirect_url = reverse('login') + '?next=' + reverse('task_replay', args=['1'])

        self.assertRedirects(response, redirect_url)

    def test_permission(self):
        self.user.user_permissions.remove(Permission.objects.get(codename='replay_task'))
        self.client.force_login(user=self.user)
        response = self.client.get(reverse('task_replay', args=['1']))

        self.assertRedirects(response, reverse('permission_denied'))

    def test_get_not_run_status(self):
        self.user.user_permissions.add(Permission.objects.get(codename='view_task_log'))
        self.client.force_login(user=self.user)
        response = self.client.get(reverse('task_replay', args=['1']))

        self.assertRedirects(response, reverse('task_log', args=['2']))

    def test_get_run_status(self):
        task = models.Task.objects.get(id=1)
        task.status = 'wait'
        task.save()
        self.user.user_permissions.add(Permission.objects.get(codename='view_task_log'))
        self.client.force_login(user=self.user)
        response = self.client.get(reverse('task_replay', args=['1']))
        response = self.client.get(response.url)

        self.assertContains(response, 'Not start duplicate task')


class LogTaskView(TestDefaultMixin, TestCase):

    def setUp(self):
        self.user = User.objects.create(
            username='Serega',
            password='passwd',
        )
        self.pem = 'view_task_log'
        self.url = reverse('task_log', args=['1'])
        self.user.user_permissions.add(Permission.objects.get(codename='view_task_log'))
        factories.AnsibleUserFactory.create()
        group_with_test = factories.HostGroupFactory.create()
        host_with_test = factories.HostFactory.create(groups=(group_with_test,))
        tsk_tmlt_wth_tst = factories.TaskTemplateFactory.create(hosts=(host_with_test,), host_groups=(group_with_test,))
        factories.TaskFactory.create(
            hosts=(host_with_test,),
            host_groups=(group_with_test,),
            template=tsk_tmlt_wth_tst,
            playbook='/home/pc/ansible/playbooks/main.yml',
            status='in_progress'
        )

    def test_title(self):
        self.client.force_login(user=self.user)

        session = self.client.session
        session['detected_tz'] = 'Europe/Moscow'
        session.save()

        response = self.client.get(reverse('task_log', args='1'))

        self.assertIn('Log "Test name task template" task for', response.context['title'])

    def test_context(self):
        self.client.force_login(user=self.user)
        response = self.client.get(reverse('task_log', args='1'))

        self.assertEqual(response.context['breadcrumbs'][0], ('Home', reverse('index')))
        self.assertEqual(response.context['breadcrumbs'][1], (task.Search.title, reverse('task_search')))
        self.assertEqual(response.context['breadcrumbs'][2],
                         ('Log %s task for %s' % (models.Task.objects.get(id=1).template,
                                                  models.Task.objects.get(id=1).dc.strftime("%d-%m-%Y %H:%M:%S")), ''))


class InventoryView(TestDefaultMixin, TestCase):

    def setUp(self):
        self.user = User.objects.create(
            username='Serega',
            password='passwd',
        )
        self.pem = 'inventory_task'
        self.url = reverse('task_inventory', args=['1'])
        self.user.user_permissions.add(Permission.objects.get(codename='inventory_task'))
        factories.AnsibleUserFactory.create()
        var = factories.VariableFactory.create()
        group_with_test = factories.HostGroupFactory.create()
        host_with_test = factories.HostFactory.create(groups=(group_with_test,), vars=(var,))
        tsk_tmlt_wth_tst = factories.TaskTemplateFactory.create(hosts=(host_with_test,), host_groups=(group_with_test,))
        factories.TaskFactory.create(
            hosts=(host_with_test,),
            host_groups=(group_with_test,),
            template=tsk_tmlt_wth_tst,
            playbook='/home/pc/ansible/playbooks/main.yml',
            status='completed'
        )

    def test_get(self):
        self.client.force_login(user=self.user)

        response = self.client.get(reverse('task_inventory', args='1'))

        self.assertContains(response,
                            '{}  {}={}'.format(str(models.Host.objects.get(id=1).address),
                                               str(models.Variable.objects.get(id=1).name),
                                               str(models.Variable.objects.get(id=1).value)))
