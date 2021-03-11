from .test_setup import TestSetUp


class TestSignupPartner(TestSetUp):
    def test_cannot_signup_without_credentials(self):
        response = self.client.post(self.register_url, format='json')
        self.assertEqual(response.status_code, 400)

    # TODO
    # def test_correct_signup(self):
    #     # response = self.client.post(self.register_url, self.user, format='multipart')
    #     data={
    #         'user': self.user,
    #         'image': self.image,
    #         'address': {},
    #     }
    #     self.client.request(data=data)
    #     response = self.client.post(self.register_url, user=self.user, image=self.image, address={})#, format='json')
    #     print(response.data)
    #     self.assertEqual(response.status_code, 201)


class TestLogin(TestSetUp):

    def test_cannot_login_without_credentials(self):
        response = self.client.post(self.login_url, format='json')
        self.assertEqual(response.status_code, 400)
    
    # TODO
    # def test_correct_login(self):
    #     # self.client.post(self.register_url, self.user, format='json')
    #     response = self.client.post(self.register_url, self.user,) #, format='json')
    #     response = self.client.post(
    #         self.login_url, 
    #         username=self.user['username'], 
    #         password=self.user['password'],
    #         format='json'
    #     )
    #     self.assertEqual(response.status_code, 200)
