from django.contrib import admin

from .models import Mobile, MobileBrand

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

class MobileBrandAdmin(admin.ModelAdmin):
    fields = ('id', 'name')
    readonly_fields = ('id',)
    
admin.site.register(Mobile, MobileAdmin)
admin.site.register(MobileBrand, MobileBrandAdmin)
