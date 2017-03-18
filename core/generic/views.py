from django.views.generic import (
    DeleteView as DjangoDeleteView,
    TemplateView as DjangoTemplateView,
    ListView as DjangoListView,
    DetailView as DjangoDetailView,
    View as DjangoView,
    CreateView as DjangoCreateView,
    UpdateView as DjangoUpdateView,
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


class CreateView(mixins.BreadcrumbsMixin, mixins.TitleMixin, DjangoCreateView):
    pass


class UpdateView(mixins.BreadcrumbsMixin, mixins.TitleMixin, DjangoUpdateView):
    pass
