from django.urls import path

from .views import MobileDetailView

app_name = 'mobiles'

urlpatterns = [
    path('mobile-detail/<slug>', MobileDetailView.as_view(), 
        name='mobile-detail'),

]
