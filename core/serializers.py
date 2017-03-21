from rest_framework import serializers

from core import models


class TaskLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.TaskLog
        fields = '__all__'
