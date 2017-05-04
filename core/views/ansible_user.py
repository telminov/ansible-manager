from django.shortcuts import redirect
from django.urls import reverse
from django.urls import reverse_lazy

import core.forms.ansible_user

from core import models
from core.generic import mixins
from core.generic import views


class Search(mixins.PermissionRequiredMixin, mixins.FormMixin, views.ListView):
    template_name = 'core/ansible_user/search.html'
    form_class = core.forms.ansible_user.Search
    paginate_by = 20
    title = 'Ansible Users'
    model = models.AnsibleUser
    permission_required = 'core.view_ansible_user'

    def get_breadcrumbs(self):
        return (
            ('Home', reverse('index')),
            (self.get_title(), '')
        )

    def get_queryset(self):
        queryset = super().get_queryset()
        form = self.get_form()
        if form.is_valid():
            name = form.cleaned_data.get('name')

            if name:
                queryset = queryset.filter(name__icontains=name)
        
        return queryset
search = Search.as_view()


class Edit(mixins.PermissionRequiredMixin, views.EditView):
    template_name = 'core/ansible_user/edit.html'
    form_class = core.forms.ansible_user.Edit
    model = models.AnsibleUser
    permission_required = 'core.add_ansibleuser'
    success_url = reverse_lazy('ansible_user_search')
    title_create = 'Create'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['instance'] = self.get_object()
        return kwargs

    def get_breadcrumbs(self):
        return (
            ('Home', reverse('index')),
            (Search.title, reverse('ansible_user_search')),
            (self.get_title(), '')
        )

    def form_valid(self, form):
        self.object = form.save()
        return redirect(self.get_success_url())
edit = Edit.as_view()


class Delete(mixins.PermissionRequiredMixin, views.DeleteView):
    template_name = 'core/ansible_user/delete.html'
    model = models.AnsibleUser
    permission_required = 'core.delete_ansibleuser'
    success_url = reverse_lazy('ansible_user_search')

    def get_title(self):
        obj = self.get_object()
        return "Delete %s" % obj

    def get_breadcrumbs(self):
        obj = self.get_object()
        return (
            ('Home', reverse('index')),
            (Search.title, reverse('ansible_user_search')),
            (str(obj), reverse('ansible_user_update', kwargs={'pk': obj.id})),
            ('Delete', '')
        )
delete = Delete.as_view()
