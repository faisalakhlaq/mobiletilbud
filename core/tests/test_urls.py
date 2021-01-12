from django.test import SimpleTestCase
from django.urls import reverse, resolve
from core.views import (HomeView, MobileManufacturersView, get_mobile_auto_complete)

class TestUrls(SimpleTestCase):
    def test_mobiles_and_offers_url_resolves(self):
        url = reverse('core:mobiles-and-offers')
        self.assertEquals(resolve(url).func.view_class, HomeView)

    def test_mobile_search_url_resolves(self):
        url = reverse('core:mobile_search_auto_complete')
        self.assertEquals(resolve(url).func, get_mobile_auto_complete)

    def test_mobile_brands_url_resolves(self):
        url = reverse('core:mobile-brands')
        self.assertEquals(resolve(url).func.view_class, MobileManufacturersView)
