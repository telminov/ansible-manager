from django import forms
from django.conf import settings

from core import consts
from core import models


class Search(forms.Form):
    STATUS_CHOICES = [("", "---------")] + list(consts.STATUS_CHOICES)
    template = forms.ModelChoiceField(queryset=models.TaskTemplate.objects.all(), required=False,
                                      widget=forms.Select(attrs={'class': 'need-select2'}))
    playbook = forms.FilePathField(path=settings.ANSIBLE_PLAYBOOKS_PATH, match='.*\.yml$', required=False,
                                   widget=forms.Select(attrs={'class': 'need-select2'}))
    status = forms.ChoiceField(choices=STATUS_CHOICES, required=False,
                               widget=forms.Select(attrs={'class': 'need-select2'}))


class Create(forms.ModelForm):
    template = forms.ModelChoiceField(queryset=models.TaskTemplate.objects.all(), required=False,
                                      widget=forms.Select(attrs={'class': 'need-select2'}))
    hosts = forms.ModelMultipleChoiceField(queryset=models.Host.objects.all(), required=False,
                                           widget=forms.SelectMultiple(attrs={'class': 'need-select2'}))
    host_groups = forms.ModelMultipleChoiceField(queryset=models.HostGroup.objects.all(), required=False,
                                                 widget=forms.SelectMultiple(attrs={'class': 'need-select2'}))
    playbook = forms.FilePathField(path=settings.ANSIBLE_PLAYBOOKS_PATH, match='.*\.yml$',
                                   widget=forms.Select(attrs={'class': 'need-select2'}))

    class Meta:
        model = models.Task
        fields = ('template', 'hosts', 'playbook', 'host_groups')

