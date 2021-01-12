from django.test import TestCase
from mobiles.models import Mobile

class TestModels(TestCase):
    def setUp(self):
        self.mobile1 = Mobile.objects.create(
            name = 'test mobile1',
            full_name = 'huawei test mobile1',
            cash_price = 500,
        )
    
    def test_slug(self):
        # Test if the slug is automatically created
        self.assertTrue(not self.mobile1.slug == None)
