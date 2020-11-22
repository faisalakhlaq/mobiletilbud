from django.conf import settings
from django.db.models import Q
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.views import View
from django.views.generic import ListView, View


from .models import MobileBrand, TelecomCompany, Mobile
from telecompanies.spider import ThreeSpider, TelenorSpider, TeliaSpider
from telecompanies.models import Offer

# from mobiles.utils import bulk_copy_brand_data

class HomeView(View):
    def get(self, *args, **kwargs):
        context = {}
        # bulk_copy_brand_data()
        # HuawaiMobileSpider().fetch_mobiles()
        return render(self.request, 'home.html', context)
        # TODO get all the offers and display 10 with the 
        # highest Discount value. Need a float discount field Offer

class MobileDetailView(View):
    def get(self, *args, **kwargs):
        """Return the mobile details and offers on 
        this mobile from different companies"""
        template_name = 'mobile/mobile_detail.html'
        try:
            context = self.get_context_data()
            return render(self.request, template_name, context)
        except Mobile.DoesNotExist:
            # TODO give a message about mobile not found
            raise Http404("No MyModel matches the given query.")
    
    def get_context_data(self, **kwargs):
        # import pdb; pdb.set_trace()
        slug = self.kwargs["slug"]   
        mobile = Mobile.objects.get(slug=slug)
        offers = Offer.objects.filter(Q(mobile=mobile) | 
                                      Q(mobile__name__iexact=mobile.name))
        context = {
                'mobile': mobile,
                'offers': offers,
            }
        return context
    

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

class TelecomCompaniesView(View):
    def get(self, *args, **kwargs):
        template_name = 'core/telecom_companies.html'
        context = self.get_context_data(self, args, kwargs)
        return render(self.request, template_name, context)

    def get_context_data(self, *args, **kwargs):
        company = self.request.GET.get("company")
        offers = Offer.objects.all()
        # TODO get the set of related mobiles from the MobileBrand table
        if company and company.strip() and company != 'ALL':
            offers = Offer.objects.filter(telecom_company__name__iexact=company.strip())         
        context = {
            "offers": offers,
            "object_list": TelecomCompany.objects.all(),
            "offer_count": offers.count()
        }
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