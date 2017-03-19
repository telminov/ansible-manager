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
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['next'] = self.request.META.get('HTTP_REFERER', self.request.GET.get('next'))
        return context


class CreateView(mixins.BreadcrumbsMixin, mixins.TitleMixin, DjangoCreateView):
    pass


class UpdateView(mixins.BreadcrumbsMixin, mixins.TitleMixin, DjangoUpdateView):
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
