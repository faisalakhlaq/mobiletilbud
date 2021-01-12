from django.test import SimpleTestCase
from django.urls import resolve, reverse

from telecompanies.views import (
    OffersHome,
    PopularOffersView,
    OfferDetailView,
    get_tilbud_auto_complete,
    )

class TestUrls(SimpleTestCase):
    def test_home_resolves(self):
        url = reverse('telecompanies:home')
        self.assertEquals(resolve(url).func.view_class, OffersHome)

    def test_offers_resolves(self):
        url = reverse('telecompanies:offers')
        self.assertEquals(resolve(url).func.view_class, PopularOffersView)

    def test_auto_complate_resolves(self):
        url = reverse('telecompanies:tilbud_search_auto_complete')
        self.assertEquals(resolve(url).func, get_tilbud_auto_complete)
