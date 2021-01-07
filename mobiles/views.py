from django.contrib import messages
from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.utils.translation import gettext as _
from django.views.generic import View
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

class MobileComparison(View):
    """Gets the two mobile ids to be compared from the request.
    Redirects to the mobile comparison page."""
    def get(self, *args, **kwargs):
        try:
            id1 = self.request.GET.get('id1')
            id2 = self.request.GET.get('id2')
            if not id1 or not id2 or id1 == id2:
                messages.info(self.request, _('Please try choosing two different mobiles'))
                return redirect(self.request.META.get('HTTP_REFERER'))
            mobile1 = Mobile.objects.get(slug=id1)
            mobile2 = Mobile.objects.get(slug=id2)
            context = self.get_context_data(mobile1=mobile1, mobile2=mobile2)
            return render(self.request, 'mobile/mobile_comparison.html', context)
        except Mobile.DoesNotExist:
            messages.info(self.request, _('Please try choosing two different mobiles'))
            # TODO LOGGING
            print('Unable to find mobile for comparison')
            return redirect(self.request.META.get('HTTP_REFERER'))

    def get_context_data(self, mobile1, mobile2):
        offers = Offer.objects.filter(Q(mobile=mobile1) | 
                                      Q(mobile__name__iexact=mobile1.name))
        # specs = MobileTechnicalSpecification.objects.filter(mobile=mobile)
        offers2 = Offer.objects.filter(Q(mobile=mobile2) | 
                                Q(mobile__name__iexact=mobile2.name))

        specs = mobile1.technical_specs.all()
        if specs: specs = specs[0]
        specs2 = mobile2.technical_specs.all()
        if specs2: specs2 = specs2[0]
        variation = Variation.objects.filter(mobile=mobile1)
        variation2 = Variation.objects.filter(mobile=mobile2)
        # TODO get the variation values from MobileVariation
        cam = mobile1.camera_specs.all()
        if cam: cam = cam[0]
        cam2 = mobile2.camera_specs.all()
        if cam2: cam2 = cam2[0]
        colours = MobileVariation.objects.filter(variation__mobile=mobile1,
                                            variation__name='colour')
        colours2 = MobileVariation.objects.filter(variation__mobile=mobile2,
                                            variation__name='colour')
        memory = MobileVariation.objects.filter(variation__mobile=mobile1, 
                                            variation__name='memory')
        memory2 = MobileVariation.objects.filter(variation__mobile=mobile2, 
                                            variation__name='memory')
        context = {
                'mobile': mobile1,
                'offers': offers,
                'tech_specs': specs,
                'camera_specs': cam,
                'colours': colours,
                'memory': memory,

                'mobile2': mobile2,
                'offers2': offers2,
                'tech_specs2': specs2,
                'camera_specs2': cam2,
                'colours2': colours2,
                'memory2': memory2,
            }
        return context
