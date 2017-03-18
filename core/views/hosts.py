from django.urls import reverse

import core.forms.host
from core import models

from core.generic import mixins
from core.generic import views


class Search(mixins.PermissionRequiredMixin, mixins.FormMixin, views.ListView):
    template_name = 'core/host/search.html'
    form_class = core.forms.host.Search
    paginate_by = 20
    title = 'Search hosts'
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
                queryset = queryset.filter(address=address)
            if group:
                queryset = queryset.filter(groups__in=[group, ])
        return queryset
search = Search.as_view()


class Create(mixins.PermissionRequiredMixin, mixins.FormAndModelFormsetMixin, views.CreateView):
    template_name = 'core/host/create.html'
    title = 'Create host'
    form_class = core.forms.host.Edit
    model = models.Host
    formset_model = models.Variable
    permission_required = 'core.add_host'

    def get_breadcrumbs(self):
        return (
            ('Home', reverse('index')),
            ('Search hosts', reverse('host_search')),
            (self.get_title(), '')
        )

create = Create.as_view()


class Update(mixins.PermissionRequiredMixin, views.UpdateView):
    template_name = 'core/host/update.html'
    form_class = core.forms.host.Edit
    model = models.Host
    permission_required = 'core.change_host'

    def get_title(self):
        obj = self.get_object()
        return 'Update host %s' % obj

    def get_breadcrumbs(self):
        return (
            ('Home', reverse('index')),
            ('Search hosts', reverse('host_search')),
            (self.get_title(), '')
        )
update = Update.as_view()


class Delete(mixins.PermissionRequiredMixin, views.DeleteView):
    template_name = 'core/host/delete.html'
    model = models.Host
    permission_required = 'core.delete_host'

    def get_title(self):
        obj = self.get_object()
        return "Delete %s" % obj
delete = Delete.as_view()
