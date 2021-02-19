from django.urls import path

from api.views import (MobileListAPIView, MobileDetailAPIView, TilbudView)

app_name = 'api'

urlpatterns = [
    path('mobilelist/', MobileListAPIView.as_view()),
    path('mobiledetails/<int:id>', MobileDetailAPIView.as_view()),
    path('offerslist/', TilbudView.as_view()),
    path('offerslist/<int:id>', TilbudView.as_view()),
]
