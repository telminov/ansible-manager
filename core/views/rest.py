from django.http import HttpResponse
from rest_framework.generics import ListAPIView
from rest_framework.views import APIView
from rest_framework.authentication import TokenAuthentication

from prometheus_client import generate_latest

from core import models
from core import serializers
from core import consts

tokenBeaver = TokenAuthentication
tokenBeaver.keyword = 'Bearer'


class TaskLogs(ListAPIView):
    model = models.TaskLog
    serializer_class = serializers.TaskLogSerializer

    def get_queryset(self):
        last_log_id = self.request.GET.get('last_log_id', 0)
        return self.model.objects.filter(task_id=self.kwargs['task_id'], id__gt=last_log_id)
task_logs = TaskLogs.as_view()


class DjangoMetrics(APIView):
    authentication_classes = (tokenBeaver, )

    def get(self, request):
        result = generate_latest().decode()

        return HttpResponse(result, content_type='text/plain; charset=utf-8')


class AnsibleManagerMetrics(APIView):
    authentication_classes = (tokenBeaver, )

    def get(self, reuqest):
        result = '# HELP ansible_manager_template_last_task_success show success or fail last task\n'
        result += '# TYPE ansible_manager_template_last_task_success gauge\n'
        deferred_result = ''
        for template in models.TaskTemplate.objects.filter(cron__isnull=False):
            completed_tasks = template.tasks.filter(status__in=consts.NOT_RUN_STATUSES)

            if completed_tasks.last().status == consts.COMPLETED:
                metric_value_last_task = 1
            else:
                metric_value_last_task = 0

            metric_value_fail = template.tasks.filter(status=consts.FAIL).count()
            metric_value_success = template.tasks.filter(status=consts.COMPLETED).count()

            result += 'ansible_manger_template_last_task_success{name="%s", id="%s"} %s\n' % (template.name,
                                                                                              template.pk,
                                                                                              metric_value_last_task)
            deferred_result += 'ansible_manager_tasks_completed_total{name="%s", id="%s", status="fail"} %s\n' % \
                               (template.name, template.pk, metric_value_fail)
            deferred_result += 'ansible_manager_tasks_completed_total{name="%s", id="%s", status="success"} %s\n' % \
                               (template.name, template.pk, metric_value_success)

        result += '# HELP ansible_manager_tasks_completed_total show number of completed tasks\n'
        result += '# TYPE ansible_manager_tasks_completed_total gauge\n'
        result += deferred_result

        return HttpResponse(result, content_type='text/plain; charset=utf-8')
