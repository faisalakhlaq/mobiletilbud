from django import forms
from django.contrib.auth import get_user_model
from .models import PartnerEmployee

class UserForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(UserForm, self).__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['style'] = 'width:20rem'
            field.widget.attrs['required'] = 'required'

    class Meta:
        model = get_user_model()
        fields = ('username', 'first_name', 'last_name', 'email', 'password')
        widgets = {
          'password': forms.PasswordInput()
         }

class CreatePartnerForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(CreatePartnerForm, self).__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['style'] = 'width:20rem'
            field.widget.attrs['required'] = 'required'

    class Meta:
        model = PartnerEmployee
        fields = ['image', 'company']
