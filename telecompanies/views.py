from django.db.models import Q
from django.shortcuts import render
from django.views.generic import ListView, DetailView, View
from django.http import HttpResponse
from itertools import chain
import json

from telecompanies.models import Offer, TelecomCompany
from telecompanies.utils import get_popular_offers

class TelecomCompaniesView(View):
    def get(self, *args, **kwargs):
        template_name = 'core/telecom_companies.html'
        context = self.get_context_data(self, args, kwargs)
        return render(self.request, template_name, context)

    def get_context_data(self, *args, **kwargs):
        company = self.request.GET.get("company")
        offers = Offer.objects.all()
        # TODO get the set of related mobiles from the MobileBrand table
        if offers and company and company != 'ALL':
            offers = offers.filter(telecom_company__name__iexact=company.strip())         
        context = {
            "offers": offers,
            "object_list": TelecomCompany.objects.all(),
            "offer_count": offers.count()
        }
        return context

class OfferDetailView(DetailView):
    template_name = 'offer/offer_detail.html'
    model = Offer

class PopularOffersView(ListView):
    """ Return top 5 offers from each company.
    """
    template_name = 'offer/offer_list.html'

    def get_queryset(self):
        offer_type = self.request.GET.get('offer')
        company = self.request.GET.get('company')
        query = self.request.GET.get('query')
        all_offers = Offer.objects.all()
        if query and len(query.strip()) > 0:
            return all_offers.filter(mobile__name__icontains=query.strip())
        elif offer_type and offer_type == 'Popular':
            return self.get_popular_offers(offers=all_offers, offers_per_company=5)
        elif company:
            return all_offers.filter(telecom_company__name__iexact=company.strip())         
        return all_offers

    def get_context_data(self, **kwargs):
        context = super(PopularOffersView, self).get_context_data(**kwargs)
        context["tele_companies"] = TelecomCompany.objects.all()
        return context

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

def get_tilbud_auto_complete(request):    
    """Search tilbud containing mobile names.
    Return 5 matching names."""
    data = 'fail'
    mimetype = 'application/json'
    if not request.is_ajax():
        return HttpResponse(data, mimetype)
    query = request.GET.get('term', '')
    mobile_list = Offer.objects.select_related('mobile').filter(
        Q(mobile__name__icontains=query.strip()) | 
        Q(mobile__full_name__icontains=query.strip())).distinct('mobile')[:5]
    # mobile_list = Offer.objects.filter(Q(mobile__name__icontains=query.strip()) | 
    #                                     Q(mobile__full_name__icontains=query.strip()))[:5]
    results = []
    for rs in mobile_list:
        mobile_json = {}
        mobile_json = rs
        mobile_json = rs.mobile.name
        results.append(mobile_json)
    data = json.dumps(results)
    return HttpResponse(data, mimetype)
