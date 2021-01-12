from django.test import SimpleTestCase
from django.urls import resolve, reverse

from mobiles.views import (MobileDetailView, MobileComparison)

class TestUrls(SimpleTestCase):
    def test_detail_url_resolves(self):
        url = reverse('mobiles:mobile-detail', args=['dummy-slug'])
        self.assertEquals(resolve(url).func.view_class, MobileDetailView)

    def test_mobile_comparison_url_resolves(self):
        url = reverse('mobiles:mobile-comparison')
        self.assertEquals(resolve(url).func.view_class, MobileComparison)
        # resolver = resolve('mobiles:mobile-comparison')
        # self.assertEquals(resolver.func.cls, MobileComparison)

