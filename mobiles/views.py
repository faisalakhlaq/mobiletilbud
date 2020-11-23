from django.shortcuts import render
from django.views.generic import View
from django.db.models import Q

from telecompanies.models import Offer
from .models import Mobile

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
