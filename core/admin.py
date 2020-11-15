from django.contrib import admin

from .models import (Mobile, MobileBrand, MobileCameraSpecification, 
                     MobilePrice, MobileTechnicalSpecification, 
                     MobileVariation, Variation, TelecomCompany, Package)

admin.site.register(Mobile)
admin.site.register(MobileBrand)
admin.site.register(MobileCameraSpecification)
admin.site.register(MobilePrice)
admin.site.register(MobileTechnicalSpecification)
admin.site.register(MobileVariation)
admin.site.register(Variation)
admin.site.register(TelecomCompany)
admin.site.register(Package)