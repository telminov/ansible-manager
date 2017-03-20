from rest_framework.generics import ListAPIView

from core import models


class TaskLogs(ListAPIView):
    model = models.TaskLog

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset
task_logs = TaskLogs.as_view()
