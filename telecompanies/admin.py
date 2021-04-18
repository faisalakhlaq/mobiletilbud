from django.contrib import admin
from django.core import management

from .models import Offer
from .forms import OfferForm
from .management.commands import fetch_tilbud


def run_fetch_tilbud(modeladmin, request, queryset):
    management.call_command(fetch_tilbud.Command())

run_fetch_tilbud.short_description = 'Fetch all Tilbud'

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
    list_editable = ['discount']
    actions = [run_fetch_tilbud]


admin.site.register(Offer, OfferAdmin)
