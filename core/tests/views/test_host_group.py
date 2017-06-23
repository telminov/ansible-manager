from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from django.contrib.auth.models import Permission

from core import models
from core.views import host_group


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

        self.assertRedirects(response, redirect_url)

    def test_permission(self):
        self.user.user_permissions.remove(Permission.objects.get(codename='view_host_group'))

        self.client.force_login(user=self.user)
        response = self.client.get(reverse('host_group_search'))

        self.assertRedirects(response, reverse('permission_denied'))

    def test_smoke(self):
        self.client.force_login(user=self.user)

        response = self.client.get(reverse('host_group_search'))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'core/host_group/search.html')

    def test_get_qeueryset(self):
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

        self.assertRedirects(response, redirect_url)

    def test_permission(self):
        self.user.user_permissions.remove(Permission.objects.get(codename='add_hostgroup'))

        self.client.force_login(user=self.user)
        response = self.client.get(reverse('host_group_create'))

        self.assertRedirects(response, reverse('permission_denied'))

    def test_smoke(self):
        self.client.force_login(user=self.user)
        response = self.client.get(reverse('host_group_create'))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'core/host_group/edit.html')

    def test_create(self):
        self.user.user_permissions.add(Permission.objects.get(codename='view_host_group'))
        models.Host.objects.create(
            name='Test host',
            address='192.168.19.19'
        )
        self.client.force_login(user=self.user)
        response = self.client.post(reverse('host_group_create'),
                                    {'name': 'Test name', 'hosts': '1', 'form-INITIAL_FORMS': '0',
                                     'form-MAX_NUM_FORMS': '1000', 'form-MIN_NUM_FORMS': '0', 'form-TOTAL_FORMS': '1'})

        self.assertEqual(str(models.HostGroup.objects.get(id=1)), 'Test name')
        self.assertRedirects(response, reverse('host_group_search'))

    def test_create_invalid(self):
        models.Host.objects.create(
            name='Test host',
            address='192.168.19.19'
        )
        self.client.force_login(user=self.user)
        response = self.client.post(reverse('host_group_create'),
                                    {'name': '  ', 'hosts': '1', 'form-INITIAL_FORMS': '0',
                                     'form-MAX_NUM_FORMS': '1000', 'form-MIN_NUM_FORMS': '0', 'form-TOTAL_FORMS': '1'})

        self.assertContains(response, 'This field is required.')

    def test_edit(self):
        self.user.user_permissions.add(Permission.objects.get(codename='view_host_group'))
        host_group = models.HostGroup.objects.create(
            name='Test hostgroup'
        )
        host = models.Host.objects.create(
            name='Test host',
            address='192.168.19.19'
        )
        host.groups.add(host_group)

        self.client.force_login(user=self.user)
        response = self.client.post(reverse('host_group_update', args=['1']),
                                    {'name': 'blabla test', 'hosts': '1', 'form-INITIAL_FORMS': '0',
                                     'form-MAX_NUM_FORMS': '1000', 'form-MIN_NUM_FORMS': '0', 'form-TOTAL_FORMS': '1'})
        changed_host_group = models.HostGroup.objects.get(id=1)

        self.assertEqual(str(changed_host_group), 'blabla test')
        self.assertEqual(str(changed_host_group.hosts.get(id=1)), 'Test host (192.168.19.19)')
        self.assertRedirects(response, reverse('host_group_search'))

    def test_edit_invalid(self):
        host_group = models.HostGroup.objects.create(
            name='Test hostgroup'
        )
        host = models.Host.objects.create(
            name='Test host',
            address='192.168.19.19'
        )
        host.groups.add(host_group)

        self.client.force_login(user=self.user)
        response = self.client.post(reverse('host_group_update', args=['1']),
                                    {'name': ' ', 'hosts': '1', 'form-INITIAL_FORMS': '0',
                                     'form-MAX_NUM_FORMS': '1000', 'form-MIN_NUM_FORMS': '0', 'form-TOTAL_FORMS': '1'})

        self.assertContains(response, 'This field is required.')

    def test_context_create(self):
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

        self.assertRedirects(response, redirect_url)

    def test_permission(self):
        self.user.user_permissions.remove(Permission.objects.get(codename='delete_hostgroup'))

        self.client.force_login(user=self.user)
        response = self.client.get(reverse('host_group_delete', args=['1']))

        self.assertRedirects(response, reverse('permission_denied'))

    def test_smoke(self):
        self.client.force_login(user=self.user)
        response = self.client.get(reverse('host_group_delete', args=['1']))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'core/host_group/delete.html')

    def test_delete(self):
        self.user.user_permissions.add(Permission.objects.get(codename='view_host_group'))
        self.client.force_login(user=self.user)
        response = self.client.post(reverse('host_group_delete', args=['1']))

        self.assertEqual(len(models.HostGroup.objects.all()), 0)
        self.assertRedirects(response, reverse('host_group_search'))

    def test_context(self):
        self.client.force_login(user=self.user)
        response = self.client.get(reverse('host_group_delete', args=['1']))

        self.assertEqual(response.context['breadcrumbs'][0], ('Home', reverse('index')))
        self.assertEqual(response.context['breadcrumbs'][1], ('Search host group', reverse('host_group_search')))
        self.assertEqual(response.context['breadcrumbs'][2],
                         (str(models.HostGroup.objects.get(id=1)), reverse('host_group_update', args=['1'])))
        self.assertEqual(response.context['breadcrumbs'][3], ('Delete', ''))
        self.assertEqual(response.context['title'], 'Delete Test hostgroup')
