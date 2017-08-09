from django.http import HttpResponse
from rest_framework.generics import ListAPIView
from rest_framework.views import APIView
from rest_framework.authentication import TokenAuthentication

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


class Metrics(APIView):
    authentication_classes = (tokenBeaver, )

    def get(self, request):
        result = '# HELP ansible_manager_template_last_task_success show success or fail last task\n'
        result += '# TYPE ansible_manager_template_last_task_success gauge\n'
        deferred_result = ''
        for template in models.TaskTemplate.objects.filter(cron__isnull=False):
            if not template.tasks.last():
                continue

            if template.tasks.last().status == consts.FAIL:
                metric_value_last_task = 0
            else:
                metric_value_last_task = 1

            metric_value_fail = template.tasks.filter(status=consts.FAIL).count()
            metric_value_success = template.tasks.filter(status=consts.COMPLETED).count()
            metric_value_count = metric_value_fail + metric_value_success

            result += 'ansible_manger_template_last_task_success{name="%s", id="%s"} %s\n' % (template.name,
                                                                                              template.pk, metric_value_last_task)
            deferred_result += 'ansible_manager_template_tasks_completed_total{name="%s", id="%s", fail="%s", success="%s"} %s\n' % \
                               (template.name, template.pk, metric_value_fail, metric_value_success, metric_value_count)

        result += '# HELP ansible_manager_template_tasks_completed_total show number of completed tasks\n'
        result += '# TYPE ansible_manager_template_tasks_completed_total gauge\n'
        result += deferred_result

        return HttpResponse(result, content_type='text/plain; charset=utf-8')
