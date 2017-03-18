from django.views.generic import (
    DeleteView as DjangoDeleteView,
    TemplateView as DjangoTemplateView,
    ListView as DjangoListView,
    DetailView as DjangoDetailView,
    View as DjangoView
)

from core.generic import mixins


class TemplateView(mixins.BreadcrumbsMixin, mixins.TitleMixin, DjangoTemplateView):
    pass


class View(mixins.BreadcrumbsMixin, mixins.TitleMixin, DjangoView):
    pass


class ListView(mixins.BreadcrumbsMixin, mixins.TitleMixin, DjangoListView):
    pass


class DetailView(mixins.BreadcrumbsMixin, mixins.TitleMixin, DjangoDetailView):
    pass


class DeleteView(mixins.BreadcrumbsMixin, mixins.TitleMixin, DjangoDeleteView):
    pass
