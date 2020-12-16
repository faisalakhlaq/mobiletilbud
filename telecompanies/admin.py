from django.contrib import admin

from .models import Offer
from .forms import OfferForm

class OfferAdmin(admin.ModelAdmin):
    form = OfferForm
    readonly_fields = ['updated']
    list_display = [
        'mobile',
        'telecom_company',
        'mobile_name',
        'discount',
        'price',
        'updated',
    ]
    list_filter = ['telecom_company',]

admin.site.register(Offer, OfferAdmin)
