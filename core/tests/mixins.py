from django.contrib.auth.models import Permission
from django.urls import reverse


class TestDefaultMixin(object):

    def test_auth(self):
        response = self.client.get(self.url)
        redirect_url = reverse('login') + '?next=' + self.url

        self.assertRedirects(response, redirect_url)

    def test_permissions(self):
        self.user.user_permissions.remove(Permission.objects.get(codename=self.pem))

        self.client.force_login(user=self.user)
        response = self.client.get(self.url)

        self.assertRedirects(response, reverse('permission_denied'))

    def test_smoke(self):
        self.client.force_login(user=self.user)
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
