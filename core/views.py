from django.conf import settings
from django.db.models import Q, F
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render
from django.utils.translation import gettext as _
from django.views import View
from django.views.generic import ListView, View
import json
from urllib.parse import urlparse

from .models import TelecomCompany
from mobiles.models import Mobile, MobileBrand, PopularMobile
from telecompanies.models import Offer
# from telecompanies.tilbud_spider import ThreeSpider, TelenorSpider, TeliaSpider, YouSeeSpider
from telecompanies.utils import get_popular_offers

# from mobiles.mobile_specs_spider import GsmarenaMobileSpecSpider
# from telecompanies.spider import YouSeeSpider
# from mobiles.utils import update_launch_date
# from mobiles.mobile_spider import GsmarenaMobileSpider

class HomeView(View):
    def get(self, *args, **kwargs):
        # update_launch_date('Sony')
        # ThreeSpider().fetch_offers() 
        # TelenorSpider().fetch_offers()
        # TeliaSpider().fetch_offers()
        # YouSeeSpider().fetch_offers()
        # TeliaSpider().fetch_offers()
        # fetch_mobiles_task.delay('Motorola')
        # GsmarenaMobileSpecSpider().fetch_mobile_specs('Huawei')
        # GsmarenaMobileSpider().update_mobile_url(brand_name_='Huawei')
        context = self.get_context_data(*kwargs)
        return render(self.request, 'core/home.html', context)
    
    def get_context_data(self, **kwargs):
        """Returns all the popular mobiles and one offer from 
        each telecompany"""
        popular_mobiles = PopularMobile.objects.all()[:10]
        context = {
            "popular_mobiles": popular_mobiles,
        }
        popular_offers = get_popular_offers(offers_per_company=2)
        context['popular_offers'] = popular_offers
        return context

class MobileManufacturersView(ListView):
    model = Mobile
    template_name = 'core/mobile_brands.html'
    paginate_by = 20

    def get_queryset(self):
        company = self.request.GET.get("brand")
        query = self.request.GET.get('query')            
        if query and len(query.strip()) > 0:
            return Mobile.objects.filter(Q(name__icontains=query.strip()) |
            Q(full_name__icontains=query.strip())).order_by('-name')
        elif company:
            # If popular mobiles is not selected then a brand name is 
            # selected. Therefore, find the mobiles of the selected brand
            if company.strip() != 'Popular':
                # Order by date and send the ones will null value at the end
                # return Mobile.objects.filter(brand__name__iexact=company.strip()).order_by('-launch_date')
                return Mobile.objects.filter(brand__name__iexact=company.strip()).order_by(F('launch_date').desc(nulls_last=True))
            elif company.strip() == 'Popular':
                # get all the ids from popularmobile 
                # table and then fetch the related mobiles
                ids = PopularMobile.objects.values_list('mobile')
                return Mobile.objects.filter(id__in = ids).order_by('-name')
        # If the page is loading without any query 
        # then display the popular mobiles
        if not company and not query:
            ids = PopularMobile.objects.values_list('mobile')
            return Mobile.objects.filter(id__in = ids).order_by('-name')
    
    def get_context_data(self, **kwargs):
        context = super(MobileManufacturersView, self).get_context_data(**kwargs)
        company = self.request.GET.get("brand")
        query = self.request.GET.get('query')            
        if not company and not query:
            query = 'Popular'
        context['mobile_brands'] = MobileBrand.objects.all()
        context["brand"] = company or query
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
                referer_page = urlparse(request.META.get('HTTP_REFERER')).path
                redirect_path = f'/{language}{referer_page}'
            elif language == settings.LANGUAGE_CODE:
                referer_page = urlparse(request.META.get('HTTP_REFERER')).path
                if '/en' in referer_page:
                    referer_page = referer_page.replace('/en', '')
                redirect_path = f'{referer_page}'
            else:
                return response
            from django.utils import translation
            translation.activate(language)
            response = HttpResponseRedirect(redirect_path)
            response.set_cookie(settings.LANGUAGE_COOKIE_NAME, language)
    return response

# Error page handlers
def handler500(request):
        data = {}
        return render(request,'error_pages/500.html', data)

def handler404(request, exception):
        data = {}
        return render(request,'error_pages/404.html', data)

def handler403(request, exception):
        data = {}
        return render(request,'error_pages/403.html', data)

def handler400(request, exception):
        data = {}
        return render(request,'error_pages/400.html', data)
