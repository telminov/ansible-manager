from django import forms
from django.db.models.functions import Lower

from core import models


class Search(forms.Form):
    name = forms.CharField(required=False)


class Edit(forms.ModelForm):
    hosts = forms.ModelMultipleChoiceField(widget=forms.SelectMultiple(attrs={'class': 'need-select2'}),
                                           queryset=models.Host.objects.order_by(Lower('name')), required=False)

    class Meta:
        model = models.HostGroup
        fields = ('name', 'hosts')
