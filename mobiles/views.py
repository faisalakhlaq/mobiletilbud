from django.shortcuts import render, redirect
from django.views.generic import View
from django.db.models import Q
from django.http import HttpResponse
import json

from telecompanies.models import Offer
from .models import (Mobile, MobileTechnicalSpecification, 
MobileCameraSpecification, MobileVariation, Variation)

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
            return redirect(self.request.META.get('HTTP_REFERER'))
            # raise Http404("No mobile matches the given query.")
    
    def get_context_data(self, **kwargs):
        # import pdb; pdb.set_trace()
        slug = self.kwargs["slug"]
        mobile = Mobile.objects.get(slug=slug) or None
        offers = Offer.objects.filter(Q(mobile=mobile) | 
                                      Q(mobile__name__iexact=mobile.name))
        # specs = MobileTechnicalSpecification.objects.filter(mobile=mobile)
        specs = mobile.technical_specs.all()
        variation = Variation.objects.filter(mobile=mobile)
        # TODO get the variation values from MobileVariation
        if specs: specs = specs[0]
        cam = mobile.camera_specs.all()
        if cam: cam = cam[0]
        colours = MobileVariation.objects.filter(variation__mobile=mobile,
                                            variation__name='colour')
        memory = MobileVariation.objects.filter(variation__mobile=mobile, 
                                            variation__name='memory')
        context = {
                'mobile': mobile,
                'offers': offers,
                'tech_specs': specs,
                'camera_specs': cam,
                'colours': colours,
                'memory': memory,
            }
        return context

class CompareMobile(View):
    """Gets the two mobile ids to be compared from the request.
    Redirects to the mobile comparison page."""
    def get(self, *args, **kwargs):
        # try:
        # if self.request.is_ajax():
        # import pdb; pdb.set_trace()
        mobile1_id = kwargs.get('id1')
        mobile2_id = kwargs.get('id2')
        mobile1 = Mobile.objects.get(id=mobile1_id)
        mobile2 = Mobile.objects.get(id=mobile2_id)
        context = self.get_context_data(mobile1)
        return render(self.request, 'offer/compare_mobiles.html', context)
        # except Mobile.DoesNotExist:
            # TODO display a message that couldn't find mobile
            # print('Something went wrong! Mobile not found')
            # return redirect(self.request.META.get('HTTP_REFERER'))
            
    def get_context_data(self, mobile):
        offers = Offer.objects.filter(Q(mobile=mobile) | 
                                      Q(mobile__name__iexact=mobile.name))
        # specs = MobileTechnicalSpecification.objects.filter(mobile=mobile)
        specs = mobile.technical_specs.all()
        variation = Variation.objects.filter(mobile=mobile)
        # TODO get the variation values from MobileVariation
        if specs: specs = specs[0]
        cam = mobile.camera_specs.all()
        if cam: cam = cam[0]
        colours = MobileVariation.objects.filter(variation__mobile=mobile,
                                            variation__name='colour')
        memory = MobileVariation.objects.filter(variation__mobile=mobile, 
                                            variation__name='memory')
        context = {
                'mobile': mobile,
                'offers': offers,
                'tech_specs': specs,
                'camera_specs': cam,
                'colours': colours,
                'memory': memory,
            }
        return context

def fetch_mobiles(request):
    """Find the two mobiles to be compared using the ids from the request."""
    if request.is_ajax():
        mobile1_id = request.GET.get('mobile1_id')
        mobile2_id = request.GET.get('mobile2_id')
        mobile1 = Mobile.objects.get(id=mobile1_id)
        mobile2 = Mobile.objects.get(id=mobile2_id)
        print(mobile1)
        print(mobile2)
        # data = json.dumps([mobile1, mobile2])
        return HttpResponse(mobile1, 'application/json')
