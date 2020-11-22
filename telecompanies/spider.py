from bs4 import BeautifulSoup
from celery import shared_task
from django.db.models import Q
import requests
from selenium import webdriver
from webdriver_manager.firefox import GeckoDriverManager
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from .models import Offer
from core.models import Mobile, TelecomCompany, MobileBrand


def has_child(node):
    """Check if a given node has child nodes in it"""
    # print(type(node))
    try:
        node.children
        return True
    except:
        return False

def samsung_models_spider():
    headers = {'User-agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:61.0) Gecko/20100101 Firefox/61.0'}
    response = requests.get('https://www.phonemodelslist.com/samsung/', headers=headers)
    content = response.content

    soup = BeautifulSoup(content, "html.parser")
    rows = soup.find("table", {"id": "tablepress-39"}).find("tbody", {"class", "row-hover"}).find_all("tr")
    brand = MobileBrand.objects.get(name='Samsung')
    for row in rows:
        try:
            name1 = row.find("td", {"column-1"}).text.strip().split(' ', 1)[1].strip()
            name2 = row.find("td", {"column-2"}).text.strip().split(" ", 1)[1].strip()
            # print(name1)
            # print(name2)
            _ = Mobile.objects.get_or_create(name=name1, brand=brand)
            _ = Mobile.objects.get_or_create(name=name2, brand=brand)
        except:
            pass

def save_offer(mobile_name, telecom_company_name, 
               offer_url=None, discount=0, price=0):
    """Save the offer in the database"""
    # import pdb; pdb.set_trace()
    offer = Offer()
    mobile = Mobile.objects.filter(Q(name__iexact=mobile_name) | 
                                   Q(full_name__iexact=mobile_name))
    if mobile: offer.mobile = mobile[0]
    telecom_company = TelecomCompany.objects.filter(
        name=telecom_company_name)
    if telecom_company:
        offer.telecom_company = telecom_company[0]
    else:
        offer.telecom_company = TelecomCompany.objects.create(
            name=telecom_company_name)
    offer.mobile_name = mobile_name
    if offer_url:
        offer.offer_url = offer_url
    if discount != 0:
        # extract the float value from the string
        offer.discount = discount
        offer.discount_offered = float(''.join(i for i in discount if i.isdigit()))
    if price != 0:
        offer.price = price
    # Check if the same offer exists previously then delete the old one
    # Check if the mobile or mobile_name and telecom company are same then 
    # delete the old offer and save the new one
    if offer.mobile:
        existing_offer = Offer.objects.filter(Q(mobile=offer.mobile),
                                            Q(telecom_company=offer.telecom_company))
        if existing_offer:
            existing_offer[0].delete()
    else:
        existing_offer = Offer.objects.filter(Q(mobile_name__iexact=mobile_name),
                                            Q(telecom_company=offer.telecom_company))
        if existing_offer:
            existing_offer[0].delete()
    offer.save()

# TODO tilbud_urls in the fetched tilbud are not complete. 
# Append base_ulr with all
class TeliaSpider:
    def __init__(self):
        self.tilbud_url = 'https://shop.telia.dk/cgodetilbud.html'
        self.headers = {'User-agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:61.0) Gecko/20100101 Firefox/61.0'}

    # @shared_task
    def get_telia_offers(self):
        response = requests.get(self.tilbud_url, headers=self.headers)
        content = response.content
        soup = BeautifulSoup(content, 'html.parser')
        wrap_div = soup.find('div', {'id': 'page'}).find('div',{'class':'wrap clear'})
        ajax_div = wrap_div.find('div', {"class", "wide clear"}).find('div')
        rows = ajax_div.find_all("div", {'class': 'grids'})
        offer_divs = []
        for row in rows:
            for div in row.find_all('div'):
                offer_divs.append(div.find('div', {'class': 'productbox'}))
        for p_box in offer_divs:
            try:
                # p_box = od.find('div', {'class': 'productbox'})
                rabat_div = p_box.find('div', {'class': ' tsr-tactical-flash tsr-tactical-round tsr-color-purple tsr-first'})
                if not rabat_div: rabat_div = p_box.find_all('div')[0]
                discount_div = rabat_div.find('span', {'class':'discountamount'})
                discount = 0
                if discount_div: discount = discount_div.find('b').text.strip()
                name_and_link = p_box.find('h2').find('a', href=True)
                mobile_name = name_and_link.text.strip().rsplit(' ', 1)[0]
                offer_url = name_and_link['href']
                table = p_box.find('table', {'class': 'product-prices'})
                # price_tr = table.find('tbody').find_all('tr')
                price_tr = table.find_all('tr')
                price = 0
                for tr in price_tr:
                    td = tr.find_all('td')
                    if len(td) < 2:
                        continue
                    td1 = td[0]
                    td2 = td[1]
                    if 'Mindstepris' in td1.text.strip():
                        price = td2.text.strip()
                save_offer(mobile_name=mobile_name, telecom_company_name='Telia',
                            offer_url=offer_url, discount=discount, price=price)
            except Exception as e:
                print(e)

class ThreeSpider:
    def __init__(self):
        self.tilbud_url = 'https://www.3.dk/mobiler-tablets/mobiler/#Tilbud'
        self.firefox_driver = self.configure_driver()
        self.base_url = 'https://www.3.dk'

    def configure_driver(self):
        # Add additional Options to the webdriver
        firefox_options = FirefoxOptions()
        # add the argument and make the browser Headless.
        firefox_options.add_argument("--headless")
        try:
            driver = webdriver.Firefox(options=firefox_options,
                                       executable_path=GeckoDriverManager().install())
        except:
            driver = webdriver.Firefox(options=firefox_options,
                                       executable_path='/usr/local/bin/geckodriver')
        return driver

    # @shared_task
    def get_three_offers(self):
        try:
            print("_____________GETTING 3 OFFERS_______________")
            self.firefox_driver.get(self.tilbud_url)
            devices = WebDriverWait(self.firefox_driver, 20).until(
                EC.presence_of_element_located((By.CLASS_NAME, "devices"))
            )
            soup = BeautifulSoup(self.firefox_driver.page_source, "html.parser")
            device_list = soup.find("div", {"class": "device-list"})
            device_section = device_list.find("section", {"class": "device-list"})
            ul_list = device_section.find("ul", {"class": "list filtering"})
            active = ul_list.find("li", {"class": "active"})
            devices_li = active.find("ul", {"class": "devices"}).find_all("li")
            if not devices_li:
                return #TODO check what to do here
            # print(devices_li)
            self.get_tilbud_devices(devices_li)
            self.close_webdriver()
        except (TimeoutException, Exception) as e:
            print(e)
            self.close_webdriver()

    def close_webdriver(self):
        if self.firefox_driver:
            self.firefox_driver.close()
            self.firefox_driver.quit()

    def get_tilbud_devices(self, devices_li):
        for li in devices_li:
            try:
                article = li.find("article")
                h3_mobile_name = article.find("header").find("h3")
                mobile_name = h3_mobile_name.text.strip().split("\n")[0]
                discount = h3_mobile_name.text.strip().split("\n")[1].strip()
                shop_div = article.find("div", {"class": "shop"})
                url = shop_div.find('a', href=True)
                offer_url = self.base_url + url['href']
                price = shop_div.find("p", {"class": "lowest-price"}).text.strip()
                save_offer(mobile_name=mobile_name.strip(), telecom_company_name="3",
                            offer_url=offer_url, discount=discount, price=price)
            except Exception as e:
                print(e)

class TelenorSpider:
    def __init__(self):
        self.headers = {'User-agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:61.0) Gecko/20100101 Firefox/61.0'}
        self.telenor_tilbud_url = 'https://www.telenor.dk/shop/mobiler/campaignoffer/'

    # @shared_task
    def get_telenor_offers(self):
        response = requests.get(url=self.telenor_tilbud_url, headers=self.headers)
        content = None
        if response:
            content = response.content
        if not content:
            return None

        soup = BeautifulSoup(content, "html.parser")
        offers = soup.find_all("div", {"data-filter_campaignoffer": "campaignoffer"})
        for offer_ in offers:
            try:
                offer_div = offer_.find("div")
                offer_link = offer_div.find('a', href=True)
                mobile_url = offer_link['href']
                mobile_desc_div = offer_link.find("div", {
                    "class": "grid-row--gutter-none grid-row--bottom product-block__info padding-leader--large full-width"})
                info_div = mobile_desc_div.find("div")
                #strip extra spaces and then remove first word
                # from name which is always company name
                full_name = info_div.find("h3").text.strip()
                mobile_name = None
                if full_name:
                    mobile_name = full_name.split(' ', 1)[1]
                price_info = info_div.find_all("p")
                discount = 0
                if price_info and len(price_info) >= 2:
                    discount = price_info[1].text.strip()
                save_offer(mobile_name=mobile_name, 
                            telecom_company_name='Telenor', 
                            offer_url=mobile_url, discount=discount)
            except Exception as e:
                print(e)

    def get_iphone_specs(self):
        for url in self.urls:
            pass
            headers = {'User-agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:61.0) Gecko/20100101 Firefox/61.0'}
            response = requests.get(url=url, headers=headers)
            content = None
            if response: content = response.content
            if content:
                soup = BeautifulSoup(content, "html.parser")
                # netvark_div = soup.find('label', {"data-element": "techSpecsTitle"})
                techspecs = soup.find('div', {"data-element": "techSpecs"})
                print("We got some content!", techspecs)
        return None
