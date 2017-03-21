import urllib.parse

from django.forms import modelformset_factory
from django.shortcuts import redirect
from django.urls import reverse
from django.views.generic.base import ContextMixin
from django.contrib.auth.mixins import PermissionRequiredMixin as PermissionRequiredMixinAuth
from django.views.generic.edit import FormMixin as DjangoFormMixin


class BreadcrumbsMixin(ContextMixin):

    def get_breadcrumbs(self):
        return None

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['breadcrumbs'] = self.get_breadcrumbs()
        return context


class PermissionRequiredMixin(PermissionRequiredMixinAuth):

    def handle_no_permission(self):
        url = reverse('permission_denied')

        previous_url = self.request.META.get('HTTP_REFERER')
        if previous_url:
            url += '?next=%s' % urllib.parse.quote(previous_url)

        return redirect(url)


class FormMixin(DjangoFormMixin):
    data_method = None

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['data'] = getattr(self.request, self.data_method.upper() if self.data_method else 'GET') or None
        return kwargs


class FormAndFormsetMixin(FormMixin):
    formset_class = None
    data_method = 'post'
    formset_initial = None

    def get_formset_class(self):
        return self.formset_class

    def get_formset_initial(self):
        return self.formset_initial or []

    def get_formset_kwargs(self):
        kwargs = {
            'queryset': self.get_formset_initial(),
            'files': self.request.FILES or None,
            'data': getattr(self.request, self.data_method.upper() if self.data_method else 'GET') or None,
        }
        return kwargs

    def get_formset(self, clean=False):
        kwargs = {} if clean else self.get_formset_kwargs()
        return self.get_formset_class()(**kwargs)

    def post(self, request, *args, **kwargs):
        form = self.get_form()
        formset = self.get_formset()
        if form.is_valid() and formset.is_valid():
            return self.form_valid(form, formset)
        else:
            return self.form_invalid(form, formset)

    def form_invalid(self, form, formset):
        return self.render_to_response(self.get_context_data(formset=formset, form=form))

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['formset'] = kwargs.get('formset') or self.get_formset()
        return context

    def form_valid(self, form, formset):
        return redirect(self.get_success_url())


class FormAndModelFormsetMixin(FormAndFormsetMixin):
    formset_model = None

    def get_formset_initial(self):
        return self.formset_initial or self.formset_model.objects.none()

    def get_formset_class(self):
        return self.formset_class or modelformset_factory(model=self.formset_model, fields='__all__', can_delete=True)


class NextMixin(ContextMixin):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['next'] = self.request.META.get('HTTP_REFERER', self.request.GET.get('next'))
        return context
