from django import forms

from core import models


class CronFormField(forms.CharField):
    def __init__(self, *args, **kwargs):
        defaults = {'widget': forms.TextInput}
        kwargs.update(defaults)
        super(CronFormField, self).__init__(*args, **kwargs)

    def validate(self, value):
        super(CronFormField, self).validate(value)
        models.validate_cron(value)
