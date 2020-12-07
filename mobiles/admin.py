from django.contrib import admin

from .forms import VariationForm, PopularMobileForm
from .models import (Mobile, MobileBrand, MobileTechnicalSpecification, 
Variation, MobileVariation, MobileCameraSpecification, PopularMobile)

class InLineMobileSpecs(admin.StackedInline):
    model = MobileTechnicalSpecification
    extra = 1

class InLineMobileVariationSpecs(admin.StackedInline):
    model = MobileVariation
    extra = 1

class InLineMobileCameraSpecs(admin.StackedInline):
    model = MobileCameraSpecification
    extra = 1

class MobileAdmin(admin.ModelAdmin):
    inlines = [InLineMobileSpecs, InLineMobileCameraSpecs]
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
    list_editable = ['cash_price']

class CameraAdmin(admin.ModelAdmin):
    list_display = [
        'rear_cam_megapixel',
        'front_cam_megapixel',
    ]
    
class MobileBrandAdmin(admin.ModelAdmin):
    fields = ('name', 'image')
    # readonly_fields = ('id',)

# TODO 
class VariationAdmin(admin.ModelAdmin):
    form = VariationForm
    inlines = [InLineMobileVariationSpecs]
    list_display = ['name', 'mobile']
    # list_filter = ['mobile_brand']

class MobileVariationAdmin(admin.ModelAdmin):
    list_display = ['variation', 'value', 'mobile_name']
    list_editable = ['value']

    def mobile_name(self, obj):
        return obj.variation.mobile

class PopularMobileAdmin(admin.ModelAdmin):
    form = PopularMobileForm
    list_display = ['mobile', 'created']

admin.site.register(Mobile, MobileAdmin)
admin.site.register(MobileBrand, MobileBrandAdmin)
admin.site.register(MobileTechnicalSpecification)
admin.site.register(Variation, VariationAdmin)
admin.site.register(MobileVariation, MobileVariationAdmin)
admin.site.register(MobileCameraSpecification, CameraAdmin)
admin.site.register(PopularMobile, PopularMobileAdmin)
