from django import forms
from django.contrib import admin
from django.contrib.admin.widgets import AutocompleteSelect

from .models import Mobile, Variation, PopularMobile
from django.utils.translation import gettext_lazy as _

class FakeRelation:
    def __init__(self, model):
        self.model = model

class VariationForm(forms.ModelForm):
    mobile = forms.ModelChoiceField(
            queryset=Mobile.objects.all(),
            # widget=AutocompleteSelect(Mobile._meta.get_field('name').remote_field, admin.site)
            widget=AutocompleteSelect(FakeRelation(Mobile), admin.site),
        )
    class Meta:
        model = Variation
        fields = ['name', 'mobile',]

class PopularMobileForm(forms.ModelForm):
    mobile = forms.ModelChoiceField(
            queryset=Mobile.objects.all(),
            widget=AutocompleteSelect(FakeRelation(Mobile), admin.site),
        )
    class Meta:
        model = PopularMobile
        fields = ['mobile']
