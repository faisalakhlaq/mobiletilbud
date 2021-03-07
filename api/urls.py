from django.urls import path

from api.views import (MobileListAPIView, MobileDetailAPIView, 
TilbudView, RegisterPartnerEmployeeView, PartnerLoginAPIView, 
CreateTilbudAPI)

app_name = 'api'

urlpatterns = [
    path('mobilelist/', MobileListAPIView.as_view()),
    path('mobiledetails/<int:id>', MobileDetailAPIView.as_view()),
    path('offerslist/', TilbudView.as_view()),
    path('offerslist/<int:id>', TilbudView.as_view()),
    path('partner-signup/', RegisterPartnerEmployeeView.as_view(), name='partner-signup'),
    path('partner-login/', PartnerLoginAPIView.as_view(), name='partner-login'),
    path('create-offer/', CreateTilbudAPI.as_view(), name='create-offer'),
]
