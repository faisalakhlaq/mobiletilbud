from django.urls import path

from .views import OffersView, OfferDetailView, CompareOffersView

app_name = 'telecompanies'

urlpatterns = [
    path('offers/', OffersView.as_view(), name='offers'),
    path('compare-offers/', CompareOffersView.as_view(), name='compare-offers'),
    path('offer-detail/<slug>', OfferDetailView.as_view(), name='offer-detail'),   
]
