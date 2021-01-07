from django.urls import path

from .views import (PopularOffersView, OfferDetailView,
 get_tilbud_auto_complete, OffersHome)

app_name = 'telecompanies'

urlpatterns = [
    path('', OffersHome.as_view(), name='home'), 
    path('offers/', PopularOffersView.as_view(), name='offers'),
    path('offer-detail/<slug>', OfferDetailView.as_view(), 
    name='offer-detail'),
    path('tilbud_search_auto_complete/', get_tilbud_auto_complete, 
    name='tilbud_search_auto_complete'),    
]
