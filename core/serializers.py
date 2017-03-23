from rest_framework import serializers

from core import models


class TaskLogSerializer(serializers.ModelSerializer):
    task_status = serializers.SerializerMethodField()

    class Meta:
        model = models.TaskLog
        fields = '__all__'

    def get_task_status(self, obj):
        return obj.task.status
