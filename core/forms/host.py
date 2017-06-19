from django import forms
from django.db.models.functions import Lower

from core import models


class Search(forms.Form):
    name = forms.CharField(required=False)
    address = forms.CharField(required=False)
    group = forms.ModelChoiceField(queryset=models.HostGroup.objects.order_by(Lower('name')), required=False,
                                   widget=forms.Select(attrs={'class': 'need-select2'}))


class Edit(forms.ModelForm):
    groups = forms.ModelMultipleChoiceField(required=False, queryset=models.HostGroup.objects.order_by(Lower('name')),
                                            widget=forms.SelectMultiple(attrs={'class': 'need-select2'}))

    class Meta:
        model = models.Host
        fields = ('name', 'address', 'groups')
