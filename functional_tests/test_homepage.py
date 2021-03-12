from django.conf import settings
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.urls import reverse
from selenium import webdriver
# from webdriver_manager.chrome import ChromeDriverManager

class TestHomePage(StaticLiveServerTestCase):

    def setUp(self):
        chromeOptions = webdriver.ChromeOptions() 
        chromeOptions.add_argument("--remote-debugging-port=8000")
        chromeOptions.add_argument("--headless") 
        # self.browser = webdriver.Chrome(
        #     executable_path=ChromeDriverManager().install(),
        #     options=chromeOptions)
        self.browser = webdriver.Chrome(
            executable_path='/snap/bin/chromium.chromedriver',
        options=chromeOptions)

    def tearDown(self):
        self.browser.close()

    def test_empty_home_page(self):
        self.browser.get(self.live_server_url)
        # first time request with no offers on the page
        alert = self.browser.find_element_by_tag_name('h3').text
        heading_text = 'POPULÆRE TILBUD'
        if settings.LANGUAGE_CODE == 'en':
            heading_text = 'POPULAR OFFERS'
        self.assertEquals(alert, heading_text)

    def test_company_page_redirect(self):
        """check if clicking to the companies
        button open the company page."""
        companies_url = self.live_server_url + reverse("telecompanies:offers")
        self.browser.get(self.live_server_url)
        self.browser.find_element_by_id('company').click()
        self.assertEquals(
            self.browser.current_url,
            companies_url
        )
