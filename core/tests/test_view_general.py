from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User

from core import models
from core.views.general import PermissionDenied


class IndexView(TestCase):

    def setUp(self):
        self.user = User.objects.create(
            username='Serega',
            password='passwd',
        )

    def test_auth(self):
        response = self.client.get(reverse('index'))
        redirect_url = reverse('login') + '?next=/'

        self.assertRedirects(response, redirect_url)

    def test_smoke(self):
        self.client.force_login(user=self.user)
        response = self.client.get(reverse('index'))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'core/index.html')

    def test_context(self):
        for x in ['in_progress', 'completed', 'stopped', 'fail', 'wait']:
            models.Task.objects.create(
                playbook='/home/',
                status=x,
                user=self.user,
            )
        self.client.force_login(user=self.user)
        response = self.client.get(reverse('index'))

        self.assertEqual(len(response.context['tasks']), 2)
        self.assertEqual(response.context['tasks'][0].status, 'in_progress')
        self.assertEqual(response.context['tasks'][1].status, 'wait')


class PermissionDeniedView(TestCase):

    def setUp(self):
        self.user = User.objects.create(
            username='Serega',
            password='passwd',
        )

    def test_auth(self):
        response = self.client.get(reverse('permission_denied'))
        redirect_url = reverse('login') + '?next=' + reverse('permission_denied')

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
