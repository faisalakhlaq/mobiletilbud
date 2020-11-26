from django.urls import path

from .views import (PopularOffersView, OfferDetailView, CompareOffersView, 
TelecomCompaniesView)

app_name = 'telecompanies'

urlpatterns = [
    path('telecom-companies', TelecomCompaniesView.as_view(), 
    name='telecom-companies'), 
    path('offers/', PopularOffersView.as_view(), name='offers'),
    path('compare-offers/', CompareOffersView.as_view(), 
    name='compare-offers'),
    path('offer-detail/<slug>', OfferDetailView.as_view(), 
    name='offer-detail'),   
]
