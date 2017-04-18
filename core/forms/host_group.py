from django import forms

from core import models


class Search(forms.Form):
    name = forms.CharField(required=False)


class Edit(forms.ModelForm):
    name = forms.CharField()

    hosts = forms.ModelMultipleChoiceField(widget=forms.SelectMultiple(attrs={'class': 'need-select2'}),
                                           queryset=models.Host.objects.all(), required=False)


    class Meta:
        model = models.HostGroup
        fields = ('name', 'hosts')

