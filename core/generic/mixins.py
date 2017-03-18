from django.views.generic.base import ContextMixin


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
