from django.contrib import admin

from .models import (Country, TelecomCompany)

admin.site.site_header = 'MobileTilbud'
admin.site.register(TelecomCompany)
admin.site.register(Country)