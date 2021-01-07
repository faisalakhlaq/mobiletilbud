from django.contrib.sitemaps import Sitemap
from django.shortcuts import reverse

from mobiles.models import Mobile
from telecompanies.models import Offer

class StaticViewSitemap(Sitemap):
    def items(self):
        url_names = ['core:mobile-brands', ]
        return url_names

    def location(self, item):
        return reverse(item)

class MobilesSitemap(Sitemap):
    def items(self):
        return Mobile.objects.all().order_by('name')

class OffersSitemap(Sitemap):
    def items(self):
        return Offer.objects.all().order_by('mobile_name')
