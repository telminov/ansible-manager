from django.db.models import Count
from django.http import HttpResponse
from rest_framework.generics import ListAPIView
from rest_framework.views import APIView
from rest_framework.authentication import TokenAuthentication

from prometheus_client import generate_latest

from core import models
from core import serializers
from core import consts

tokenBearer = TokenAuthentication
tokenBearer.keyword = 'Bearer'


class TaskLogs(ListAPIView):
    model = models.TaskLog
    serializer_class = serializers.TaskLogSerializer

    def get_queryset(self):
        last_log_id = self.request.GET.get('last_log_id', 0)
        return self.model.objects.filter(task_id=self.kwargs['task_id'], id__gt=last_log_id)
task_logs = TaskLogs.as_view()


class DjangoMetrics(APIView):
    authentication_classes = (tokenBearer,)

    def get(self, request):
        result = generate_latest().decode()
        return HttpResponse(result, content_type='text/plain; charset=utf-8')


class AnsibleManagerMetrics(APIView):
    authentication_classes = (tokenBearer,)

    def get(self, request):
        result = '# HELP ansible_manager_template_last_task_success show success or fail last task\n'
        result += '# TYPE ansible_manager_template_last_task_success gauge\n'
        for template in models.TaskTemplate.objects.filter(cron__isnull=False):
            completed_tasks = template.tasks.filter(status__in=consts.NOT_RUN_STATUSES)
            if not completed_tasks:
                continue

            success = int(completed_tasks.last().status == consts.COMPLETED)
            result += 'ansible_manger_template_last_task_success{id="%s", name="%s"} %s\n' % (
                template.name, template.pk, success)

        result += '# HELP ansible_manager_tasks_completed_total show number of completed tasks\n'
        result += '# TYPE ansible_manager_tasks_completed_total gauge\n'
        tasks = models.Task.objects.values_list('template__id', 'template__name', 'status').annotate(count=Count('id'))
        for template_id, template_name, status, count in tasks:
            result += 'ansible_manager_tasks_completed_total{name="%s", id="%s", status="%s"} %s\n' % (
                template_id, template_name, status, count
            )

        return HttpResponse(result, content_type='text/plain; charset=utf-8')
