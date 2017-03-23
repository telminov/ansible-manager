from django import forms

from core import models


class Search(forms.Form):
    name = forms.CharField(required=False)
    address = forms.GenericIPAddressField(required=False)
    group = forms.ModelChoiceField(queryset=models.HostGroup.objects.all(), required=False,
                                   widget=forms.Select(attrs={'class': 'need-select2'}))


class Edit(forms.ModelForm):
    groups = forms.ModelMultipleChoiceField(required=False, queryset=models.HostGroup.objects.all(),
                                            widget=forms.SelectMultiple(attrs={'class': 'need-select2'}))

    class Meta:
        model = models.Host
        fields = ('name', 'address', 'groups')
