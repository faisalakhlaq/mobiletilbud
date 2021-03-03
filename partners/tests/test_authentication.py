from os import stat
from django.test import TestCase
from django.urls import reverse
from core.models import TelecomCompany
from django.contrib.auth.models import User
from django.contrib.auth import authenticate

class BaseTest(TestCase):
    def setUp(self):
        self.sign_url = reverse("partners:partners_signup")
        self.login_url = reverse("partners:partners_login")
        self.company = TelecomCompany.objects.create(name='Test')
        self.user = {
            'username': 'username',
            'first_name': 'first_name', 
            'last_name': 'last_name', 
            'email': 'email@gmail.com', 
            'password': 'password',
            'image': 'static/media/images/default_mobile_image.png', 
            'company': self.company.id,
        }
        self.user_invalid_email = {
            'username': 'username',
            'first_name': 'first_name', 
            'last_name': 'last_name', 
            'email': 'email@', 
            'password': 'password',
            'image': 'static/media/images/default_mobile_image.png', 
            'company': self.company.id,
        }
        return super().setUp()

    def tearDown(self):
        self.company.delete()

class SignupTest(BaseTest):
    def test_signup_page_displayed_correctly(self):
        """Test if the signup page is displayed on
        sending the get request for signup."""
        response = self.client.get(self.sign_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'registration/signup.html')

    def test_partner_can_signup(self):
        """Test if a partner is created by providing all the required fields"""
        response = self.client.post(self.sign_url, self.user, format='text/html')
        self.assertEqual(response.status_code, 302)

    def test_wrong_email_signup(self):
        """Test if we can create an account with wrong email"""
        response = self.client.post(self.sign_url, 
        self.user_invalid_email, format='text/html')
        self.assertEqual(response.status_code, 400)

    def test_user_exists_already(self):
        """Test if we can create an account with 
        credentials of an already existing user."""
        self.client.post(self.sign_url, self.user, format='text/html')
        response = self.client.post(self.sign_url, self.user, format='text/html')
        self.assertEqual(response.status_code, 400)

class LoginTest(BaseTest):
    def test_can_access_login_page(self):
        """Test if the login page is displayed correctly."""
        response = self.client.get(self.login_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'registration/login.html')

    def test_successfull_login(self):
        """Test if an active user can login."""
        self.client.post(self.sign_url, self.user, format='text/html')
        user1 = User.objects.filter(email=self.user['email']).first()
        user1.is_active = True
        user1.save()
        response = self.client.post(self.login_url, self.user, format='text/html')
        self.assertEqual(response.status_code, 302)
        user = authenticate(username=self.user['username'], 
        password=self.user['password'])
        self.assertTrue((user is not None) and user.is_authenticated)

    def test_unsuccessfull_login_with_inactive_user(self):
        """Test if an in-active user can not login."""
        self.client.post(self.sign_url, self.user, format='text/html')
        # response = self.client.post(self.login_url, self.user, format='text/html')
        # self.assertEqual(response.status_code, 401)
        user = authenticate(username=self.user['username'], 
        password=self.user['password'])
        self.assertTrue(user is None)

    def test_wrong_password_login(self):
        """Test if a user can not login with wrong password."""
        self.client.post(self.sign_url, self.user, format='text/html')
        user1 = User.objects.filter(email=self.user['email']).first()
        user1.is_active = True
        user1.save()
        user = authenticate(username=self.user['username'], 
        password='pass')
        self.assertFalse(user)

    def test_wrong_username_login(self):
        """Test if a user can not login with wrong password."""
        self.client.post(self.sign_url, self.user, format='text/html')
        user1 = User.objects.filter(email=self.user['email']).first()
        user1.is_active = True
        user1.save()
        user = authenticate(username='name', 
        password=self.user['password'])
        self.assertFalse(user)
