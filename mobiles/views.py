from django.shortcuts import render
from django.views.generic import View
from django.db.models import Q

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
            raise Http404("No MyModel matches the given query.")
    
    def get_context_data(self, **kwargs):
        # import pdb; pdb.set_trace()
        slug = self.kwargs["slug"]   
        mobile = Mobile.objects.get(slug=slug)        
        offers = Offer.objects.filter(Q(mobile=mobile) | 
                                      Q(mobile__name__iexact=mobile.name))
        # specs = MobileTechnicalSpecification.objects.filter(mobile=mobile)
        specs = mobile.technical_specs.all()
        variation = Variation.objects.filter(mobile=mobile)
        # TODO get the variation values from MobileVariation
        if specs: specs = specs[0]
        cam = mobile.camera_specs.all()
        if cam: cam = cam[0]
        context = {
                'mobile': mobile,
                'offers': offers,
                'tech_specs': specs,
                'camera': cam,
            }
        return context
