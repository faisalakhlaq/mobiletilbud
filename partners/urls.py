from django.urls import path

from .views import PartnersLogin, CreateOfferView

app_name = 'partners'

urlpatterns = [
    path('create_offer/', CreateOfferView.as_view(), name='create_offer'),
    path('partners_login/', PartnersLogin.as_view(), name='partners_login'),
]
