from django.shortcuts import render
from django.views.generic import ListView, DetailView, View
from itertools import chain

from telecompanies.models import Offer, TelecomCompany

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

        all_offers = Offer.objects.all()
        if offer_type and offer_type != 'All':
            return self.get_popular_offers(all_offers)
        elif company:
            return all_offers.filter(telecom_company__name__iexact=company.strip())         
        return all_offers

    def get_context_data(self, **kwargs):
        context = super(PopularOffersView, self).get_context_data(**kwargs)
        context["tele_companies"] = TelecomCompany.objects.all()
        return context
    
    def get_popular_offers(self, all_offers):
        """Returns highest discount offers. 
        5 from each telecomcompany."""
        telenor_best_offer = all_offers.filter(
            telecom_company__name__iexact='Telenor').order_by('-discount_offered')
        if not telenor_best_offer:
            telenor_best_offer = all_offers.filter(telecom_company__name__iexact='Telenor')
        if telenor_best_offer and len(telenor_best_offer) > 5:
            telenor_best_offer = telenor_best_offer[:5]
        three_best_offer = all_offers.filter(
            telecom_company__name__iexact='3').order_by('-discount_offered')
        if not three_best_offer:
            three_best_offer = all_offers.filter(telecom_company__name__iexact='3')
        if three_best_offer and len(three_best_offer) > 5:
            three_best_offer = three_best_offer[:5]
        telia_best_offer = all_offers.filter(
            telecom_company__name__iexact='Telia').order_by('-discount_offered')[:5]
        if not telia_best_offer:
            telia_best_offer = all_offers.filter(telecom_company__name__iexact='Telia')
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
