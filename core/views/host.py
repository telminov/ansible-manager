from django.shortcuts import redirect
from django.urls import reverse
from django.urls import reverse_lazy

import core.forms.host

from core import models
from core.generic import mixins
from core.generic import views


class Search(mixins.PermissionRequiredMixin, mixins.FormMixin, views.ListView):
    template_name = 'core/host/search.html'
    form_class = core.forms.host.Search
    paginate_by = 20
    title = 'Hosts'
    model = models.Host
    permission_required = 'core.view_host'

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
            address = form.cleaned_data.get('address')
            group = form.cleaned_data.get('group')

            if name:
                queryset = queryset.filter(name__icontains=name)
            if address:
                queryset = queryset.filter(address__contains=address)
            if group:
                queryset = queryset.filter(groups__in=[group, ])
        return queryset
search = Search.as_view()


class Edit(mixins.PermissionRequiredMixin, mixins.FormAndModelFormsetMixin, views.EditView):
    template_name = 'core/host/edit.html'
    form_class = core.forms.host.Edit
    model = models.Host
    formset_model = models.Variable
    permission_required = 'core.add_host'
    success_url = reverse_lazy('host_search')
    title_create = 'Create'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['instance'] = self.get_object()
        return kwargs

    def get_formset_initial(self):
        initial = self.formset_model.objects.none()
        obj = self.get_object()
        if obj:
            initial = self.formset_model.objects.filter(hosts__in=[obj, ])
        return initial

    def get_breadcrumbs(self):
        return (
            ('Home', reverse('index')),
            (Search.title, reverse('host_search')),
            (self.get_title(), '')
        )

    def form_valid(self, form, formset):
        self.object = form.save()
        variables = formset.save()
        self.object.vars.add(*variables)
        return redirect(self.get_success_url())
edit = Edit.as_view()


class Delete(mixins.PermissionRequiredMixin, views.DeleteView):
    template_name = 'core/host/delete.html'
    model = models.Host
    permission_required = 'core.delete_host'
    success_url = reverse_lazy('host_search')

    def get_title(self):
        obj = self.get_object()
        return "Delete %s" % obj

    def get_breadcrumbs(self):
        obj = self.get_object()
        return (
            ('Home', reverse('index')),
            (Search.title, reverse('host_search')),
            (str(obj), reverse('host_update', kwargs={'pk': obj.id})),
            ('Delete', '')
        )
delete = Delete.as_view()
