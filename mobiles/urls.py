from django.urls import path

from .views import (MobileDetailView, CompareMobile, fetch_mobiles)

app_name = 'mobiles'

urlpatterns = [
    path('mobile-detail/<slug>', MobileDetailView.as_view(), 
        name='mobile-detail'),
    path('fetch-mobiles', fetch_mobiles, 
        name='fetch-mobiles'),
    path('mobile-comparison/<int:id1><int:id2>', CompareMobile.as_view(),
        name='mobile-comparison')
]
