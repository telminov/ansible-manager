from django.views.generic import (
    DeleteView as DjangoDeleteView,
    TemplateView as DjangoTemplateView,
    ListView as DjangoListView,
    DetailView as DjangoDetailView,
    View as DjangoView,
    CreateView as DjangoCreateView,
    UpdateView as DjangoUpdateView,
)
from djutils.views.generic import TitleMixin

from core.generic import mixins


class TemplateView(mixins.BreadcrumbsMixin, mixins.NextMixin, TitleMixin, DjangoTemplateView):
    pass


class View(mixins.BreadcrumbsMixin, mixins.NextMixin, TitleMixin, DjangoView):
    pass


class ListView(mixins.BreadcrumbsMixin, mixins.NextMixin, TitleMixin, DjangoListView):
    pass


class DetailView(mixins.BreadcrumbsMixin, mixins.NextMixin, TitleMixin, DjangoDetailView):
    pass


class DeleteView(mixins.BreadcrumbsMixin, mixins.NextMixin, TitleMixin, DjangoDeleteView):
    pass


class CreateView(mixins.BreadcrumbsMixin, mixins.NextMixin, TitleMixin, DjangoCreateView):
    pass


class UpdateView(mixins.BreadcrumbsMixin, mixins.NextMixin, TitleMixin, DjangoUpdateView):
    pass


class EditView(CreateView):
    object = None
    title_create = ''

    def get_object(self):
        obj = None
        if 'pk' in self.kwargs:
            obj = self.model.objects.get(id=self.kwargs['pk'])
            self.object = obj
        return obj

    def get_title(self):
        obj = self.get_object()
        title = self.title_create
        if obj:
            title = str(obj)
        return title
