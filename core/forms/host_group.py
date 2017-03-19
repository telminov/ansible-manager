from django import forms

from core import models


class Search(forms.Form):
    name = forms.CharField(label='Name', required=False)


class Edit(forms.ModelForm):
    class Meta:
        model = models.HostGroup
        fields = ('name', )

