import urllib.parse

from django.shortcuts import redirect
from django.urls import reverse
from django.views.generic.base import ContextMixin
from django.contrib.auth.mixins import PermissionRequiredMixin as PermissionRequiredMixinAuth


class BreadcrumbsMixin(ContextMixin):

    def get_breadcrumbs(self):
        return None

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['breadcrumbs'] = self.get_breadcrumbs()
        return context


class TitleMixin(ContextMixin):
    title = None

    def get_title(self):
        return self.title

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = self.get_title()
        return context


class PermissionRequiredMixin(PermissionRequiredMixinAuth):

    def handle_no_permission(self):
        url = reverse('permission_denied')

        previous_url = self.request.META.get('HTTP_REFERER')
        if previous_url:
            url += '?next=%s' % urllib.parse.quote(previous_url)

        return redirect(url)
