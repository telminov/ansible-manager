from django.urls import reverse

from core.generic.views import TemplateView


class Index(TemplateView):
    template_name = 'core/index.html'
    title = 'Ansible Manager Project'
index = Index.as_view()


class PermissionDenied(TemplateView):
    title = 'Permission denied'
    template_name = 'core/user/permission_denied.html'

    def get_breadcrumbs(self):
        return [
            ('Главная', reverse('index')),
            (self.get_title(), ''),
        ]

    # def get_context_data(self, **kwargs):
permission_denied = PermissionDenied.as_view()
