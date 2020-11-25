from django.contrib import admin

from .models import (Mobile, MobileBrand, MobileTechnicalSpecification, 
Variation, MobileVariation, MobileCameraSpecification)

class MobileAdmin(admin.ModelAdmin):
    list_display = [
        'name',
        'full_name',
        'cash_price',
        'url',
    ]    
    list_filter = [
        'brand',
    ]
    search_fields = ['name','full_name']

class CameraAdmin(admin.ModelAdmin):
    list_display = [
        'rear_cam_megapixel',
        'front_cam_megapixel',
    ]
class MobileBrandAdmin(admin.ModelAdmin):
    fields = ('id', 'name')
    readonly_fields = ('id',)
    
admin.site.register(Mobile, MobileAdmin)
admin.site.register(MobileBrand, MobileBrandAdmin)
admin.site.register(MobileTechnicalSpecification)
admin.site.register(Variation)
admin.site.register(MobileVariation)
admin.site.register(MobileCameraSpecification, CameraAdmin)
