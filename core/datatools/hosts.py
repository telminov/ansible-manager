from django.contrib.auth.models import User

from core import models


def get_allowed_hosts(user: User):
    hosts = models.Host.objects.all()
    if user.is_superuser:
        return hosts

    return hosts.filter(users__in=[user, ])
