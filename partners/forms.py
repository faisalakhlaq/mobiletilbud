from django import forms
from django.contrib.auth import get_user_model

# from telecompanies.models import Offer

class UserForm(forms.ModelForm):
    class Meta:
        model = get_user_model()
        fields = ('username', 'first_name', 'last_name', 'email', 'password')
        widgets = {
          'password': forms.PasswordInput()
         }

# class CreateOfferForm(forms.ModelForm):
#     class Meta:
#         model = Offer
#         fields = '__all__'
#         exclude = 'slug'
