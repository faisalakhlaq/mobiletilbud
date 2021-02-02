from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from django.views.generic import View
from django.views.generic.edit import CreateView

from telecompanies.models import Offer

class PartnersLogin(View):
    def get(self, *args, **kwargs):
        return render(self.request, 'partners/login.html', {})


class CreateOfferView(LoginRequiredMixin, CreateView):
    model = Offer
    fields = [
        'mobile',
        'telecom_company',
        'mobile_name',
        'discount',
        'discount_offered',
        'offer_url',
        'price',
    ]
    template_name = 'partners/create_offer.html'
