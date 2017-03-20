from django.contrib import messages
from django.shortcuts import redirect
from django.urls import reverse
from django.views.generic.detail import SingleObjectMixin

import core.forms.task
from core import consts

from core import models
from core.generic import mixins
from core.generic import views


class Search(mixins.PermissionRequiredMixin, mixins.FormMixin, views.ListView):
    template_name = 'core/task/search.html'
    form_class = core.forms.task.Search
    paginate_by = 20
    title = 'Search tasks'
    model = models.Task
    permission_required = 'core.view_task'

    def get_breadcrumbs(self):
        return (
            ('Home', reverse('index')),
            (self.get_title(), '')
        )

    def get_queryset(self):
        queryset = super().get_queryset()
        # TODO
        return queryset
search = Search.as_view()


class Stop(mixins.PermissionRequiredMixin, views.DetailView):
    template_name = 'core/task/stop.html'
    permission_required = 'core.stop_task'
    model = models.Task

    def get_title(self):
        task = self.get_object()
        return "Stop task for %s" % task.get_playbook_name()

    def post(self, *args, **kwargs):
        task = self.get_object()
        if task.status == consts.IN_PROGRESS:
            task.stop()
        else:
            messages.info(self.request, 'Task is already stopped')
        return redirect('task_log', kwargs={'pk': task.id})
stop = Stop.as_view()


class Log(mixins.PermissionRequiredMixin, views.DetailView):
    template_name = 'core/task/log.html'
    model = models.Task
    permission_required = 'core.view_task_log'

    def get_title(self):
        task = self.get_object()
        return 'Log task for %s' % task.dc.strftime("%d/%m/%y")

    def get_breadcrumbs(self):
        return (
            ('Home', reverse('index')),
            ('Search tasks', reverse('task_search')),
            (self.get_title(), '')
        )
log = Log.as_view()