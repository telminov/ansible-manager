from django import forms

from core import models


class Search(forms.Form):
    name = forms.CharField(required=False)


class Edit(forms.ModelForm):
    class Meta:
        model = models.HostGroup
        fields = ('name', )

