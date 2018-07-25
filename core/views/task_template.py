import os

from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from django.db.models import Max
from django.contrib import messages
from django.shortcuts import redirect
from django.urls import reverse
from django.urls import reverse_lazy
from django.views.generic.detail import SingleObjectMixin
from django.forms import modelformset_factory
from djutils.views.generic import SortMixin

import core.forms.task_template
from core import consts

from core import models
from core.datatools import ansible
from core.generic import mixins
from core.generic import views


class Search(mixins.PermissionRequiredMixin, SortMixin, mixins.FormMixin, views.ListView):
    template_name = 'core/task_template/search.html'
    form_class = core.forms.task_template.Search
    paginate_by = 15
    title = 'Task templates'
    model = models.TaskTemplate
    permission_required = 'core.view_task_template'
    sort_params = ['name', 'last_task']

    def get_paginate_by(self, queryset):
        if self.request.GET.get('paginate_by') == '-1':
            paginate_by = queryset.count()
        elif self.request.GET.get('paginate_by'):
            paginate_by = self.request.GET.get('paginate_by')
        else:
            paginate_by = self.paginate_by
        return paginate_by

    def get_breadcrumbs(self):
        return (
            ('Home', reverse('index')),
            (self.get_title(), '')
        )

    def get_queryset(self):
        queryset = super().get_queryset()
        if self.sort_qs:
            order_by = self.request.GET[self.sort_param_name]
            if order_by == 'last_task':
                queryset = queryset.annotate(last_task=Max('tasks__dc')).order_by('last_task')
            elif order_by == '-last_task':
                queryset = queryset.annotate(last_task=Max('tasks__dc')).order_by('last_task').reverse()
            else:
                queryset = queryset.order_by(order_by)

        form = self.get_form()
        if form.is_valid():
            name = form.cleaned_data.get('name')
            hosts = form.cleaned_data.get('hosts')
            host_groups = form.cleaned_data.get('host_groups')

            if name:
                queryset = queryset.filter(name__icontains=name)

            if hosts:
                queryset = queryset.filter(hosts__in=hosts)

            if host_groups:
                queryset = queryset.filter(host_groups__in=host_groups)
        return queryset

search = Search.as_view()


class Edit(mixins.PermissionRequiredMixin, mixins.FormAndModelFormsetMixin, views.EditView):
    template_name = 'core/task_template/edit.html'
    form_class = core.forms.task_template.Edit
    model = models.TaskTemplate
    formset_model = models.Variable
    permission_required = 'core.add_tasktemplate'
    title_create = 'Create'

    def get_success_url(self):
        if 'pk' in self.kwargs:
            pk = self.kwargs['pk']
        else:
            pk = self.object.id
        return reverse_lazy('task_template_update', kwargs={'pk': pk})

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['instance'] = self.get_object()
        kwargs['current_user'] = self.request.user
        return kwargs

    def get_formset_initial(self):
        initial = self.formset_model.objects.none()
        obj = self.get_object()
        if obj:
            initial = self.formset_model.objects.filter(task_templates__in=[obj, ])
        return initial

    def get_breadcrumbs(self):
        return (
            ('Home', reverse('index')),
            (Search.title, reverse('task_template_search')),
            (self.get_title(), '')
        )

    def form_valid(self, form, formset):
        self.object = form.save()
        variables = formset.save()
        self.object.vars.add(*variables)
        return redirect(self.get_success_url())

    def get_context_data(self, *args, **kwargs):
        c = super().get_context_data(*args, **kwargs)
        if self.get_object():
            c['last_tasks'] = self.get_object().tasks.order_by('-id')[:10]
            c['repeat_count'] = self.get_object().repeat_settings.count()
        return c

edit = Edit.as_view()


class Copy(mixins.PermissionRequiredMixin, views.FormView):
    template_name = 'core/task_template/copy.html'
    form_class = core.forms.task_template.Copy
    permission_required = 'core.add_tasktemplate'
    title = 'Copy'

    def get_breadcrumbs(self):
        return (
            ('Home', reverse('index')),
            (Search.title, reverse('task_template_search')),
            (str(self.get_object()), reverse('task_template_update', kwargs={'pk': self.get_object().id})),
            (self.title, '')
        )

    def get_initial(self):
        kwargs = super().get_initial()
        kwargs['name'] = self.get_object().name
        return kwargs

    def get_object(self):
        obj = get_object_or_404(models.TaskTemplate, pk=self.kwargs['pk'])
        return obj

    def form_valid(self, form):
        source_template = self.get_object()
        self.new_template = models.TaskTemplate.objects.create(
            name=form.cleaned_data['name'],
            description=source_template.description,
            playbook=source_template.playbook,
            verbose=source_template.verbose,
            ansible_user=source_template.ansible_user,
            cron=source_template.cron,
            cron_dt=source_template.cron_dt,
        )

        self.new_template.hosts.add(*source_template.hosts.all())
        self.new_template.host_groups.add(*source_template.host_groups.all())

        vars = []
        for var in source_template.vars.all():
            var = models.Variable.objects.create(
                name=var.name,
                value=var.value
            )
            vars.append(var)

        self.new_template.vars.add(*vars)

        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('task_template_update', kwargs={'pk': self.new_template.pk})

copy = Copy.as_view()


class Delete(mixins.PermissionRequiredMixin, views.DeleteView):
    template_name = 'core/task_template/delete.html'
    model = models.TaskTemplate
    permission_required = 'core.delete_tasktemplate'
    success_url = reverse_lazy('task_template_search')

    def get_title(self):
        obj = self.get_object()
        return "Delete %s" % obj

    def get_breadcrumbs(self):
        obj = self.get_object()
        return (
            ('Home', reverse('index')),
            (Search.title, reverse('task_template_search')),
            (str(obj), reverse('task_template_update', kwargs={'pk': obj.id})),
            ('Delete', '')
        )
delete = Delete.as_view()


class Run(mixins.PermissionRequiredMixin, SingleObjectMixin, views.View):
    permission_required = 'core.run_task'
    model = models.TaskTemplate

    def get(self, request, *args, **kwargs):
        task_template = self.get_object()
        task_hosts = task_template.hosts.all()
        user_hosts = task_hosts.filter(users__in=[self.request.user])

        if user_hosts.count() == task_hosts.count():
            in_progress_tasks = task_template.tasks.filter(status__in=consts.RUN_STATUSES)
            if in_progress_tasks.exists():
                messages.info(self.request, 'The same task was not started. You have been redirected to a running task.')
                task = in_progress_tasks.last()
            else:
                task = task_template.create_task(self.request.user)

            return redirect(reverse('task_log', kwargs={'pk': task.id}))
        else:
            messages.info(self.request, 'This user does not have an acces to this host')
            return redirect(reverse('task_search'))
run = Run.as_view()


class Inventory(mixins.PermissionRequiredMixin, SingleObjectMixin, views.View):
    permission_required = 'core.inventory_task'
    model = models.TaskTemplate

    def get(self, *args, **kwargs):
        task_template = self.get_object()

        if task_template.inventory:
            inventory_path = task_template.inventory.path
        else:
            inventory_path = ansible.create_inventory(task_template)

        with open(inventory_path) as inventory_file:
            inventory_content = inventory_file.read()

        if not task_template.inventory:
            os.remove(inventory_path)

        return HttpResponse(inventory_content, content_type='text/plain')
inventory = Inventory.as_view()


class RepeatSettings(mixins.PermissionRequiredMixin, views.FormView):
    permission_required = 'core.add_tasktemplate'
    form_class = modelformset_factory(models.RepeatSetting, fields=('pause',), can_delete=True,)
    template_name = 'core/task_template/repeat_setting.html'
    title = 'Repeat Settings'

    def get_breadcrumbs(self):
        return (
            ('Home', reverse('index')),
            (Search.title, reverse('task_template_search')),
            (str(models.TaskTemplate.objects.get(id=self.kwargs['pk'])), reverse('task_template_update',
                                                                                 kwargs={'pk': self.kwargs['pk']})),
            (self.title, '')
        )

    def get_success_url(self):
        return reverse_lazy('task_template_update', kwargs={'pk': self.kwargs['pk']})

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        queryset = models.RepeatSetting.objects.filter(template=models.TaskTemplate.objects.get(id=self.kwargs['pk']))
        kwargs['queryset'] = queryset
        return kwargs

    def form_valid(self, form):
        self.object = models.TaskTemplate.objects.get(id=self.kwargs['pk'])

        for f in form.forms:
            f.instance.template = self.object
        form.save()

        return redirect(self.get_success_url())

repeat_settings = RepeatSettings.as_view()
