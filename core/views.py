from django.conf import settings
from django.contrib import messages
from django.db.models import Q, F
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render
from django.utils import translation
from django.utils.translation import gettext as _
from django.views import View
from django.views.generic import ListView, View
import json
from urllib.parse import urlparse

from mobiles.models import Mobile, MobileBrand, PopularMobile
from telecompanies.utils import get_popular_offers

class HomeView(View):
    def get(self, *args, **kwargs):
        context = self.get_context_data(*kwargs)
        return render(self.request, 'core/home.html', context)

    def get_context_data(self, **kwargs):
        """Returns all the popular mobiles and two offers from 
        each telecompany"""
        popular_mobiles = PopularMobile.objects.all().order_by(F('mobile__launch_date').desc(nulls_last=True))[:15]
        context = {
            "popular_mobiles": popular_mobiles,
        }
        popular_offers = get_popular_offers(offers_per_company=2)
        context['popular_offers'] = popular_offers
        context["slider_offers"] = Mobile.objects.filter(offers__isnull=False).distinct().order_by('name')
        return context

class MobileManufacturersView(ListView):
    model = Mobile
    template_name = 'core/mobile_brands.html'
    paginate_by = 20

    def get_queryset(self):
        company = self.request.GET.get("brand")
        query = self.request.GET.get('query')            
        if query and len(query.strip()) > 0:
            rs_mobiles = Mobile.objects.filter(Q(name__icontains=query.strip()) |
            Q(full_name__icontains=query.strip())).order_by(F('launch_date').desc(nulls_last=True))
            if not rs_mobiles:
                output_msg = _('Sorry no mobile found with name %(m_name)s.') % {'m_name': query}
                messages.info(self.request, output_msg)
            return rs_mobiles
        elif company:
            # If popular mobiles is not selected then a brand name is 
            # selected. Therefore, find the mobiles of the selected brand
            if company.strip() != 'Popular':
                # Order by date and send the ones with null value at the end
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
            return Mobile.objects.filter(id__in = ids).order_by(F('launch_date').desc(nulls_last=True))
    
    def get_context_data(self, **kwargs):
        context = super(MobileManufacturersView, self).get_context_data(**kwargs)
        company = self.request.GET.get("brand")
        query = self.request.GET.get('query')            
        context['mobile_brands'] = MobileBrand.objects.all()
        context["brand"] = company #or query
        context["slider_offers"] = Mobile.objects.filter(offers__isnull=False).distinct().order_by('name')
        if not company and not query:
            context["brand"] = 'Popular'
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
    """When the user selects another language from the language drop down,
    this method sets the new language for the website."""
    response = HttpResponseRedirect('/')
    if request.method == 'POST':
        language = request.POST.get('language')
        if language:
            if language != settings.LANGUAGE_CODE and [lang for lang in settings.LANGUAGES if lang[0] == language]:
                # view, args, kwargs = resolve(urlparse(request.META.get('HTTP_REFERER', '/'))[2])
                parse_result = urlparse(request.META.get('HTTP_REFERER', '/'))
                path = parse_result.path
                params = parse_result.params
                query = parse_result.query
                redirect_path = f'/{language}{path}{params}'
                if query:
                    redirect_path += "?" + query
            elif language == settings.LANGUAGE_CODE:
                # view, args, kwargs = resolve(urlparse(request.META.get('HTTP_REFERER', '/'))[2])
                parse_result = urlparse(request.META.get('HTTP_REFERER', '/'))
                path = parse_result.path
                params = parse_result.params
                query = parse_result.query
                if '/en' in path:
                    path = path.replace('/en', '')
                # redirect_path = f'{path}{params}?{query}'
                redirect_path = f'{path}{params}'
                if query:
                    redirect_path += "?" + query
            else:
                return response
            translation.activate(language)
            response = HttpResponseRedirect(redirect_path)
            # TODO setting language can be further improvement
            #  using the below method (setting the view)
            # try:
            #     view(request, *args, **kwargs)
            # except Http404:
            #     return HttpResponseRedirect('/')
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
