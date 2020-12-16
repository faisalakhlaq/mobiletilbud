from django import forms
from django.contrib import admin
from django.contrib.admin.widgets import AutocompleteSelect

from .models import Offer
from mobiles.models import Mobile

class FakeRelation:
    def __init__(self, model):
        self.model = model

class OfferForm(forms.ModelForm):
    mobile = forms.ModelChoiceField(
            queryset=Mobile.objects.all(),
            # widget=AutocompleteSelect(Mobile._meta.get_field('name').remote_field, admin.site)
            widget=AutocompleteSelect(FakeRelation(Mobile), admin.site),
        )
    class Meta:
        model = Offer
        fields = ['mobile', 'telecom_company', 'mobile_name', 'discount', 'discount_offered', 'offer_url', 'price', 'slug']
