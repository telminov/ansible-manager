from django import forms
from django.conf import settings
from django.db.models.functions import Lower

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

    def __init__(self, *args, **kwargs):
        super(Search, self).__init__(*args, **kwargs)
        self.fields['playbook'] = forms.FilePathField(path=settings.ANSIBLE_PLAYBOOKS_PATH, match='.*\.yml$',
                                                      required=False, widget=forms.Select(attrs={'class': 'need-select2'}))


class Create(forms.ModelForm):
    template = forms.ModelChoiceField(queryset=models.TaskTemplate.objects.all(), required=False,
                                      widget=forms.Select(attrs={'class': 'need-select2'}))
    hosts = forms.ModelMultipleChoiceField(queryset=models.Host.objects.order_by(Lower('name')), required=False,
                                           widget=forms.SelectMultiple(attrs={'class': 'need-select2'}))
    host_groups = forms.ModelMultipleChoiceField(queryset=models.HostGroup.objects.order_by(Lower('name')),
                                                 required=False,
                                                 widget=forms.SelectMultiple(attrs={'class': 'need-select2'}))
    playbook = forms.FilePathField(path=settings.ANSIBLE_PLAYBOOKS_PATH, match='.*\.yml$',
                                   widget=forms.Select(attrs={'class': 'need-select2'}))

    verbose = forms.ChoiceField(choices=consts.VERBOSE_CHOICES)

    ansible_user = forms.ModelChoiceField(queryset=models.AnsibleUser.objects.all(),
                                          widget=forms.Select(attrs={'class': 'need-select2'}))

    class Meta:
        model = models.Task
        fields = ('template', 'hosts', 'playbook', 'host_groups', 'ansible_user', 'verbose')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['ansible_user'].initial = models.AnsibleUser.objects.first()
        self.fields['playbook'] = forms.FilePathField(path=settings.ANSIBLE_PLAYBOOKS_PATH, match='.*\.yml$',
                                                      widget=forms.Select(attrs={'class': 'need-select2'}))
