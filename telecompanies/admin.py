from django.contrib import admin

from .models import Offer

class OfferAdmin(admin.ModelAdmin):
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
