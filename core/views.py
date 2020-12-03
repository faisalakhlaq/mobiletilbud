from django.conf import settings
from django.db.models import Q
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render
from django.views import View
from django.views.generic import ListView, View
import json

from .models import TelecomCompany
from mobiles.models import Mobile, MobileBrand
from telecompanies.spider import ThreeSpider, TelenorSpider, TeliaSpider
from telecompanies.models import Offer

# from mobiles.mobile_specs_spider import GsmarenaMobileSpecSpider
# from telecompanies.spider import YouSeeSpider
# from mobiles.tasks import fetch_mobiles_task

class HomeView(View):
    def get(self, *args, **kwargs):
        # fetch_mobiles_task.delay('Motorola')
        # GsmarenaMobileSpecSpider().fetch_mobile_specs('Sony')
        context = {}
        return render(self.request, 'home.html', context)
        # TODO get all the offers and display 10 with the
        # highest Discount value. Need a float discount field Offer.
        # Display 10 most popular mobiles

class MobileManufacturersView(ListView):
    template_name = 'core/mobile_brands.html'
    queryset = MobileBrand.objects.all()

    def get_context_data(self, **kwargs):
        context = super(MobileManufacturersView, self).get_context_data(**kwargs)
        company = self.request.GET.get("mobile_brand")
        query = self.request.GET.get('query')            
        mobile_list = []
        if query and len(query.strip()) > 0:
            mobile_list = Mobile.objects.filter(name__icontains=query.strip())
        if company and company.strip() != 'Popular Mobiles':
            mobile_list = Mobile.objects.filter(brand__name__iexact=company.strip())
        context["mobile_brand"] = company or query
        context["mobile_list"] = mobile_list 
        return context

def get_mobile_auto_complete(request):    
    """Search mobile names containing the user provided string.
    Return 5 matching names."""
    if request.is_ajax():
        query = request.GET.get('term', '')
        mobile_list = Mobile.objects.filter(Q(name__icontains=query.strip()) | 
                                            Q(full_name__icontains=query.strip()))[:5]
        results = []
        for rs in mobile_list:
            mobile_json = {}
            mobile_json = rs.name
            results.append(mobile_json)
        data = json.dumps(results)
    else:
        data = 'fail'
    mimetype = 'application/json'
    return HttpResponse(data, mimetype)

def change_language(request):
    response = HttpResponseRedirect('/')
    if request.method == 'POST':
        language = request.POST.get('language')
        if language:
            if language != settings.LANGUAGE_CODE and [lang for lang in settings.LANGUAGES if lang[0] == language]:
                redirect_path = f'/{language}/'
            elif language == settings.LANGUAGE_CODE:
                redirect_path = '/'
            else:
                return response
            from django.utils import translation
            translation.activate(language)
            response = HttpResponseRedirect(redirect_path)
            response.set_cookie(settings.LANGUAGE_COOKIE_NAME, language)
    return response
