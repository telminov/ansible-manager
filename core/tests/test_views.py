from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from django.contrib.auth.models import Permission

from core import models
from core.views.general import PermissionDenied
from core.views import ansible_user, host, host_group


class IndexView(TestCase):

    def setUp(self):
        self.user = User.objects.create(
            username='Serega',
            password='passwd',
        )

    def test_auth(self):
        response = self.client.get(reverse('index'))
        redirect_url = reverse('login') + '?next=/'

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, redirect_url)

    def test_smoke(self):
        self.client.force_login(user=self.user)
        response = self.client.get(reverse('index'))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'core/index.html')

    def test_context(self):
        models.Task.objects.create(
            playbook='/home/',
            status='in_progress',
            user=User.objects.get(username='Serega'),
        )
        self.client.force_login(user=self.user)
        response = self.client.get(reverse('index'))

        self.assertEqual(len(response.context['tasks']), 1)
        self.assertEqual(response.context['tasks'][0].status, 'in_progress')


class PermissionDeniedView(TestCase):

    def setUp(self):
        self.user = User.objects.create(
            username='Serega',
            password='passwd',
        )

    def test_auth(self):
        response = self.client.get(reverse('permission_denied'))
        redirect_url = reverse('login') + '?next=' + reverse('permission_denied')

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, redirect_url)

    def test_smoke(self):
        self.client.force_login(user=self.user)
        response = self.client.get(reverse('permission_denied'))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'core/user/permission_denied.html')

    def test_context(self):
        self.client.force_login(user=self.user)
        response = self.client.get(reverse('permission_denied'))

        self.assertEqual(response.context['breadcrumbs'][0], ('Home', reverse('index')))
        self.assertEqual(response.context['breadcrumbs'][1], (PermissionDenied.title, ''))


class SearchHostView(TestCase):

    def setUp(self):
        self.user = User.objects.create(
            username='Serega',
            password='passwd',
        )
        self.user.user_permissions.add(Permission.objects.get(codename='view_host'))

    def test_auth(self):
        response = self.client.get(reverse('host_search'))
        redirect_url = reverse('login') + '?next=' + reverse('host_search')

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, redirect_url)

    def test_permissions(self):
        self.user.user_permissions.remove(Permission.objects.get(codename='view_host'))

        self.client.force_login(user=self.user)
        response = self.client.get(reverse('host_search'))

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('permission_denied'))

    def test_smoke(self):
        self.client.force_login(user=self.user)
        response = self.client.get(reverse('host_search'))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'core/host/search.html')

    def test_search_get_queryset(self):
        host_group = models.HostGroup.objects.create(
            name='Test group'
        )
        host = models.Host.objects.create(
            name='test name',
            address='192.168.19.19',
        )
        host.groups.add(host_group)
        models.Host.objects.create(
            name='Other test name',
            address='192.168.32.44',
        )
        host = models.Host.objects.create(
            name='Other other test name',
            address='192.168.19.19',
        )
        host.groups.add(host_group)

        self.client.force_login(user=self.user)
        response = self.client.get(reverse('host_search'),
                                   {'name': 'Test', 'address': '192.168.19.19', 'group': 1})

        self.assertEqual(len(response.context['object_list']), 2)

    def test_breadcrumbs(self):
        self.client.force_login(user=self.user)
        response = self.client.get(reverse('host_search'))

        self.assertEqual(response.context['breadcrumbs'][0], ('Home', reverse('index')))
        self.assertEqual(response.context['breadcrumbs'][1], (host.Search.title, ''))


class EditHostView(TestCase):

    def setUp(self):
        self.user = User.objects.create(
            username='Serega',
            password='passwd',
        )
        self.user.user_permissions.add(Permission.objects.get(codename='add_host'))
        models.HostGroup.objects.create(
            name='Test name',
        )

    def test_auth(self):
        response = self.client.get(reverse('host_create'))
        redirect_url = reverse('login') + '?next=' + reverse('host_create')

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, redirect_url)

    def test_permissions(self):
        self.user.user_permissions.remove(Permission.objects.get(codename='add_host'))

        self.client.force_login(user=self.user)
        response = self.client.get(reverse('host_create'))

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('permission_denied'))

    def test_smoke(self):
        self.client.force_login(user=self.user)

        response = self.client.get(reverse('host_create'))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'core/host/edit.html')

    def test_create_host(self):
        self.client.force_login(user=self.user)

        self.client.post(reverse('host_create'),
                         {'address': '192.168.19.19', 'form-INITIAL_FORMS': '0', 'form-MAX_NUM_FORMS': '1000',
                          'form-MIN_NUM_FORMS': '0', 'form-TOTAL_FORMS': '1', 'groups': '1'})
        host = models.Host.objects.get(id=1)

        self.assertEqual(host.address, '192.168.19.19')
        self.assertEqual(host.groups.all()[0].name, 'Test name')

    def test_edit_host(self):
        host = models.Host.objects.create(
            name='Test',
            address='192.168.19.19'
        )
        host.groups.add(models.HostGroup.objects.get(name='Test name'))

        self.client.force_login(user=self.user)

        self.client.post(reverse('host_update', args=['1']),
                         {'address': '192.168.19.19', 'form-INITIAL_FORMS': '0',
                          'form-MAX_NUM_FORMS': '1000', 'form-MIN_NUM_FORMS': '0', 'form-TOTAL_FORMS': '1',
                          'groups': '1', 'name': 'Test Test'})
        host = models.Host.objects.get(id=1)

        self.assertEqual(host.name, 'Test Test')

    def test_context_create(self):
        self.client.force_login(user=self.user)

        response = self.client.get(reverse('host_create'))

        self.assertEqual(response.context['breadcrumbs'][0], ('Home', reverse('index')))
        self.assertEqual(response.context['breadcrumbs'][1], (host.Search.title, reverse('host_search')))
        self.assertEqual(response.context['breadcrumbs'][2], (host.Edit.title_create, ''))

    def test_context_update(self):
        models.Host.objects.create(
            name='Test',
            address='192.168.19.19'
        )
        self.client.force_login(user=self.user)

        response = self.client.get(reverse('host_update', args=['1']))

        self.assertEqual(response.context['breadcrumbs'][2], (str(models.Host.objects.get(pk=1)), ''))


class DeleteHostView(TestCase):

    def setUp(self):
        self.user = User.objects.create(
            username='Serega',
            password='passwd',
        )
        self.user.user_permissions.add(Permission.objects.get(codename='delete_host'))
        models.Host.objects.create(
            name='Test',
            address='192.168.19.19'
        )

    def test_auth(self):
        response = self.client.get(reverse('host_delete', args=['1']))
        redirect_url = reverse('login') + '?next=' + reverse('host_delete', args=['1'])

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, redirect_url)

    def test_permission(self):
        self.user.user_permissions.remove(Permission.objects.get(codename='delete_host'))

        self.client.force_login(user=self.user)
        response = self.client.get(reverse('host_delete', args=['1']))

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('permission_denied'))

    def test_smoke(self):
        self.client.force_login(user=self.user)
        response = self.client.get(reverse('host_delete', args=['1']))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'core/host/delete.html')

    def test_delete_host(self):
        self.client.force_login(user=self.user)

        self.client.post(reverse('host_delete', args=['1']))

        self.assertEqual(len(models.Host.objects.all()), 0)


class SearchHostGroupView(TestCase):

    def setUp(self):
        self.user = User.objects.create(
            username='Serega',
            password='passwd',
        )
        self.user.user_permissions.add(Permission.objects.get(codename='view_host_group'))

    def test_auth(self):
        response = self.client.get(reverse('host_group_search'))
        redirect_url = reverse('login') + '?next=' + reverse('host_group_search')

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, redirect_url)

    def test_permission(self):
        self.user.user_permissions.remove(Permission.objects.get(codename='view_host_group'))

        self.client.force_login(user=self.user)
        response = self.client.get(reverse('host_group_search'))

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('permission_denied'))

    def test_smoke(self):
        models.HostGroup.objects.create(
            name='Test',
        )
        models.HostGroup.objects.create(
            name='Ohter test'
        )
        models.HostGroup.objects.create(
            name='est'
        )
        self.client.force_login(user=self.user)

        response = self.client.get(reverse('host_group_search'), {'name': 'test'})

        self.assertEqual(len(response.context['object_list']), 2)

    def test_context(self):
        self.client.force_login(user=self.user)

        response = self.client.get(reverse('host_group_search'))

        self.assertEqual(response.context['breadcrumbs'][0], ('Home', reverse('index')))
        self.assertEqual(response.context['breadcrumbs'][1], (host_group.Search.title, ''))


class EditHostGroupView(TestCase):

    def setUp(self):
        self.user = User.objects.create(
            username='Serega',
            password='passwd',
        )
        self.user.user_permissions.add(Permission.objects.get(codename='add_hostgroup'))

    def test_auth(self):
        response = self.client.get(reverse('host_group_create'))
        redirect_url = reverse('login') + '?next=' + reverse('host_group_create')

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, redirect_url)

    def test_permission(self):
        self.user.user_permissions.remove(Permission.objects.get(codename='add_hostgroup'))

        self.client.force_login(user=self.user)
        response = self.client.get(reverse('host_group_create'))

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('permission_denied'))

    def test_smoke(self):
        self.client.force_login(user=self.user)
        response = self.client.get(reverse('host_group_create'))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'core/host_group/edit.html')

    def test_create(self):
        models.Host.objects.create(
            name='Test host',
            address='192.168.19.19'
        )
        self.client.force_login(user=self.user)
        self.client.post(reverse('host_group_create'),
                         {'name': 'Test name', 'hosts': '1', 'form-INITIAL_FORMS': '0',
                          'form-MAX_NUM_FORMS': '1000', 'form-MIN_NUM_FORMS': '0', 'form-TOTAL_FORMS': '1'})

        self.assertEqual(str(models.HostGroup.objects.get(id=1)), 'Test name')

    def test_edit(self):
        host_group = models.HostGroup.objects.create(
            name='Test hostgroup'
        )
        host = models.Host.objects.create(
            name='Test host',
            address='192.168.19.19'
        )
        host.groups.add(host_group)

        self.client.force_login(user=self.user)
        changed_name = 'blabla test'
        self.client.post(reverse('host_group_update', args=['1']),
                         {'name': changed_name, 'hosts': '1', 'form-INITIAL_FORMS': '0',
                          'form-MAX_NUM_FORMS': '1000', 'form-MIN_NUM_FORMS': '0', 'form-TOTAL_FORMS': '1'})

        self.assertEqual(str(models.HostGroup.objects.get(id=1)), changed_name)

    def test_context(self):
        self.client.force_login(user=self.user)

        response = self.client.get(reverse('host_group_create'))

        self.assertEqual(response.context['breadcrumbs'][0], ('Home', reverse('index')))
        self.assertEqual(response.context['breadcrumbs'][1],
                         (host_group.Search.title, reverse('host_group_search')))
        self.assertEqual(response.context['breadcrumbs'][2], (host_group.Edit.title_create, ''))

    def test_context_update(self):
        models.HostGroup.objects.create(
            name='Test group'
        )

        self.client.force_login(user=self.user)

        response = self.client.get(reverse('host_group_update', args=['1']))

        self.assertEqual(response.context['breadcrumbs'][2], (str(models.HostGroup.objects.get(id=1)), ''))


class DeleteHostGroupView(TestCase):

    def setUp(self):
        self.user = User.objects.create(
            username='Serega',
            password='passwd',
        )
        self.user.user_permissions.add(Permission.objects.get(codename='delete_hostgroup'))
        models.HostGroup.objects.create(
            name='Test hostgroup'
        )

    def test_auth(self):
        response = self.client.get(reverse('host_group_delete', args=['1']))
        redirect_url = reverse('login') + '?next=' + reverse('host_group_delete', args=['1'])

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, redirect_url)

    def test_permission(self):
        self.user.user_permissions.remove(Permission.objects.get(codename='delete_hostgroup'))

        self.client.force_login(user=self.user)
        response = self.client.get(reverse('host_group_delete', args=['1']))

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('permission_denied'))

    def test_smoke(self):
        self.client.force_login(user=self.user)
        response = self.client.get(reverse('host_group_delete', args=['1']))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'core/host_group/delete.html')

    def test_delete(self):
        self.client.force_login(user=self.user)
        self.client.post(reverse('host_group_delete', args=['1']))

        self.assertEqual(len(models.HostGroup.objects.all()), 0)

    def test_context(self):
        self.client.force_login(user=self.user)
        response = self.client.get(reverse('host_group_delete', args=['1']))

        self.assertEqual(response.context['breadcrumbs'][0], ('Home', reverse('index')))
        self.assertEqual(response.context['breadcrumbs'][1], ('Search host group', reverse('host_group_search')))
        self.assertEqual(response.context['breadcrumbs'][2],
                         (str(models.HostGroup.objects.get(id=1)), reverse('host_group_update', args=['1'])))
        self.assertEqual(response.context['breadcrumbs'][3], ('Delete', ''))
        self.assertEqual(response.context['title'], 'Delete Test hostgroup')


class SearchAnsibleUserView(TestCase):

    def setUp(self):
        self.user = User.objects.create(
            username='Serega',
            password='passwd',
        )
        self.user.user_permissions.add(Permission.objects.get(codename='view_ansible_user'))

    def test_auth(self):
        response = self.client.get(reverse('ansible_user_search'))
        redirect_url = reverse('login') + '?next=' + reverse('ansible_user_search')

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, redirect_url)

    def test_permission(self):
        self.user.user_permissions.remove(Permission.objects.get(codename='view_ansible_user'))

        self.client.force_login(user=self.user)
        response = self.client.get(reverse('ansible_user_search'))

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('permission_denied'))

    def test_smoke(self):
        self.client.force_login(user=self.user)
        response = self.client.get(reverse('ansible_user_search'))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'core/ansible_user/search.html')

    def test_get_queryset(self):
        models.AnsibleUser.objects.create(
            name='Test name',
        )
        models.AnsibleUser.objects.create(
            name='Other test name'
        )
        models.AnsibleUser.objects.create(
            name='qwerty'
        )

        self.client.force_login(user=self.user)

        response = self.client.get(reverse('ansible_user_search'), {'name': 'test'})

        self.assertEqual(len(response.context['object_list']), 2)

    def test_context(self):
        self.client.force_login(user=self.user)

        response = self.client.get(reverse('ansible_user_search'))

        self.assertEqual(response.context['breadcrumbs'][0], ('Home', reverse('index')))
        self.assertEqual(response.context['breadcrumbs'][1], (ansible_user.Search.title, ''))


class EditAnsibleUserView(TestCase):

    def setUp(self):
        self.user = User.objects.create(
            username='Serega',
            password='passwd',
        )
        self.user.user_permissions.add(Permission.objects.get(codename='add_ansibleuser'))

    def test_auth(self):
        response = self.client.get(reverse('ansible_user_create'))
        redirect_url = reverse('login') + '?next=' + reverse('ansible_user_create')

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, redirect_url)

    def test_permission(self):
        self.user.user_permissions.remove(Permission.objects.get(codename='add_ansibleuser'))

        self.client.force_login(user=self.user)
        response = self.client.get(reverse('ansible_user_create'))

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('permission_denied'))

    def test_smoke(self):
        self.client.force_login(user=self.user)
        response = self.client.get(reverse('ansible_user_create'))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'core/ansible_user/edit.html')

    def test_create(self):
        self.client.force_login(user=self.user)
        self.client.post(reverse('ansible_user_create'), {'name': 'Test name'})

        self.assertEqual(str(models.AnsibleUser.objects.get(id=1)), 'Test name')

    def test_edit(self):
        models.AnsibleUser.objects.create(
            name='Test name'
        )
        self.client.force_login(user=self.user)
        self.client.post(reverse('ansible_user_update', args=['1']), {'name': 'blabla test'})

        self.assertEqual(str(models.AnsibleUser.objects.get(id=1)), 'blabla test')

    def test_context(self):
        self.client.force_login(user=self.user)

        response = self.client.get(reverse('ansible_user_create'))

        self.assertEqual(response.context['breadcrumbs'][0], ('Home', reverse('index')))
        self.assertEqual(response.context['breadcrumbs'][1],
                         (ansible_user.Search.title, reverse('ansible_user_search')))
        self.assertEqual(response.context['breadcrumbs'][2], (ansible_user.Edit.title_create, ''))

    def test_context_update(self):
        models.AnsibleUser.objects.create(
            name='Test ansible user'
        )

        self.client.force_login(user=self.user)

        response = self.client.get(reverse('ansible_user_update', args=['1']))

        self.assertEqual(response.context['breadcrumbs'][2], (str(models.AnsibleUser.objects.get(id=1)), ''))


class DeleteAnsibleUserView(TestCase):

    def setUp(self):
        self.user = User.objects.create(
            username='Serega',
            password='passwd',
        )
        self.user.user_permissions.add(Permission.objects.get(codename='delete_ansibleuser'))
        models.AnsibleUser.objects.create(
            name='Test ansible user'
        )

    def test_auth(self):
        response = self.client.get(reverse('ansible_user_delete', args=['1']))
        redirect_url = reverse('login') + '?next=' + reverse('ansible_user_delete', args=['1'])

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, redirect_url)

    def test_permission(self):
        self.user.user_permissions.remove(Permission.objects.get(codename='delete_ansibleuser'))

        self.client.force_login(user=self.user)
        response = self.client.get(reverse('ansible_user_delete', args=['1']))

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('permission_denied'))

    def test_smoke(self):
        self.client.force_login(user=self.user)
        response = self.client.get(reverse('ansible_user_delete', args=['1']))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'core/ansible_user/delete.html')

    def test_delete(self):
        self.client.force_login(user=self.user)
        self.client.post(reverse('ansible_user_delete', args=['1']))

        self.assertEqual(len(models.AnsibleUser.objects.all()), 0)

    def test_context(self):
        self.client.force_login(user=self.user)
        response = self.client.get(reverse('ansible_user_delete', args=['1']))

        self.assertEqual(response.context['breadcrumbs'][0], ('Home', reverse('index')))
        self.assertEqual(response.context['breadcrumbs'][1],
                         (ansible_user.Search.title, reverse('ansible_user_search')))
        self.assertEqual(response.context['breadcrumbs'][2],
                         (str(models.AnsibleUser.objects.get(id=1)), reverse('ansible_user_update', args=['1'])))
        self.assertEqual(response.context['breadcrumbs'][3], ('Delete', ''))
        self.assertEqual(response.context['title'], 'Delete Test ansible user')


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

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, redirect_url)

    def test_permission(self):
        self.user.user_permissions.remove(Permission.objects.get(codename='view_task_template'))

        self.client.force_login(user=self.user)
        response = self.client.get(reverse('task_template_search'))

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('permission_denied'))

    def test_smoke(self):
        self.client.force_login(user=self.user)
        response = self.client.get(reverse('task_template_search'))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'core/task_template/search.html')
