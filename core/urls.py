from django.urls import path

from .views import HomeView, MobileManufacturersView

app_name = 'core'

urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('mobile-manufacturers', MobileManufacturersView.as_view(), 
          name='mobile-manufacturers'),
]
