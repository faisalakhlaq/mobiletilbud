from django.conf import settings
from django.db.models import Q
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.views import View
from django.views.generic import ListView, View

from .models import TelecomCompany
from mobiles.models import Mobile, MobileBrand
from telecompanies.spider import ThreeSpider, TelenorSpider, TeliaSpider
from telecompanies.models import Offer

from mobiles.mobile_specs_spider import GsmarenaMobileSpecSpider
# from telecompanies.spider import YouSeeSpider

class HomeView(View):
    def get(self, *args, **kwargs):
        context = {}
        GsmarenaMobileSpecSpider().fetch_mobile_specs('Motorola')
        return render(self.request, 'home.html', context)
        # TODO get all the offers and display 10 with the
        # highest Discount value. Need a float discount field Offer

class MobileManufacturersView(ListView):
    template_name = 'core/mobile_brands.html'
    queryset = MobileBrand.objects.all()

    def get_context_data(self, **kwargs):
        context = super(MobileManufacturersView, self).get_context_data(**kwargs)
        company = self.request.GET.get("mobile_brand")
        mobile_list = []
        if company and company.strip() != 'ALL':
            mobile_list = Mobile.objects.filter(brand__name__iexact=company.strip())
        context["mobile_brand"] = company 
        context["mobile_list"] = mobile_list 
        return context

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
