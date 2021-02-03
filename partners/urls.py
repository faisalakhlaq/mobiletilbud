from django.urls import path

from .views import PartnersLogin, CreateOfferView, PartnersCreateView

app_name = 'partners'

urlpatterns = [
    path('create_offer/', CreateOfferView.as_view(), name='create_offer'),
    path('partners_login/', PartnersLogin.as_view(), name='partners_login'),
    path('partners_signup/', PartnersCreateView.as_view(), name='partners_signup'),
]
