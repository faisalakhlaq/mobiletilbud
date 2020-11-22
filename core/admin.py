from django.contrib import admin

from .models import (Mobile, MobileBrand, Country, TelecomCompany)
#  MobileCameraSpecification, 
#                      MobilePrice, MobileTechnicalSpecification, Country,
#                      MobileVariation, Variation, TelecomCompany, Package)

class MobileAdmin(admin.ModelAdmin):
    list_display = [
        'name',
        'full_name',
        'brand',
        'cash_price',
    ]    
    list_filter = [
        'brand',
    ]
    search_fields = ['name','full_name']
    
admin.site.register(Mobile, MobileAdmin)
admin.site.register(MobileBrand)
# admin.site.register(MobileCameraSpecification)
# admin.site.register(MobilePrice)
# admin.site.register(MobileTechnicalSpecification)
# admin.site.register(MobileVariation)
# admin.site.register(Variation)
admin.site.register(TelecomCompany)
# admin.site.register(Package)
admin.site.register(Country)