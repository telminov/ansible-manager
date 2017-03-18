from django import forms

from core import models


class Search(forms.Form):
    name = forms.CharField(label='Name', required=False)
    address = forms.GenericIPAddressField(label='IP address', required=False)
    group = forms.ModelChoiceField(label='Group', queryset=models.HostGroup.objects.all(), required=False,
                                   widget=forms.Select(attrs={'class': 'need-select2'}))


class Edit(forms.ModelForm):
    class Meta:
        model = models.Host
        fields = '__all__'
        widgets = {
            'groups': forms.SelectMultiple(attrs={'class': 'need-select2'})
        }
