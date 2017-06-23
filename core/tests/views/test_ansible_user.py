from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from django.contrib.auth.models import Permission

from core import models
from core.views import ansible_user


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

        self.assertRedirects(response, redirect_url)

    def test_permission(self):
        self.user.user_permissions.remove(Permission.objects.get(codename='view_ansible_user'))

        self.client.force_login(user=self.user)
        response = self.client.get(reverse('ansible_user_search'))

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

        self.assertRedirects(response, redirect_url)

    def test_permission(self):
        self.user.user_permissions.remove(Permission.objects.get(codename='add_ansibleuser'))

        self.client.force_login(user=self.user)
        response = self.client.get(reverse('ansible_user_create'))

        self.assertRedirects(response, reverse('permission_denied'))

    def test_smoke(self):
        self.client.force_login(user=self.user)
        response = self.client.get(reverse('ansible_user_create'))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'core/ansible_user/edit.html')

    def test_create(self):
        self.user.user_permissions.add(Permission.objects.get(codename='view_ansible_user'))
        self.client.force_login(user=self.user)
        response = self.client.post(reverse('ansible_user_create'), {'name': 'Test name'})

        self.assertEqual(str(models.AnsibleUser.objects.get(id=1)), 'Test name')
        self.assertRedirects(response, reverse('ansible_user_search'))

    def test_create_invalid(self):
        self.client.force_login(user=self.user)
        response = self.client.post(reverse('ansible_user_create'), {'name': '  '})

        self.assertContains(response, 'This field is required.')

    def test_edit(self):
        self.user.user_permissions.add(Permission.objects.get(codename='view_ansible_user'))
        models.AnsibleUser.objects.create(
            name='Test name'
        )
        self.client.force_login(user=self.user)
        response = self.client.post(reverse('ansible_user_update', args=['1']), {'name': 'blabla test'})

        self.assertEqual(str(models.AnsibleUser.objects.get(id=1)), 'blabla test')
        self.assertRedirects(response, reverse('ansible_user_search'))

    def test_edit_invalid(self):
        models.AnsibleUser.objects.create(
            name='Test name'
        )
        self.client.force_login(user=self.user)
        response = self.client.post(reverse('ansible_user_update', args=['1']), {'name': '  '})

        self.assertContains(response, 'This field is required.')

    def test_context_create(self):
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

        self.assertRedirects(response, redirect_url)

    def test_permission(self):
        self.user.user_permissions.remove(Permission.objects.get(codename='delete_ansibleuser'))

        self.client.force_login(user=self.user)
        response = self.client.get(reverse('ansible_user_delete', args=['1']))

        self.assertRedirects(response, reverse('permission_denied'))

    def test_smoke(self):
        self.client.force_login(user=self.user)
        response = self.client.get(reverse('ansible_user_delete', args=['1']))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'core/ansible_user/delete.html')

    def test_delete(self):
        self.user.user_permissions.add(Permission.objects.get(codename='view_ansible_user'))
        self.client.force_login(user=self.user)
        response = self.client.post(reverse('ansible_user_delete', args=['1']))

        self.assertEqual(len(models.AnsibleUser.objects.all()), 0)
        self.assertRedirects(response, reverse('ansible_user_search'))

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
