from django import forms
from django.conf import settings
from django.db.models.functions import Lower
from django.utils import timezone

from core.datatools.hosts import get_allowed_hosts
from core.forms.fields import CronFormField
from core import models


class Search(forms.Form):
    name = forms.CharField(required=False)
    hosts = forms.ModelMultipleChoiceField(required=False, queryset=models.Host.objects.order_by(Lower('name')),
                                           widget=forms.SelectMultiple(attrs={'class': 'need-select2'}))
    host_groups = forms.ModelMultipleChoiceField(label='Groups', required=False,
                                                 queryset=models.HostGroup.objects.order_by(Lower('name')),
                                                 widget=forms.SelectMultiple(attrs={'class': 'need-select2'}))


class Edit(forms.ModelForm):
    hosts = forms.ModelMultipleChoiceField(queryset=models.Host.objects.order_by(Lower('name')), required=False,
                                           widget=forms.SelectMultiple(attrs={'class': 'need-select2'}))
    host_groups = forms.ModelMultipleChoiceField(queryset=models.HostGroup.objects.order_by(Lower('name')),
                                                 required=False,
                                                 widget=forms.SelectMultiple(attrs={'class': 'need-select2'}))
    playbook = forms.FilePathField(path=settings.ANSIBLE_PLAYBOOKS_PATH, match='.*\.yml$',
                                   widget=forms.Select(attrs={'class': 'need-select2'}))
    ansible_user = forms.ModelChoiceField(queryset=models.AnsibleUser.objects.all(),
                                          widget=forms.Select(attrs={'class': 'need-select2'}))

    cron = CronFormField(widget=forms.TextInput, required=False)

    class Meta:
        model = models.TaskTemplate
        exclude = ('vars', )

    def __init__(self, current_user, *args, **kwargs):
        self.user = current_user
        super().__init__(*args, **kwargs)
        self.fields['ansible_user'].initial = models.AnsibleUser.objects.first()
        self.fields['playbook'] = forms.FilePathField(path=settings.ANSIBLE_PLAYBOOKS_PATH, match='.*\.yml$',
                                                      widget=forms.Select(attrs={'class': 'need-select2'}))
        self.fields['hosts'].queryset = get_allowed_hosts(self.user)

    def save(self, commit=True, *args, **kwargs):
        task_template = super(Edit, self).save(commit=False, *args, **kwargs)
        if task_template.cron and not task_template.cron_dt:
            task_template.cron_dt = timezone.now()
        elif not task_template.cron:
            task_template.cron_dt = None
        elif task_template.cron and 'cron' in self.changed_data:
            task_template.cron_dt = timezone.now()
        if commit:
            task_template.save()
            self.save_m2m()
        return task_template


class Copy(forms.Form):
    name = forms.CharField()

    def clean_name(self):
        name = self.cleaned_data['name']
        if models.TaskTemplate.objects.filter(name=name).exists():
            raise forms.ValidationError('Template with name alreay exists')
        return name
