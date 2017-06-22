import pytz
import os

from django.contrib import messages
from django.http import HttpResponse
from django.shortcuts import redirect
from django.urls import reverse
from django.urls import reverse_lazy
from django.views.generic.detail import SingleObjectMixin
from djutils.views.generic import SortMixin

import core.forms.task
from core import consts
from core.utils import get_timezone
from core import models
from core.datatools import ansible
from core.generic import mixins
from core.generic import views


class Search(mixins.PermissionRequiredMixin, SortMixin, mixins.FormMixin, views.ListView):
    template_name = 'core/task/search.html'
    form_class = core.forms.task.Search
    paginate_by = 15
    title = 'Tasks'
    model = models.Task
    permission_required = 'core.view_task'
    sort_params = ['-dc', 'template', 'dc']

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
        form = self.get_form()
        if form.is_valid():
            template = form.cleaned_data.get('template')
            playbook = form.cleaned_data.get('playbook')
            status = form.cleaned_data.get('status')
            if template:
                queryset = queryset.filter(template=template)
            if playbook:
                queryset = queryset.filter(playbook=playbook)
            if status:
                queryset = queryset.filter(status=status)
        return queryset
search = Search.as_view()


class Create(mixins.PermissionRequiredMixin, mixins.FormAndModelFormsetMixin, views.EditView):
    template_name = 'core/task/create.html'
    form_class = core.forms.task.Create
    model = models.Task
    formset_model = models.Variable
    permission_required = 'core.add_task'
    success_url = reverse_lazy('task_search')
    title_create = 'Create'

    def get_breadcrumbs(self):
        return (
            ('Home', reverse('index')),
            (Search.title, reverse('task_search')),
            (self.get_title(), '')
        )

    def form_valid(self, form, formset):
        form.instance.user = self.request.user
        self.object = form.save()
        variables = formset.save()
        self.object.vars.add(*variables)
        return redirect(self.get_success_url())
create = Create.as_view()


class Stop(mixins.PermissionRequiredMixin, views.DetailView):
    template_name = 'core/task/stop.html'
    permission_required = 'core.stop_task'
    model = models.Task
    title = 'Stop'

    def get_breadcrumbs(self):
        task = self.get_object()
        return (
            ('Home', reverse('index')),
            (Search.title, reverse('task_search')),
            (str(task), reverse('task_log', kwargs={'pk': task.id})),
            (self.get_title(), '')
        )

    def post(self, *args, **kwargs):
        task = self.get_object()
        if task.status in consts.RUN_STATUSES:
            task.stop()
        else:
            messages.info(self.request, 'Task is not run')
        return redirect('task_search')
stop = Stop.as_view()


class Replay(mixins.PermissionRequiredMixin, SingleObjectMixin, views.View):
    permission_required = 'core.replay_task'
    model = models.Task

    def get(self, *args, **kwargs):
        task = self.get_object()
        if task.status in consts.NOT_RUN_STATUSES:
            hosts = task.hosts.all()
            groups = task.host_groups.all()
            vars = task.vars.all()

            task.id = None
            task.pid = None
            task.status = consts.WAIT
            task.save()

            task.hosts.add(*hosts)
            task.host_groups.add(*groups)
            task.vars.add(*vars)

            models.TaskLog.objects.create(
                task=task,
                status=consts.IN_PROGRESS,
                message='Replay task'
            )
        else:
            messages.info(self.request, 'Not start duplicate task')
        return redirect(reverse('task_log', kwargs={'pk': task.id}))
replay = Replay.as_view()


class Log(mixins.PermissionRequiredMixin, views.DetailView):
    template_name = 'core/task/log.html'
    model = models.Task
    permission_required = 'core.view_task_log'

    def get_title(self):
        task = self.get_object()
        tz = self.request.session.get('detected_tz')
        if tz:
            timezone = pytz.timezone(str(get_timezone(tz)))
            return 'Log %s task for %s' % (task.template if task.template else '',
                                           task.dc.astimezone(timezone).strftime("%d-%m-%Y %H:%M:%S"))
        else:
            return 'Log %s task for %s' % (task.template if task.template else '', task.dc.strftime("%d-%m-%Y %H:%M:%S"))

    def get_breadcrumbs(self):
        return (
            ('Home', reverse('index')),
            (Search.title, reverse('task_search')),
            (self.get_title(), '')
        )
log = Log.as_view()


class Inventory(mixins.PermissionRequiredMixin, SingleObjectMixin, views.View):
    permission_required = 'core.inventory_task'
    model = models.Task

    def get(self, *args, **kwargs):
        task = self.get_object()
        inventory_path = ansible.create_inventory(task)
        with open(inventory_path) as inventory_file:
            inventory_content = inventory_file.read()
        os.remove(inventory_path)
        return HttpResponse(inventory_content, content_type='text/plain')
inventory = Inventory.as_view()

