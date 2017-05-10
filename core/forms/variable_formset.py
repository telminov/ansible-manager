from django.forms.models import BaseModelFormSet


class ModelFormSetForVariable(BaseModelFormSet):
    def add_fields(self, form, index):
        super(ModelFormSetForVariable, self).add_fields(form, index)
        form.fields['cipher'].label = 'Encrypt'
