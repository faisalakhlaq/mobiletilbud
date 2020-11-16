from django.urls import path

from .views import HomeView, MobileManufacturersView, TelecomCompaniesView

app_name = 'core'

urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('mobile-manufacturers', MobileManufacturersView.as_view(), 
          name='mobile-manufacturers'),
    path('telecom-companies', TelecomCompaniesView.as_view(), 
          name='telecom-companies'), 
]
