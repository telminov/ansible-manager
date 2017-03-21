from django import forms
from django.conf import settings

from core import consts
from core import models


class Search(forms.Form):
    STATUS_CHOICES = [("", "---------")] + list(consts.STATUS_CHOICES)
    template = forms.ModelChoiceField(queryset=models.TaskTemplate.objects.all(), required=False,
                                      widget=forms.Select(attrs={'class': 'need-select2'}))
    playbook = forms.FilePathField(path=settings.ANSIBLE_PLAYBOOKS_PATH, required=False,
                                   widget=forms.Select(attrs={'class': 'need-select2'}))
    status = forms.ChoiceField(choices=STATUS_CHOICES, required=False,
                               widget=forms.Select(attrs={'class': 'need-select2'}))




