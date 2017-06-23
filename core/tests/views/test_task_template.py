import os

from django.test import TestCase, override_settings
from django.urls import reverse
from django.contrib.auth.models import User
from django.contrib.auth.models import Permission
from django.contrib.auth import settings

from core import models
from core.views import task_template
from core.tests import factories


class SearchTaskTemplateView(TestCase):

    def setUp(self):
        self.user = User.objects.create(
            username='Serega',
            password='passwd',
        )
        self.user.user_permissions.add(Permission.objects.get(codename='view_task_template'))

    def test_auth(self):
        response = self.client.get(reverse('task_template_search'))
        redirect_url = reverse('login') + '?next=' + reverse('task_template_search')

        self.assertRedirects(response, redirect_url)

    def test_permission(self):
        self.user.user_permissions.remove(Permission.objects.get(codename='view_task_template'))

        self.client.force_login(user=self.user)
        response = self.client.get(reverse('task_template_search'))

        self.assertRedirects(response, reverse('permission_denied'))

    def test_smoke(self):
        self.client.force_login(user=self.user)
        response = self.client.get(reverse('task_template_search'), {'sort': 'name'})

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'core/task_template/search.html')

    def test_get_queryset(self):
        factories.create_data_for_search_template()

        self.client.force_login(user=self.user)
        response = self.client.get(reverse('task_template_search'), {'name': 'Test', 'hosts': '1', 'host_groups': '1',
                                                                     'sort': 'name'})

        self.assertEqual(len(response.context['object_list']), 1)

    def test_paginate(self):
        factories.create_data_for_search_template()

        self.client.force_login(user=self.user)
        response = self.client.get(reverse('task_template_search'), {'sort': 'name', 'paginate_by': '1'})

        self.assertEqual(len(response.context['object_list']), 1)

    def test_paginate_all(self):
        factories.create_data_for_search_template()

        self.client.force_login(user=self.user)
        response = self.client.get(reverse('task_template_search'), {'sort': 'name', 'paginate_by': '-1'})

        self.assertEqual(len(response.context['object_list']), 2)

    def test_sort_queryset_ltask(self):
        self.user.user_permissions.add(Permission.objects.get(codename='run_task'))
        factories.create_data_for_search_template()

        self.client.force_login(user=self.user)
        self.client.get(reverse('task_template_run', args='1'))
        response = self.client.get(reverse('task_template_search'), {'sort': 'last_task'})

        self.assertEqual(response.context['object_list'][0], models.TaskTemplate.objects.get(id=2))

    def test_sort_queryset_reverse_ltask(self):
        self.user.user_permissions.add(Permission.objects.get(codename='run_task'))
        factories.create_data_for_search_template()

        self.client.force_login(user=self.user)
        self.client.get(reverse('task_template_run', args='1'))
        response = self.client.get(reverse('task_template_search'), {'sort': '-last_task'})

        self.assertEqual(response.context['object_list'][0], models.TaskTemplate.objects.get(id=1))

    def test_context(self):
        self.client.force_login(user=self.user)
        response = self.client.get(reverse('task_template_search'), {'sort': 'name'})

        self.assertEqual(response.context['breadcrumbs'][0], ('Home', reverse('index')))
        self.assertEqual(response.context['breadcrumbs'][1], (task_template.Search.title, ''))


class EditTaskTemplateView(TestCase):

    def setUp(self):
        self.user = User.objects.create(
            username='Serega',
            password='passwd',
        )
        self.user.user_permissions.add(Permission.objects.get(codename='add_tasktemplate'))

    def test_auth(self):
        response = self.client.get(reverse('task_template_create'))
        redirect_url = reverse('login') + '?next=' + reverse('task_template_create')

        self.assertRedirects(response, redirect_url)

    def test_permission(self):
        self.user.user_permissions.remove(Permission.objects.get(codename='add_tasktemplate'))

        self.client.force_login(user=self.user)
        response = self.client.get(reverse('task_template_create'))

        self.assertRedirects(response, reverse('permission_denied'))

    @override_settings(ANSIBLE_PLAYBOOKS_PATH='/tmp/playbooks')
    def test_create(self):
        self.user.user_permissions.add(Permission.objects.get(codename='view_task_template'))
        self.client.force_login(user=self.user)
        factories.AnsibleUserFactory.create()
        factories.HostFactory.create()
        factories.HostGroupFactory.create()

        path = settings.ANSIBLE_PLAYBOOKS_PATH
        os.mkdir(path)

        f = open(path + '/test.yml', 'w')
        f.write('- hosts: all\n'
                '  roles:\n'
                '   - preconf\n'
                '  tags: preconf')
        f.close()

        response = self.client.post(reverse('task_template_create'),
                                    {'name': 'Test name', 'ansible_user': '1', 'playbook': path + '/test.yml',
                                     'hosts': '1', 'host_groups': '1', 'description': 'Test description',
                                     'form-INITIAL_FORMS': '0', 'form-MAX_NUM_FORMS': '1000', 'form-MIN_NUM_FORMS': '0',
                                     'form-TOTAL_FORMS': '1', 'cron': '0 * * * *'})
        task_template_var = models.TaskTemplate.objects.get(id=1)

        self.assertEqual(str(task_template_var), 'Test name')
        self.assertEqual(str(task_template_var.ansible_user), 'Test name')
        self.assertEqual(str(task_template_var.playbook), path + '/test.yml')
        self.assertEqual(str(task_template_var.hosts.all()[0]), 'test name host (192.168.19.19)')
        self.assertEqual(str(task_template_var.host_groups.all()[0]), 'Test host group name')
        self.assertEqual(str(task_template_var.description), 'Test description')
        self.assertNotEqual(task_template_var.cron_dt, None)
        self.assertRedirects(response, reverse('task_template_update',
                                               kwargs={'pk': models.TaskTemplate.objects.last().id}))

        os.remove(path + '/test.yml')
        os.rmdir(path)

    def test_create_invalid_playbook(self):
        self.client.force_login(user=self.user)
        factories.AnsibleUserFactory.create()
        factories.HostFactory.create()
        factories.HostGroupFactory.create()

        response = self.client.post(reverse('task_template_create'),
                                    {'name': 'Test name', 'ansible_user': '1',
                                     'playbook': '',
                                     'hosts': '1', 'host_groups': '1', 'description': 'Test description',
                                     'form-INITIAL_FORMS': '0', 'form-MAX_NUM_FORMS': '1000', 'form-MIN_NUM_FORMS': '0',
                                     'form-TOTAL_FORMS': '1'})

        self.assertContains(response, 'This field is required.')

    @override_settings(ANSIBLE_PLAYBOOKS_PATH='/tmp/playbooks')
    def test_create_invalid_cron(self):
        self.user.user_permissions.add(Permission.objects.get(codename='view_task_template'))
        self.client.force_login(user=self.user)
        factories.AnsibleUserFactory.create()
        factories.HostFactory.create()
        factories.HostGroupFactory.create()

        path = settings.ANSIBLE_PLAYBOOKS_PATH
        os.mkdir(path)

        f = open(path + '/test.yml', 'w')
        f.write('- hosts: all\n'
                '  roles:\n'
                '   - preconf\n'
                '  tags: preconf')
        f.close()

        response = self.client.post(reverse('task_template_create'),
                                    {'name': 'Test name', 'ansible_user': '1', 'playbook': path + '/test.yml',
                                     'hosts': '1', 'host_groups': '1', 'description': 'Test description',
                                     'form-INITIAL_FORMS': '0', 'form-MAX_NUM_FORMS': '1000', 'form-MIN_NUM_FORMS': '0',
                                     'form-TOTAL_FORMS': '1', 'cron': 'asfsdsdf'})

        self.assertContains(response, 'Invalid value cron')

        os.remove(path + '/test.yml')
        os.rmdir(path)

    @override_settings(ANSIBLE_PLAYBOOKS_PATH='/tmp/playbooks')
    def test_edit(self):
        self.user.user_permissions.add(Permission.objects.get(codename='view_task_template'))
        self.client.force_login(user=self.user)
        factories.HostGroupFactory.create()
        factories.HostFactory.create()
        ansb_usr = factories.AnsibleUserFactory.create()
        factories.AnsibleUserFactory.create(name='two')
        factories.TaskTemplateFactory.create(ansible_user=ansb_usr)

        path = settings.ANSIBLE_PLAYBOOKS_PATH
        os.mkdir(path)

        f = open(path + '/test.yml', 'w')
        f.write('- hosts: all\n'
                '  roles:\n'
                '   - preconf\n'
                '  tags: preconf')
        f.close()

        response = self.client.post(reverse('task_template_update', args=['1']),
                                    {'name': 'Test', 'ansible_user': '2', 'playbook': path + '/test.yml',
                                     'hosts': '1', 'host_groups': '1', 'description': 'two', 'form-INITIAL_FORMS': '0',
                                     'form-MAX_NUM_FORMS': '1000', 'form-MIN_NUM_FORMS': '0', 'form-TOTAL_FORMS': '1'})
        changed_task_template = models.TaskTemplate.objects.get(id=1)

        self.assertEqual(str(changed_task_template), 'Test')
        self.assertEqual(str(changed_task_template.description), 'two')
        self.assertEqual(str(changed_task_template.playbook), path + '/test.yml')
        self.assertEqual(str(changed_task_template.hosts.get(id=1)), 'test name host (192.168.19.19)')
        self.assertEqual(str(changed_task_template.host_groups.get(id=1)), 'Test host group name')
        self.assertEqual(str(changed_task_template.ansible_user), 'two')
        self.assertRedirects(response, reverse('task_template_update', kwargs={'pk': 1}))

        os.remove(path + '/test.yml')
        os.rmdir(path)

    def test_edit_invalid(self):
        self.client.force_login(user=self.user)
        factories.HostGroupFactory.create()
        factories.HostFactory.create()
        ansb_usr = factories.AnsibleUserFactory.create()
        factories.AnsibleUserFactory.create(name='two')
        factories.TaskTemplateFactory.create(ansible_user=ansb_usr)

        response = self.client.post(reverse('task_template_update', args=['1']),
                                    {'name': 'Test', 'ansible_user': '2',
                                     'playbook': '',
                                     'hosts': '1', 'host_groups': '1', 'description': 'two', 'form-INITIAL_FORMS': '0',
                                     'form-MAX_NUM_FORMS': '1000', 'form-MIN_NUM_FORMS': '0', 'form-TOTAL_FORMS': '1'})

        self.assertContains(response, 'This field is required.')

    def test_context_create(self):
        task_template_var = factories.TaskTemplateFactory.create(ansible_user=factories.AnsibleUserFactory.create())
        for x in range(1, 12):
            factories.TaskFactory.create(template=task_template_var)
        self.client.force_login(user=self.user)

        response = self.client.get(reverse('task_template_create'))

        self.assertEqual(response.context['breadcrumbs'][0], ('Home', reverse('index')))
        self.assertEqual(response.context['breadcrumbs'][1], (task_template.Search.title,
                                                              reverse('task_template_search')))
        self.assertEqual(response.context['breadcrumbs'][2], (task_template.Edit.title_create, ''))

    def test_context_update(self):
        task_template_var = factories.TaskTemplateFactory.create(ansible_user=factories.AnsibleUserFactory.create())
        for x in range(1, 12):
            factories.TaskFactory.create(template=task_template_var)
        self.client.force_login(user=self.user)

        response = self.client.get(reverse('task_template_update', args=['1']))

        self.assertEqual(len(response.context['last_tasks']), 10)
        self.assertEqual(response.context['last_tasks'][0].id, 11)
        self.assertEqual(response.context['breadcrumbs'][2], ('Test name task template', ''))


class DeleteTaskTemplateView(TestCase):

    def setUp(self):
        self.user = User.objects.create(
            username='Serega',
            password='passwd',
        )
        self.user.user_permissions.add(Permission.objects.get(codename='delete_tasktemplate'))
        factories.HostGroupFactory.create()
        factories.HostFactory.create()
        ansb_usr = factories.AnsibleUserFactory.create()
        factories.AnsibleUserFactory.create(name='two')
        factories.TaskTemplateFactory.create(ansible_user=ansb_usr)

    def test_auth(self):
        response = self.client.get(reverse('task_template_delete', args=['1']))
        redirect_url = reverse('login') + '?next=' + reverse('task_template_delete', args=['1'])

        self.assertRedirects(response, redirect_url)

    def test_permission(self):
        self.user.user_permissions.remove(Permission.objects.get(codename='delete_tasktemplate'))
        self.client.force_login(user=self.user)
        response = self.client.get(reverse('task_template_delete', args=['1']))

        self.assertRedirects(response, reverse('permission_denied'))

    def test_smoke(self):
        self.client.force_login(user=self.user)
        response = self.client.get(reverse('task_template_delete', args=['1']))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'core/task_template/delete.html')

    def test_delete(self):
        self.user.user_permissions.add(Permission.objects.get(codename='view_task_template'))
        self.client.force_login(user=self.user)
        self.client.post(reverse('task_template_delete', args=['1']))

        self.assertEqual(len(models.TaskTemplate.objects.all()), 0)

    def test_context(self):
        self.client.force_login(user=self.user)
        response = self.client.get(reverse('task_template_delete', args=['1']))

        self.assertEqual(response.context['breadcrumbs'][0], ('Home', reverse('index')))
        self.assertEqual(response.context['breadcrumbs'][1], (task_template.Search.title,
                                                              reverse('task_template_search')))
        self.assertEqual(response.context['breadcrumbs'][2],
                         (str(response.context['object']), reverse('task_template_update',
                                                                   args=[str(response.context['object'].id)])))
        self.assertEqual(response.context['breadcrumbs'][3], ('Delete', ''))
        self.assertEqual(response.context['title'], 'Delete Test name task template')


class RunTaskTemplateView(TestCase):

    def setUp(self):
        self.user = User.objects.create(
            username='Serega',
            password='passwd',
        )
        self.user.user_permissions.add(Permission.objects.get(codename='run_task'))
        factories.HostGroupFactory.create()
        factories.HostFactory.create()
        ansb_usr = factories.AnsibleUserFactory.create()
        factories.TaskTemplateFactory.create(ansible_user=ansb_usr)

    def test_auth(self):
        response = self.client.get(reverse('task_template_run', args=['1']))
        redirect_url = reverse('login') + '?next=' + reverse('task_template_run', args=['1'])

        self.assertRedirects(response, redirect_url)

    def test_permission(self):
        self.user.user_permissions.remove(Permission.objects.get(codename='run_task'))
        self.client.force_login(user=self.user)
        response = self.client.get(reverse('task_template_run', args=['1']))

        self.assertRedirects(response, reverse('permission_denied'))

    def test_create_task(self):
        self.user.user_permissions.add(Permission.objects.get(codename='view_task_log'))
        self.client.force_login(user=self.user)
        response = self.client.get(reverse('task_template_run', args=['1']))

        self.assertRedirects(response, reverse('task_log', args=['1']))

    def test_in_progress_tasks(self):
        self.user.user_permissions.add(Permission.objects.get(codename='view_task_log'))
        self.client.force_login(user=self.user)
        self.client.get(reverse('task_template_run', args=['1']))
        response = self.client.get(reverse('task_template_run', args=['1']))
        response = self.client.get(response.url)

        self.assertContains(response, 'The same task was not started. You have been redirected to a running task.')


class InventoryView(TestCase):

    def setUp(self):
        self.user = User.objects.create(
            username='Serega',
            password='passwd',
        )
        self.user.user_permissions.add(Permission.objects.get(codename='inventory_task'))
        var = factories.VariableFactory.create()
        factories.HostGroupFactory.create()
        host = factories.HostFactory.create(vars=(var,))
        ansb_usr = factories.AnsibleUserFactory.create()
        factories.AnsibleUserFactory.create(name='two')
        factories.TaskTemplateFactory.create(ansible_user=ansb_usr, hosts=(host,))

    def test_auth(self):
        response = self.client.get(reverse('task_template_inventory', args=['1']))
        redirect_url = reverse('login') + '?next=' + reverse('task_template_inventory', args=['1'])

        self.assertRedirects(response, redirect_url)

    def test_permission(self):
        self.user.user_permissions.remove(Permission.objects.get(codename='inventory_task'))
        self.client.force_login(user=self.user)
        response = self.client.get(reverse('task_template_inventory', args=['1']))

        self.assertRedirects(response, reverse('permission_denied'))

    def test_smoke(self):
        self.client.force_login(user=self.user)

        response = self.client.get(reverse('task_template_inventory', args='1'))

        self.assertEqual(response.status_code, 200)

    def test_get(self):
        self.user.user_permissions.add(Permission.objects.get(codename='run_task'))
        self.client.force_login(user=self.user)

        self.client.get(reverse('task_template_run', args='1'))
        response = self.client.get(reverse('task_template_inventory', args='1'))

        self.assertContains(response, '{}  {}={}'.format(models.Host.objects.get(id=1).address,
                                                         models.Variable.objects.get(id=1).name,
                                                         models.Variable.objects.get(id=1).value))
