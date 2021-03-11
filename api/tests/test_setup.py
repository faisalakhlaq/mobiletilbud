# from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from rest_framework.test import APITestCase
# import tempfile
# from PIL import Image

from django.conf import settings
from telecompanies.models import TelecomCompany

class TestSetUp(APITestCase):
    def setUp(self):
        self.register_url = reverse("api:partner-signup")
        self.login_url = reverse("api:partner-login")
        self.company = TelecomCompany.objects.create(name='Test')
        # file = SimpleUploadedFile("static/media/images/default_mobile_image.jpg", b"abc", content_type="image/jpg")
        # self.tmp_file = SimpleUploadedFile(
        #         "static/media/images/default_mobile_image.jpg", "file_content", content_type="image/jpg")
        # image = Image.new('RGBA', size=(50, 50), color=(155, 0, 0))
        # file = tempfile.NamedTemporaryFile(suffix='.png')
        # image.save(file)
        image_path = settings.MEDIA_ROOT / 'images/default_mobile_image.jpg'
        self.image = {
            'image': open(image_path, 'rb')
        }
        self.user = {
            'username': 'username',
            'first_name': 'first_name', 
            'last_name': 'last_name', 
            'email': 'email@gmail.com', 
            'password': 'password',
            'image': str(image_path),
            'company': self.company.id,
        }
        # self.user = {
        #     'user':{
        #         'username': 'username',
        #         'first_name': 'first_name', 
        #         'last_name': 'last_name', 
        #         'email': 'email@gmail.com', 
        #         'password': 'password',
        #     },
            # 'image': image,
            # 'image': "static/media/images/default_mobile_image.jpg", 
        #     'company': self.company.id,
        #     'address': {},
        # }
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
        # self.tmp_file.delete()
        return super().tearDown()
