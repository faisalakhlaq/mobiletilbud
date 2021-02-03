from django import forms
from django.contrib.auth import get_user_model
from .models import PartnerEmployee

# from telecompanies.models import Offer

class UserForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(UserForm, self).__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['style'] = 'width:20rem'

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
    
    birth_date = forms.DateField(required=False,
    widget=forms.TextInput(     
        attrs={'type': 'date'} 
        )
    )    
    class Meta:
        model = PartnerEmployee
        fields = ['birth_date', 'image', 'company']

# class CreateOfferForm(forms.ModelForm):
#     class Meta:
#         model = Offer
#         fields = '__all__'
#         exclude = 'slug'
