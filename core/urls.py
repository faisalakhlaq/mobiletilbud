from django.urls import path

from .views import (HomeView, MobileManufacturersView, 
                    MobileDetailView, TelecomCompaniesView)

app_name = 'core'

urlpatterns = [
      path('', HomeView.as_view(), name='home'),
      path('mobile-brands', MobileManufacturersView.as_view(), 
            name='mobile-brands'),
      path('telecom-companies', TelecomCompaniesView.as_view(), 
            name='telecom-companies'), 
      path('mobile-detail/<slug>', MobileDetailView.as_view(), 
            name='mobile-detail'),
]
