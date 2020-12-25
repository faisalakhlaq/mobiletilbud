from django.urls import path

from .views import (HomeView, MobileManufacturersView, get_mobile_auto_complete)

app_name = 'core'

urlpatterns = [
      path('mobiles-and-offers', HomeView.as_view(), name='mobiles-and-offers'),
      path('mobile-brands/', MobileManufacturersView.as_view(), 
            name='mobile-brands'),
      path('mobile_search_auto_complete/', get_mobile_auto_complete, 
            name='mobile_search_auto_complete'),
]
