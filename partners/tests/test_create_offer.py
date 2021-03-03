
from django.http import response
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from django.contrib.auth import authenticate

from core.models import TelecomCompany
from mobiles.models import Mobile
from telecompanies.models import Offer


class BaseTest(TestCase):
    def setUp(self):
        self.company = TelecomCompany.objects.create(name='Test')
        self.company2 = TelecomCompany.objects.create(name='Company2')
        self.mobile = Mobile.objects.create(name='Test Mobile')

        self.sign_url = reverse("partners:partners_signup")
        self.login_url = reverse("partners:partners_login")
        self.create_offer_url = reverse("partners:create_offer")
        self.user = {
            'username': 'username',
            'first_name': 'first_name', 
            'last_name': 'last_name', 
            'email': 'email@gmail.com', 
            'password': 'password',
            'image': 'static/media/images/default_mobile_image.png', 
            'company': self.company.id,
        }
        self.offer = {
            'mobile': self.mobile.id,
            'telecom_company': self.company.id,
            'mobile_name': 'mobile_name',
            'discount': 'discount',
            'discount_offered': 500,
            'offer_url': 'https://www.telenor.dk/shop/mobil/apple/apple-iphone-11-black-64gb/?subscriptionId=12460892',
            'price': '500',
        }
        return super().setUp()

    def tearDown(self):
        self.company.delete()
        self.mobile.delete()
        self.company2.delete()


class CreateOfferTest(BaseTest):
    def test_create_offer_page_unaccessable_without_login(self):
        """Test if we are redirected to login url if we are not logged in."""
        response = self.client.get(self.create_offer_url)
        self.assertEqual(response.status_code, 302)
        self.assertTemplateUsed('registration/login.html')
        self.assertEqual(response.url, "/accounts/login/?next=/create_offer/")

    def test_loggedin_user_can_access_create_offer_page(self):
        """Test if the create offer page is shown for the logged in user"""
        # 1. First create the user 
        # 2. Set user as active
        # 3. Login the user
        # 4. Try to access the create offer page
        self.client.post(self.sign_url, self.user, format='text/html')
        user1 = User.objects.filter(email=self.user['email']).first()
        user1.is_active = True
        user1.save()
        self.client.post(self.login_url, self.user, format='text/html')
        response = self.client.get(self.create_offer_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'partners/create_offer.html')

    def test_create_offer(self):
        """Test if an offer can be created."""
        # 1. First create the user 
        # 2. Set user as active
        # 3. Login the user
        # 4. Create a post request to create offer page
        self.client.post(self.sign_url, self.user, format='text/html')
        user1 = User.objects.filter(email=self.user['email']).first()
        user1.is_active = True
        user1.save()
        self.client.post(self.login_url, self.user, format='text/html')
        self.client.post(self.create_offer_url, self.offer)
        offer = Offer.objects.filter(
            mobile = self.mobile
            )[0]
        self.assertTrue(offer)
        self.assertEqual(offer.offer_url, self.offer['offer_url'])

    def test_create_offer_with_wrong_company(self):
        """Test to create an offer with a company which if not users company."""
        # 1. First create the user 
        # 2. Set user as active
        # 3. Login the user
        # 4. Set a different company for the offer. User should not be employee of this company
        # 5. Create a post request to create offer page
        self.client.post(self.sign_url, self.user, format='text/html')
        user1 = User.objects.filter(email=self.user['email']).first()
        user1.is_active = True
        user1.save()
        self.client.post(self.login_url, self.user, format='text/html')
        self.offer['telecom_company'] = self.company2
        self.client.post(self.create_offer_url, self.offer)
        offer = Offer.objects.filter(
            mobile = self.mobile
            )
        self.assertFalse(offer)
