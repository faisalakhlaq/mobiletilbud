from django.contrib import admin

from .models import Offer

class OfferAdmin(admin.ModelAdmin):
    list_display = [
        'mobile',
        'telecom_company',
        'mobile_name',
        'discount',
        'price',
    ]
    list_filter = ['telecom_company',]

admin.site.register(Offer, OfferAdmin)