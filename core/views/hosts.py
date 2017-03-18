from django.urls import reverse

import core.forms.host
from core import models

from core.generic import mixins
from core.generic import views


class Search(mixins.PermissionRequiredMixin, views.ListView):
    template_name = 'core/host/search.html'
    form_class = core.forms.host.HostSearch
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
        return queryset
search = Search.as_view()
