from django.shortcuts import redirect
from django.urls import reverse
from django.urls import reverse_lazy

import core.forms.host_group

from core import models
from core.generic import mixins
from core.generic import views


class Search(mixins.PermissionRequiredMixin, mixins.FormMixin, views.ListView):
    template_name = 'core/host_group/search.html'
    form_class = core.forms.host_group.Search
    paginate_by = 20
    title = 'Host groups'
    model = models.HostGroup
    permission_required = 'core.view_host_group'

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


class Edit(mixins.PermissionRequiredMixin, mixins.FormAndModelFormsetMixin, views.EditView):
    template_name = 'core/host_group/edit.html'
    form_class = core.forms.host_group.Edit
    model = models.HostGroup
    formset_model = models.Variable
    permission_required = 'core.add_hostgroup'
    success_url = reverse_lazy('host_group_search')
    title_create = 'Create'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['instance'] = self.get_object()
        if self.get_object():
            kwargs['initial'] = {'hosts': self.get_object().hosts.all()}
        return kwargs

    def get_formset_initial(self):
        initial = self.formset_model.objects.none()
        obj = self.get_object()
        if obj:
            initial = self.formset_model.objects.filter(host_groups__in=[obj, ])
        return initial

    def get_breadcrumbs(self):
        return (
            ('Home', reverse('index')),
            (Search.title, reverse('host_group_search')),
            (self.get_title(), '')
        )

    def form_valid(self, form, formset):
        self.object = form.save()
        variables = formset.save()
        self.object.vars.add(*variables)
        self.object.hosts = form.cleaned_data['hosts']
        return redirect(self.get_success_url())
edit = Edit.as_view()


class Delete(mixins.PermissionRequiredMixin, views.DeleteView):
    template_name = 'core/host_group/delete.html'
    model = models.HostGroup
    permission_required = 'core.delete_host_group'
    success_url = reverse_lazy('host_group_search')

    def get_title(self):
        obj = self.get_object()
        return "Delete %s" % obj

    def get_breadcrumbs(self):
        obj = self.get_object()
        return (
            ('Home', reverse('index')),
            ('Search host group', reverse('host_group_search')),
            (str(obj), reverse('host_group_update', kwargs={'pk': obj.id})),
            ('Delete', '')
        )
delete = Delete.as_view()
