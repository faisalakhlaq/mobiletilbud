from django.urls import path

from .views import (MobileDetailView, MobileComparison)

app_name = 'mobiles'

urlpatterns = [
    path('<slug:slug>', MobileDetailView.as_view(), 
        name='mobile-detail'),
    path('mobile-comparison/', MobileComparison.as_view(),
        name='mobile-comparison'),
]
