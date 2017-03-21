from django.contrib import messages
from django.shortcuts import redirect
from django.urls import reverse
from django.urls import reverse_lazy
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
    title_create = 'Create Task'

    def get_breadcrumbs(self):
        return (
            ('Home', reverse('index')),
            ('Search tasks', reverse('task_search')),
            (self.get_title(), '')
        )

    def form_invalid(self, form, formset):
        return super().form_invalid(form, formset)

    def form_valid(self, form, formset):
        form.instance.user = self.request.user
        self.object = form.save()
        variables = formset.save()
        self.object.vars.add(*variables)
        return redirect(self.get_success_url())
create = Create.as_view()


class Stop(mixins.PermissionRequiredMixin, SingleObjectMixin, views.View):
    permission_required = 'core.stop_task'
    model = models.Task

    def get(self, *args, **kwargs): # TODO Post , Get - message
        task = self.get_object()
        if task.status == consts.IN_PROGRESS:
            task.stop()
        else:
            messages.info(self.request, 'Task is already finished')
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
        else:
            messages.info(self.request, 'Not start duplicate task')
        return redirect('task_search')
replay = Replay.as_view()


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