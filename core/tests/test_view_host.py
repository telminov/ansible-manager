import urllib.parse

from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from django.contrib.auth.models import Permission

from core import models
from core.views import host


def create_data_for_search():
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

        self.assertRedirects(response, redirect_url)

    # Здесь проверяем миксин
    def test_permissions(self):
        self.user.user_permissions.remove(Permission.objects.get(codename='view_host'))

        self.client.force_login(user=self.user)
        http_referer = 'http://127.0.0.1/hosts'
        response = self.client.get(reverse('host_search'), HTTP_REFERER=http_referer)
        url = reverse('permission_denied') + '?next=%s' % urllib.parse.quote(http_referer)

        self.assertRedirects(response, url)

    def test_smoke(self):
        self.client.force_login(user=self.user)
        response = self.client.get(reverse('host_search'))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'core/host/search.html')

    def test_get_queryset(self):
        create_data_for_search()

        self.client.force_login(user=self.user)
        response = self.client.get(reverse('host_search'),
                                   {'name': 'Test', 'address': '192.168.19.19', 'group': 1})

        self.assertEqual(len(response.context['object_list']), 2)

    def test_context(self):
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

        self.assertRedirects(response, redirect_url)

    def test_permissions(self):
        self.user.user_permissions.remove(Permission.objects.get(codename='add_host'))

        self.client.force_login(user=self.user)
        response = self.client.get(reverse('host_create'))

        self.assertRedirects(response, reverse('permission_denied'))

    def test_smoke(self):
        self.client.force_login(user=self.user)

        response = self.client.get(reverse('host_create'))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'core/host/edit.html')

    def test_create(self):
        self.user.user_permissions.add(Permission.objects.get(codename='view_host'))
        self.client.force_login(user=self.user)

        response = self.client.post(reverse('host_create'),
                                    {'address': '192.168.19.19', 'form-INITIAL_FORMS': '0', 'form-MAX_NUM_FORMS': '1000',
                                     'form-MIN_NUM_FORMS': '0', 'form-TOTAL_FORMS': '1', 'groups': '1',
                                     'name': 'Test name'})

        self.assertEqual(str(models.Host.objects.get(id=1)), 'Test name (192.168.19.19)')
        self.assertRedirects(response, reverse('host_search'))

    def test_create_invalid(self):
        self.client.force_login(user=self.user)

        response = self.client.post(reverse('host_create'),
                                    {'address': '  ', 'form-INITIAL_FORMS': '0', 'form-MAX_NUM_FORMS': '1000',
                                     'form-MIN_NUM_FORMS': '0', 'form-TOTAL_FORMS': '1', 'groups': '1',
                                     'name': 'Test name'})

        self.assertContains(response, 'This field is required.')

    def test_edit(self):
        self.user.user_permissions.add(Permission.objects.get(codename='view_host'))
        host = models.Host.objects.create(
            name='Test',
            address='192.168.19.19'
        )
        models.HostGroup.objects.create(
            name='Other test name'
        )
        host.groups.add(models.HostGroup.objects.get(name='Test name'))

        self.client.force_login(user=self.user)
        response = self.client.post(reverse('host_update', args=['1']),
                                    {'address': '192.168.19.18', 'form-INITIAL_FORMS': '0',
                                     'form-MAX_NUM_FORMS': '1000', 'form-MIN_NUM_FORMS': '0', 'form-TOTAL_FORMS': '1',
                                     'groups': '2', 'name': 'Test Test'})
        changed_host = models.Host.objects.get(id=1)

        self.assertEqual(str(changed_host), 'Test Test (192.168.19.18)')
        self.assertEqual(str(changed_host.groups.get(id=2)), 'Other test name')
        self.assertRedirects(response, reverse('host_search'))

    def test_edit_invalid(self):
        host = models.Host.objects.create(
            name='Test',
            address='192.168.19.19'
        )
        models.HostGroup.objects.create(
            name='Other test name'
        )
        host.groups.add(models.HostGroup.objects.get(name='Test name'))

        self.client.force_login(user=self.user)

        response = self.client.post(reverse('host_update', args=['1']),
                                    {'address': '  ', 'form-INITIAL_FORMS': '0',
                                     'form-MAX_NUM_FORMS': '1000', 'form-MIN_NUM_FORMS': '0', 'form-TOTAL_FORMS': '1',
                                     'groups': '2', 'name': 'Test Test'})

        self.assertContains(response, 'This field is required.')

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
        self.user.user_permissions.add(Permission.objects.get(codename='view_host'))
        models.Host.objects.create(
            name='Test',
            address='192.168.19.19'
        )

    def test_auth(self):
        response = self.client.get(reverse('host_delete', args=['1']))
        redirect_url = reverse('login') + '?next=' + reverse('host_delete', args=['1'])

        self.assertRedirects(response, redirect_url)

    def test_permission(self):
        self.user.user_permissions.remove(Permission.objects.get(codename='delete_host'))

        self.client.force_login(user=self.user)
        response = self.client.get(reverse('host_delete', args=['1']))

        self.assertRedirects(response, reverse('permission_denied'))

    def test_smoke(self):
        self.client.force_login(user=self.user)
        response = self.client.get(reverse('host_delete', args=['1']))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'core/host/delete.html')

    def test_delete_host(self):
        self.client.force_login(user=self.user)

        response = self.client.post(reverse('host_delete', args=['1']))

        self.assertEqual(len(models.Host.objects.all()), 0)
        self.assertRedirects(response, reverse('host_search'))
