from django.shortcuts import render
from django.views.generic import ListView

from .models import Offer

class OffersView(ListView):
    template_name = 'offer/offer_list.html'
    model = Offer
    