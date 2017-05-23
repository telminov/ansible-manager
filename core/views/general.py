from django.urls import reverse

from core import consts
from core import models
from core.generic.views import TemplateView


class Index(TemplateView):
    template_name = 'core/index.html'
    title = 'Ansible Manager Project'

    def get_tasks(self):
        return models.Task.objects.order_by('-dc')[:10]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['tasks'] = self.get_tasks()
        return context
index = Index.as_view()


class PermissionDenied(TemplateView):
    title = 'Permission denied'
    template_name = 'core/user/permission_denied.html'

    def get_breadcrumbs(self):
        return [
            ('Home', reverse('index')),
            (self.get_title(), ''),
        ]
permission_denied = PermissionDenied.as_view()
