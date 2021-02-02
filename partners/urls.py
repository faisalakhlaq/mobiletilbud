from django.urls import path

from .views import PartnersLogin

app_name = 'partners'

urlpatterns = [
    path('partners_login/', PartnersLogin.as_view(), name='partners_login'),
]
