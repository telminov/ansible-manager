from rest_framework.generics import ListAPIView

from core import models
from core import serializers


class TaskLogs(ListAPIView):
    model = models.TaskLog
    serializer_class = serializers.TaskLogSerializer

    def get_queryset(self):
        last_log_id = self.request.GET.get('last_log_id', 0)
        return self.model.objects.filter(task_id=self.kwargs['task_id'], id__gt=last_log_id)
task_logs = TaskLogs.as_view()
