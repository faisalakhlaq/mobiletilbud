from abc import ABC, abstractmethod
from bs4 import BeautifulSoup
# from celery import shared_task
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q
import re
import requests
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.firefox import GeckoDriverManager

from .models import Offer
from core.models import TelecomCompany
from mobiles.models import Mobile, MobileBrand
from mobiles.utils import HeaderFactory, ProxyFactory

def task_fetch_offers():
    TelenorSpider().fetch_offers()
    YouSeeSpider().fetch_offers()
    TeliaSpider().get_telia_offers()
    ThreeSpider().get_three_offers()

class AbstractTilbudSpider(ABC):
    def __init__(self):
        self.headers = HeaderFactory()
        super().__init__()
    
    def close_webdriver(self, driver):
        if driver:
            driver.close()
            driver.quit()

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

    @abstractmethod
    def fetch_offers(self):
        print('Fetching Tilbud for ', self.__class__.__name__)

    def save_offer(self, mobile_name, telecom_company_name, 
                offer_url=None, m_full_name=None, 
                discount=0, price=0, telecom_company=None):
        """Save the offer in the database"""
        # import pdb; pdb.set_trace()
        offer = Offer()
        mobile = None
        if m_full_name:
            try:
                mobile = Mobile.objects.get(full_name__iexact=m_full_name)
            except ObjectDoesNotExist as e:
                print(f'Unable to find {m_full_name} mobile by full name :', e)
        if not mobile:
            filtered_mobile = Mobile.objects.filter(Q(name__iexact=mobile_name) | 
                                        Q(full_name__iexact=mobile_name))
            if filtered_mobile: mobile = filtered_mobile[0]
        if mobile: offer.mobile = mobile
        if telecom_company:
            offer.telecom_company = telecom_company
        else:
            telecom_company = TelecomCompany.objects.filter(
                name=telecom_company_name)
            if telecom_company:
                offer.telecom_company = telecom_company[0]
            else:
                offer.telecom_company = TelecomCompany.objects.create(
                    name=telecom_company_name)

        # Set mobile name
        if mobile:
            offer.mobile_name = mobile.full_name
        elif m_full_name:
            offer.mobile_name = m_full_name
        else:    
            offer.mobile_name = mobile_name
        if offer_url:
            offer.offer_url = offer_url
        if discount != 0:
            # extract the float value from the string
            offer.discount = discount
            value = (''.join(i for i in discount if i.isdigit()))
            if value:
                if telecom_company_name == '3':
                    import pdb; pdb.set_trace()
                    if 'spar' in discount.lower():
                        offer.discount_offered = float(value)
                else:
                        offer.discount_offered = float(value)
        if price != 0:
            offer.price = price
        offer.save()

    def delete_old_offers(self, telecom_company):
        offers = Offer.objects.filter(telecom_company=telecom_company)
        if offers:
            offers.delete()
            print(f'Offers Deleted for {telecom_company.name}')

    def get_response(self, url, tele_comp_name):
        response = None
        try:
            response = requests.get(
                url=url, 
                # proxies={"http": proxy, "https": proxy}, 
                headers=self.headers.get_header(),
                timeout=30, # timeout in 20 seconds in order to avoid hanging/freezing
            )
        except Exception as e:
            print(f'Exception while Requesting {tele_comp_name} offers: ', e)
        return response

class TelenorSpider(AbstractTilbudSpider):
    def __init__(self):
        self.telenor_tilbud_url = 'https://www.telenor.dk/shop/mobiler/campaignoffer/'
        self.base_url = 'https://www.telenor.dk'
        super(TelenorSpider, self).__init__()

    # @shared_task
    def fetch_offers(self):
        offers = None
        try:
            # proxies = ProxyFactory().get_proxies(number_of_proxies=3)
            # import pdb; pdb.set_trace()
            for i in range(3):
                # Make 3 tries to get the offers 
                # in case something goes wrong
                # proxy =  None
                # if len(proxies) > 0:
                #     proxy = proxies.pop()
                response = self.get_response(url=self.telenor_tilbud_url, 
                tele_comp_name='Telenor')
                content = None
                if response:
                    content = response.content
                if not content:
                    continue
                soup = BeautifulSoup(content, "html.parser")
                offers = soup.find_all("div", {"data-filter_campaignoffer": "campaignoffer"})
                if offers and len(offers) > 0:
                    break
        except Exception as e:
            print('Exception in Telenor while fetching: ', e)
        # response = requests.get(url=self.telenor_tilbud_url, headers=self.headers)
        # content = None
        # if response:
        #     content = response.content
        # if not content:
        #     return None

        # soup = BeautifulSoup(content, "html.parser")
        # offers = soup.find_all("div", {"data-filter_campaignoffer": "campaignoffer"})
        # TODO make a new method from here
        # Lets check if we got some new 
        # offers and delete old ones
        telecom_company = None
        if offers and len(offers) > 0:
            telecom_company = TelecomCompany.objects.get(name='Telenor')
            self.delete_old_offers(telecom_company)
            for offer_ in offers:
                try:
                    offer_div = offer_.find("div")
                    offer_link = offer_div.find('a', href=True)
                    mobile_url = self.base_url + offer_link['href']
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
                    price = 0
                    if price_info and len(price_info) >= 2:
                        price = price_info[0].text.strip()
                        discount = price_info[1].text.strip()
                    self.save_offer(mobile_name=mobile_name,
                                telecom_company_name='Telenor', 
                                offer_url=mobile_url, m_full_name=full_name, 
                                discount=discount, price=price,
                                telecom_company=telecom_company)
                except Exception as e:
                    print('Telenor Spider Exception: ', e)
                    continue


class YouSeeSpider(AbstractTilbudSpider):
    def __init__(self):
        self.base_url = 'https://yousee.dk'
        self.tilbud_url = 'https://yousee.dk/mobil/mobiltelefoner/?filter=tilbud'
        super(YouSeeSpider, self).__init__()

    # @shared_task
    def fetch_offers(self):
        try:
            lis = None
            tele_company = None
            for i in range(3):
                # import pdb; pdb.set_trace()
                driver = self.configure_driver()
                driver.get(self.tilbud_url)
                devices = WebDriverWait(driver, 60).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "component-terminal-list__terminal-list"))
                )
                soup = BeautifulSoup(driver.page_source, "html.parser")
                if not soup: continue
                lis = soup.find_all('li', {'class', 'component-terminal-list__terminal-list__item col-12 col-sm-6 col-lg-4 col--reduced-gutter'})
                if lis and len(lis) > 0: 
                    tele_company = TelecomCompany.objects.get(name='YouSee')
                    self.delete_old_offers(telecom_company=tele_company)
                    break
            
            self.get_devices(lis, telecom_company=tele_company)
            self.close_webdriver(driver)
        except (TimeoutException, Exception) as e:
            print('Exception while fetching YouSee offers: ', e)
            self.close_webdriver(driver)

    def get_devices(self, rows, telecom_company=None):
        if not rows or not len(rows) > 0: 
            print('No offers found for YouSee!')
            return
        for li in rows:
            try:
                anker = li.find('div').find('a')
                offer_url = self.base_url + anker['href']
                info = anker.find('div', {'class', "component-terminal-card__text-container"})
                brand = info.find('div', {'class', 'component-terminal-card__brand'}).text.strip()
                mobile_name = info.find('div', {'class', 'component-terminal-card__title'}).text.strip()
                m_full_name = brand + " " + mobile_name
                section = anker.find('section', {'class', "component-terminal-card__price-container"})
                saving_div = section.find('div', {'class', 'component-terminal-card__price-container__savings'})
                discount = saving_div.find('span').text.strip()
                price_div = section.find('div', {'class', 'component-terminal-card__price-container__price'})
                price_span = price_div.find_all('span')
                if price_span:
                    if len(price_span) >= 2:
                        price = price_span[0].text.strip() + " " + price_span[1].text.strip()
                    else:
                        price = price_span[0].text.strip()
                self.save_offer(mobile_name=mobile_name, 
                m_full_name=m_full_name, 
                telecom_company_name='YouSee',
                offer_url=offer_url, 
                discount=discount, price=price,
                telecom_company=telecom_company)
            except Exception as e:
                print('Error-YouSee offer spider. Exception: ', e)
                continue


class TeliaSpider(AbstractTilbudSpider):
    def __init__(self):
        self.telia_base_url = 'https://shop.telia.dk'
        self.tilbud_url = 'https://shop.telia.dk/cgodetilbud.html'
        super(TeliaSpider, self).__init__()

    # @shared_task
    def fetch_offers(self):
        rows = None
            # TODO use proxies
            # proxies = ProxyFactory().get_proxies(number_of_proxies=3)
        for i in range(3):
            try:
                # Make 3 tries to get the offers 
                # in case something goes wrong
                response = self.get_response(url=self.tilbud_url, 
                tele_comp_name='Telia')
                content = None
                if response:
                    content = response.content
                if not content:
                    continue
                soup = BeautifulSoup(content, "html.parser")
                if not soup: continue
                wrap_div = soup.find('div', {'id': 'page'}).find('div',{'class':'wrap clear'})
                ajax_div = wrap_div.find('div', {"class", "wide clear"}).find('div')
                rows = ajax_div.find_all("div", {'class': 'grids'})
                if rows and len(rows) > 0:
                    break
            except Exception as e:
                print('Exception in Telia while fetching request: ', e)
                continue
        if not rows or not len(rows) > 0: 
            print('No offers found for Telia')
            return
        offer_divs = []
        for row in rows:
            for div in row.find_all('div'):
                offer_divs.append(div.find('div', {'class': 'productbox'}))
        tele_company = None
        if offer_divs and len(offer_divs) > 0:
            tele_company = TelecomCompany.objects.get(name='Telia')
            self.delete_old_offers(tele_company)
        # import pdb; pdb.set_trace()
        for p_box in offer_divs:
            try:
                rabat_div = p_box.find('div', {'class': ' tsr-tactical-flash tsr-tactical-round tsr-color-purple tsr-first'})
                if not rabat_div: rabat_div = p_box.find_all('div')[0]
                discount_div = rabat_div.find('span', {'class':'discountamount'})
                discount = 0
                if discount_div: discount = discount_div.find('b').text.strip()
                name_and_link = p_box.find('h2').find('a', href=True)
                # TODO mobile name includes the memory. Use this as mobile memory variation 
                mobile_name = self.extract_name(name_and_link)
                offer_url = self.telia_base_url + name_and_link['href']
                table = p_box.find('table', {'class': 'product-prices'})
                # price_tr = table.find('tbody').find_all('tr')
                price_tr = table.find_all('tr')
                price = None
                for tr in price_tr:
                    td = tr.find_all('td')
                    if len(td) < 2:
                        continue
                    td1 = td[0]
                    td2 = td[1]
                    if 'Mindstepris' in td1.text.strip() or 'Pris.' in td1.text.strip():
                        if not price:
                            price = td1.text.strip() +" "+td2.text.strip()
                        else:
                            price = price +" - "+ td1.text.strip() +" "+td2.text.strip()
                self.save_offer(mobile_name=mobile_name, 
                                telecom_company_name='Telia',
                                offer_url=offer_url, discount=discount, 
                                price=price, telecom_company=tele_company)
            except Exception as e:
                print('Exception in extracting Telia offer: ', e)
                continue

    def extract_name(self, sequence):
        pattern = r'\(\d+\S+\s\S+\)'
        # Check if the mobile name (sequence) includes ram information e.g.
        # Z40 lite(128GB RAM). Remove it by using re
        # \( check for bracket (
        # \d+ check for any number of digits
        # \S+ check for any number of characters
        # \s check for space
        # \S+ 
        # \) check for ending bracket )
        sequence = sequence.text.strip()
        found = re.search(pattern, sequence)
        if found:
            sequence = sequence.replace(found.group(),'')
        mobile_name = sequence.strip().rsplit(' ', 1)[0]
        return mobile_name        



class ThreeSpider(AbstractTilbudSpider):
    def __init__(self):
        self.tilbud_url = 'https://www.3.dk/mobiler-tablets/mobiler/#Tilbud'
        self.base_url = 'https://www.3.dk'
        super(ThreeSpider, self).__init__()

    # @shared_task
    def fetch_offers(self):
        try:
            devices_li = None
            tele_company = None
            for i in range(3):
                driver = self.configure_driver()
                driver.get(self.tilbud_url)
                devices = WebDriverWait(driver, 20).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "devices"))
                )
                soup = BeautifulSoup(driver.page_source, "html.parser")
                if not soup: continue
                device_list = soup.find("div", {"class": "device-list"})
                device_section = device_list.find("section", {"class": "device-list"})
                ul_list = device_section.find("ul", {"class": "list filtering"})
                active = ul_list.find("li", {"class": "active"})
                devices_li = active.find("ul", {"class": "devices"}).find_all("li")
                if devices_li and len(devices_li) > 0:
                    tele_company = TelecomCompany.objects.get(name='3')
                    self.delete_old_offers(telecom_company=tele_company)
                    break

            self.get_tilbud_devices(devices_li=devices_li, telecom_company=tele_company)
            self.close_webdriver(driver)
        except (TimeoutException, Exception) as e:
            print('Exception while fetching Three offers: ', e)
            self.close_webdriver(driver)

    def get_tilbud_devices(self, devices_li, telecom_company=None):
        if not devices_li or not len(devices_li) > 0:
            print('No offers found for 3')
            return
        for li in devices_li:
            try:
                article = li.find("article")
                h3_mobile_name = article.find("header").find("h3")
                mobile_name = h3_mobile_name.text.strip().split("\n")[0].strip()
                discount = h3_mobile_name.text.strip().split("\n")[1].strip()
                shop_div = article.find("div", {"class": "shop"})
                url = shop_div.find('a', href=True)
                offer_url = self.base_url + url['href']
                price = None
                try:
                    price_box = shop_div.find('div', {'class': 'price-box'})
                    installment_price = price_box.find('span', {'class': 'installment-price'}).text.strip()
                    suffix = price_box.find('span', {'class': 'suffix'}).text.strip()
                    price = shop_div.find("p", {"class": "lowest-price"}).text.strip() + '\n' + \
                    installment_price + " " + suffix
                except:
                    pass
                self.save_offer(mobile_name=mobile_name, 
                            telecom_company_name="3", offer_url=offer_url, 
                            discount=discount, price=price, 
                            telecom_company=telecom_company)
            except Exception as e:
                print('Exception while extracting offer details for 3: ', e)
                continue
