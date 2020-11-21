from django.shortcuts import render
from django.views.generic import ListView, DetailView, View
from itertools import chain

from .models import Offer

class OfferDetailView(DetailView):
    template_name = 'offer/offer_detail.html'
    model = Offer

class OffersView(ListView):
    template_name = 'offer/offer_list.html'

    def get_queryset(self):
        """ Return top 5 offers from each company.
        """
        telenor_best_offer = Offer.objects.filter(
            telecom_company__name__iexact='Telenor').order_by('-discount_offered')
        if not telenor_best_offer:
            telenor_best_offer = Offer.objects.filter(telecom_company__name__iexact='Telenor')
        if telenor_best_offer and len(telenor_best_offer) > 5:
            telenor_best_offer = telenor_best_offer[:5]
        three_best_offer = Offer.objects.filter(
            telecom_company__name__iexact='3').order_by('-discount_offered')
        if not three_best_offer:
            three_best_offer = Offer.objects.filter(telecom_company__name__iexact='3')
        if three_best_offer and len(three_best_offer) > 5:
            three_best_offer = three_best_offer[:5]

        telia_best_offer = Offer.objects.filter(
            telecom_company__name__iexact='Telia').order_by('-discount_offered')[:5]
        if not telia_best_offer:
            telia_best_offer = Offer.objects.filter(telecom_company__name__iexact='Telia')
        if telia_best_offer and len(telia_best_offer) > 5:
            telia_best_offer = telia_best_offer[:5]
        result_list = list(chain(telenor_best_offer, three_best_offer, telia_best_offer))
        return result_list

class CompareOffersView(View):
    def get(self, *args, **kwargs):
        template_name = 'offer/compare_offers.html'
        context = self.get_context_data()
        return render(self.request, template_name, context)

    def get_context_data(self):
        telenor_offers = Offer.objects.filter(telecom_company__name__iexact='Telenor')
        telia_offers = Offer.objects.filter(telecom_company__name__iexact='Telia')
        three_offers = Offer.objects.filter(telecom_company__name__iexact='3')
        context = {
            'telenor_offers': telenor_offers,
            'telia_offers': telia_offers,
            'three_offers': three_offers,
        } 
        return context
