from django.urls import path

from .views import (PartnersLogin, CreateOfferView, 
PartnersCreateView, PartnersHome, DeleteOfferView, UpdateOfferView)

app_name = 'partners'

urlpatterns = [
    path('create_offer/', CreateOfferView.as_view(), name='create_offer'),
    path('partners_login/', PartnersLogin.as_view(), name='partners_login'),
    path('partners_signup/', PartnersCreateView.as_view(), name='partners_signup'),
    path('partners_home/', PartnersHome.as_view(), name='partners_home'),
    path('<pk>/delete/', DeleteOfferView.as_view(), name='delete_offer'),
    path('<pk>/update/', UpdateOfferView.as_view(), name='update_offer'),
]
