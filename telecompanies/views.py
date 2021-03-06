from django.contrib import messages
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q, Count
from django.shortcuts import render
from django.utils.translation import gettext as _
from django.views.generic import ListView, DetailView, View
from django.http import HttpResponse
from itertools import chain
import json

from mobiles.models import Mobile
from telecompanies.models import Offer, TelecomCompany
from telecompanies.utils import get_popular_offers

class OffersHome(View):
    """View for all mobiles with offers on them."""
    def get(self, *args, **kwargs):
        template_name = 'offer/offers_home.html'
        context = self.get_context_data(**kwargs)
        return render(self.request, template_name, context)

    def get_context_data(self, **kwargs):
        filters = self.request.GET.get('filter')
        query = self.request.GET.get("query")
        all_offers = Offer.objects.all().order_by('updated')
        offer_mobiles = Mobile.objects.filter(offers__isnull=False).order_by('full_name')
        # Create a list of mobiles on offer to display in the baner
        slider_offers = offer_mobiles.distinct()
        context = {}
        if query and len(query.strip()) > 0:
            query = query.strip()
            all_offers = all_offers.filter(Q(mobile_name__icontains=query) |
            Q(mobile__full_name__icontains=query)).order_by('-mobile_name')
            if not all_offers:
                output_msg = _('Sorry no offers found for %(m_name)s.') % {'m_name': query}
                messages.info(self.request, output_msg)
            offer_mobiles = offer_mobiles.filter(Q(name__icontains=query) |
            Q(full_name__icontains=query))
            # create a list of offers where the mobile is null
            context['unknown_offers'] = all_offers.filter(mobile=None)
        elif filters:
            if filters == 'All':
                context['unknown_offers'] = all_offers.filter(mobile=None)
            elif filters == 'Popular':
                offer_mobiles = offer_mobiles.annotate(num_offers=Count('offers')).filter(num_offers__gte=3)
        if not query and not filters:
            filters = 'All'
            context['unknown_offers'] = all_offers.filter(mobile=None)
        offers_dict = {}
        for m in offer_mobiles:
            offers_dict[m] = all_offers.filter(mobile=m)[:3]
        context['offers_dict'] = offers_dict
        context['tele_companies'] = TelecomCompany.objects.values_list('name', flat=True).order_by('name')
        context['filter'] = filters
        context['slider_offers'] = slider_offers
        return context

class TelecomCompaniesView(View):
    """This class is NOT USED anymore"""
    def get(self, *args, **kwargs):
        template_name = 'core/telecom_companies.html'
        context = self.get_context_data(args, kwargs)
        return render(self.request, template_name, context)

    def get_context_data(self, *args, **kwargs):
        company = self.request.GET.get("company")
        offers = Offer.objects.all().order_by('updated')
        # TODO get the set of related mobiles from the MobileBrand table
        if offers and company and company != 'ALL':
            offers = offers.filter(telecom_company__name__iexact=company.strip())  
        page = self.request.GET.get('page', 1)
        paginator = Paginator(offers, 10)
        try:
            offer_list = paginator.page(page)
        except PageNotAnInteger:
            offer_list = paginator.page(1)
        except EmptyPage:
            offer_list = paginator.page(paginator.num_pages)
        context = {
            "paginator": paginator,
            "offers": offer_list,
            "object_list": TelecomCompany.objects.all(),
            "offer_count": offers.count(),
            "slider_offers": Mobile.objects.filter(offers__isnull=False).order_by('name').distinct(),
        }
        return context

class OfferDetailView(DetailView):
    template_name = 'offer/offer_detail.html'
    model = Offer

class PopularOffersView(ListView):
    """ Return top 3 offers from each company.
    """
    model = Offer
    template_name = 'offer/offer_list.html'
    paginate_by = 10

    def get_queryset(self):
        company = self.request.GET.get('company')
        query = self.request.GET.get('query')
        all_offers = Offer.objects.all().order_by('updated')
        if query and len(query.strip()) > 0:
            rs_mobiles = all_offers.filter(Q(mobile_name__icontains=query.strip()) |
            Q(mobile__full_name__icontains=query.strip())).order_by('-mobile_name')
            if not rs_mobiles:
                output_msg = _('Sorry no offers found for %(m_name)s.') % {'m_name': query}
                messages.info(self.request, output_msg)
            return rs_mobiles
        elif company:
            if company == 'Popular':
                return get_popular_offers(offers=all_offers, offers_per_company=3)
            elif company == 'All':
                return all_offers
            else:
                # We want offers from a given company. So filter by company name
                return all_offers.filter(telecom_company__name__iexact=company.strip())         
        return get_popular_offers(offers=all_offers, offers_per_company=3)

    def get_context_data(self, **kwargs):
        context = super(PopularOffersView, self).get_context_data(**kwargs)
        company = self.request.GET.get('company')
        query = self.request.GET.get('query')
        context["tele_companies"] = TelecomCompany.objects.all()
        if not company and not query:
            company = 'Popular'
        context["company"] = company # or query
        context["slider_offers"] = Mobile.objects.filter(offers__isnull=False).distinct().order_by('name')
        return context

class CompareOffersView(View):
    # Not used
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
    """Return 5 mobile names matching the given name.
     Names are searched from the offers table."""
    data = 'fail'
    mimetype = 'application/json'
    if not request.is_ajax():
        return HttpResponse(data, mimetype)
    query = request.GET.get('term', '')
    mobile_list = Offer.objects.values_list('mobile_name', flat=True).filter(
        mobile_name__icontains=query.strip()).distinct()[:5]
    # mobile_list = Offer.objects.select_related('mobile').filter(
    #     Q(mobile__name__icontains=query.strip()) | 
    #     Q(mobile__full_name__icontains=query.strip())).distinct('mobile')[:5]
    # mobile_list = Offer.objects.filter(Q(mobile__name__icontains=query.strip()) | 
    #                                     Q(mobile__full_name__icontains=query.strip()))[:5]
    results = []
    for rs in mobile_list:
        mobile_json = {}
        mobile_json = rs
        # mobile_json = rs.mobile.name
        results.append(mobile_json)
    data = json.dumps(results)
    return HttpResponse(data, mimetype)
