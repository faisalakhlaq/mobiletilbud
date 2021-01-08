import asyncio
from abc import ABC, abstractmethod
from bs4 import BeautifulSoup
from django.core.files.base import ContentFile
from django.db.models import Q
import io
from itertools import cycle
import logging
from PIL import Image
import requests
import time
from selenium import webdriver
from webdriver_manager.firefox import GeckoDriverManager
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import (
    ElementNotVisibleException
)
from mobiles.models import MobileBrand, Mobile
from mobiles.mobile_specs_spider import HeaderFactory, ProxyFactory
from .mobile_specs_spider import GsmarenaMobileSpecSpider

logger = logging.getLogger(__name__)

class AbstractMobileSpider(ABC):
 
    def __init__(self):
        # self.headers = {'User-agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:61.0) Gecko/20100101 Firefox/61.0'}
        self.headers = HeaderFactory()
        super().__init__()
    
    @abstractmethod
    def fetch_mobiles(self, brand_name_):
        """Brand name depicts which urls to use."""
        print("Fetching mobiles")

    def close_webdriver(self, firefox_driver):
        if firefox_driver:
            firefox_driver.close()
            firefox_driver.quit()
    
    def save_mobile(self, name, full_name, brand_name, brand=None, url=None, image=None):
        try:
            if not brand:
                brand = MobileBrand.objects.get(name__iexact=brand_name)
            # mobile = Mobile.objects.get(name__iexact=name, brand=brand)
            try:
                mobile, _created = Mobile.objects.get_or_create(
                    name=name,
                    full_name=full_name,
                    brand=brand,
                    url=url,
                )
            except MultipleObjectsReturned as e:
                logger.error(f"Multiple mobiles returned for full_name {full_name}")
            # if not mobile:
            #     print('Cannot find mobile: ', full_name)
            #     return
            # if mobile.image:
                # mobile is already in the database and has an image.
                # Therefore we are not going to update it.
                # print('NO UPDATES - Mobile and image already available.')
                # return
            if image:
                thumb_io = io.BytesIO()
                image.save(thumb_io, image.format, quality=95)
                # TODO if mobile/ OR ANyName/ is not provided in the save method then 
                # the image is saved to the parent folder i.e. media
                # mobile.image.save('sony/'+image.filename, ContentFile(thumb_io.getvalue()), save=False)
                mobile.image.save('HTC'+'/'+image.filename, ContentFile(thumb_io.getvalue()), save=False)
            mobile.save()
            # if created:
            print("Saved a new mobile: ", mobile.full_name)
            # import pdb; pdb.set_trace()
            # else:
            # print('Updated mobile image: ', mobile.full_name)
        except Exception as e:
            print("Exception while saving Mobile: ", e)
    
    def get_image(self,img_src):
        image = None
        try:
            # img_src = img['src']
            if img_src and len(img_src.strip()) > 5:
                response = requests.get(img_src, stream=True, timeout=30).content
                image_file = io.BytesIO(response)
                image = Image.open(image_file)
                return image
        except Exception as e:
            print('Exception occured while downloading the image: ', e)


class GadgetsndtvMobileSpider(AbstractMobileSpider):
    def __init__(self):
        self.huawei_url = 'https://gadgets.ndtv.com/mobiles/huawei-phones'
        self.samsung_url = 'https://gadgets.ndtv.com/mobiles/samsung-phones'
        super().__init__()
    
    def fetch_mobiles(self, brand_name_):
        header = HeaderFactory().get_header()
        proxies = get_proxies()
        proxy_pool = cycle(proxies)
        proxy = next(proxy_pool)
        if proxies:
            response = requests.get(
                url=self.samsung_url, 
                proxies={"http": proxy, "https": proxy},
                headers=self.headers.get_header(),
                timeout=20,)
        soup = BeautifulSoup(response.content, 'html.parser')
        ul = soup.find('ul', {'class', 'clearfix margin_t20'})
        lis = ul.find_all('li')
        if not lis:
            brand_details = soup.find('div', {'class', 'brand_detail'})
            brand_list = brand_details.find('div', {'class', 'nlist brand_list'})
            ul = brand_list.find('div', {'class', 'brand row'}).find('ul')
            lis = ul.find_all('li')
        brand = MobileBrand.objects.get(name__iexact=brand_name_)
        all_mobiles = Mobile.objects.filter(brand=brand)
        mobile_update_list = []
        for li in lis:
            try:
                image_a = li.find('div', {'class', 'rvw-imgbox'}).find('a')
                mobile_url = image_a['href']
                m_full_name = li.find('a', {'class', 'rvw-title'}).find('strong').text.strip()
                mobile_name = m_full_name.split(' ', 1)[1]
                mobile = all_mobiles.filter(full_name__iexact=m_full_name)
                if mobile:
                    # If the mobile is found only update its url 
                    # and continue to next iteration
                    mobile = mobile[0]
                    if mobile.url != mobile_url:
                        mobile.url = mobile_url
                        mobile_update_list.append(mobile)
                        print('Adding a new mobile to be updated: ', mobile)
                    # mobile.save()
                    # continue
                else:
                    # Image on this website are very small. Therefore we are not
                    # downloading images
                    # img_src = image_a.find('img')['src']
                    # image = self.get_image(img_src)
                    self.save_mobile(name=mobile_name, full_name=m_full_name, 
                    url=mobile_url, brand=brand, brand_name=brand_name_, image=None)
            except Exception as e:
                print(f'Exception in fetching mobiles {brand_name_} ', e)
                continue
        # Bulk update all the objects  
        print('To Be Updated: ', len(mobile_update_list))
        if len(mobile_update_list) > 0:
            Mobile.objects.bulk_update(mobile_update_list, ['url'])
            print('Updated mobiles: ', len(mobile_update_list))


class GsmarenaMobileSpider(AbstractMobileSpider):
    """Fetches mobile data from https://www.gsmarena.com/"""
    def __init__(self):
        self.apple_url = 'https://www.gsmarena.com/apple-phones-48.php'
        self.apple_base_url = 'https://www.gsmarena.com/apple-phones-f-48-0-p'
        self.samsung_url = 'https://www.gsmarena.com/samsung-phones-9.php'
        self.samsung_base_url = 'https://www.gsmarena.com/samsung-phones-f-9-0-p'
        self.nokia_url = 'https://www.gsmarena.com/nokia-phones-1.php'
        self.nokia_base_url = 'https://www.gsmarena.com/nokia-phones-f-1-0-p'
        self.huawei_url = 'https://www.gsmarena.com/huawei-phones-58.php'
        self.huawei_base_url = 'https://www.gsmarena.com/huawei-phones-f-58-0-p'
        self.htc_url = 'https://www.gsmarena.com/htc-phones-45.php'
        self.htc_base_url = 'https://www.gsmarena.com/htc-phones-f-45-0-p'
        super().__init__()

    def get_pages(self, brand_name):
        pages = []
        url = None
        base_url = None
        if 'samsung' in brand_name.lower():
            url = self.samsung_url
            base_url = self.samsung_base_url
        elif 'nokia' in brand_name.lower():
            url = self.nokia_url
            base_url = self.nokia_base_url
        elif 'apple' in brand_name.lower():
            url = self.apple_url
            base_url = self.apple_base_url
        elif 'huawei' in brand_name.lower():
            url = self.huawei_url
            base_url = self.huawei_base_url
        elif 'htc' in brand_name.lower():
            url = self.htc_url
            base_url = self.htc_base_url

        response = requests.get(url=url, 
                                headers=self.headers.get_header(), 
                                timeout=20,)
        pages.append(response.content)
        soup = BeautifulSoup(response.content, "html.parser")
        pages_div = soup.find('div', {'class', 'nav-pages'})
        total_pages = 1
        if pages_div:
            # we are adding one to total pages because the displayed 
            # page doesnot come in the list. So we get one less page
            total_pages = len(pages_div.find_all('a')) + 1
        if total_pages == 1:
            return pages
        for i in range(1, total_pages, 1):
            next_page_url = base_url + str(i+1) + '.php'
            response = requests.get(url=next_page_url, 
                                    headers=self.headers.get_header(),
                                    timeout=20,)
            pages.append(response.content)
            print('Downloaded page number', i)
            time.sleep(20)
        return pages

    def update_mobile_url(self, brand_name_):
        pages = self.get_pages(brand_name_)
        m_brand = MobileBrand.objects.get(name__iexact=brand_name_)
        for p_index, page in enumerate(pages):
            soup = BeautifulSoup(page, "html.parser")
            rows = soup.find('div', {'class', 'makers'}).find('ul').find_all('li')
            # print("GOT mobiles = ", len(rows))
            for row in rows:
                try:
                    anker = row.find('a')
                    mobile_url = 'https://www.gsmarena.com/' + anker['href']
                    mobile_name = anker.find('strong').find('span').text.strip()
                    # To avoid storing apple watches and ipad we are checking if the name
                    # contains iphone, so its a phone. Therefore store it.
                    if 'apple' in brand_name_.lower() and "iphone" not in mobile_name.lower():
                        continue
                    m_full_name = brand_name_.lower().capitalize() + " " + mobile_name
                    filtered_mobiles = Mobile.objects.filter(Q(brand=m_brand),
                                                    Q(name__iexact=mobile_name))
                    mobile = None
                    if not filtered_mobiles:
                        filtered_mobiles = Mobile.objects.filter(Q(brand=m_brand),
                                                    Q(full_name__iexact=m_full_name))
                    if filtered_mobiles:
                        mobile = filtered_mobiles[0]
                        # print('Found a mobile: ', mobile)
                    else:
                        print('Found no mobile with name: ', mobile_name)
                        continue
                    specs = mobile.technical_specs.all()
                    if specs: specs = specs[0]
                    specs_is_null = True
                    if specs:
                        if specs.weight and not specs.weight.strip() == '':
                            specs_is_null = False
                        if specs.screen_type and not specs.screen_type.strip() == '':
                            specs_is_null = False
                        if specs.screen_size and not specs.screen_size.strip() == '':
                            specs_is_null = False
                        if specs.screen_resolution and not specs.screen_resolution.strip() == '':
                            specs_is_null = False
                        if specs.ip_certification and not specs.ip_certification.strip() == '':
                            specs_is_null = False
                        if specs.internal_storage and not specs.internal_storage.strip() == '':
                            specs_is_null = False
                        if specs.external_storage and not specs.external_storage.strip() == '':
                            specs_is_null = False
                        if specs.WLAN and not specs.WLAN.strip() == '':
                            specs_is_null = False
                        if specs.bluetooth and not specs.bluetooth.strip() == '':
                            specs_is_null = False
                        if specs.USB and not specs.USB.strip() == '':
                            specs_is_null = False
                        if specs.battery_type and not specs.battery_type.strip() == '':
                            specs_is_null = False
                        if specs.wireless_charging and not specs.wireless_charging.strip() == '':
                            specs_is_null = False
                        if specs.operating_system and not specs.operating_system.strip() == '':
                            specs_is_null = False
                        if specs.ram and not specs.ram.strip() == '':
                            specs_is_null = False       
                        if specs.launch and not specs.launch.strip() == '':
                            specs_is_null = False
                    # if mobile and not 'gsmarena' in mobile.url:
                    if 'gadgets' in mobile.url or specs_is_null:
                        mobile.url = mobile_url
                        mobile.save()
                        # If we got a mobile then try to get its specs as well
                        print(f"Page number = {p_index}, Sending request for: ", mobile)
                        GsmarenaMobileSpecSpider().fetch_single_specs(mobile)
                        time.sleep(20)
                except Exception as e:
                    print('Exception occured while fetching mobile: ', e)
                    continue

    def fetch_mobiles(self, brand_name_):
        # import pdb; pdb.set_trace()
        pages = self.get_pages(brand_name_)
        brand = MobileBrand.objects.get(name='HTC')
        for page in pages:
            soup = BeautifulSoup(page, "html.parser")
            rows = soup.find('div', {'class', 'makers'}).find('ul').find_all('li')
            # print("GOT mobiles = ", len(rows))
            for row in rows:
                try:
                    anker = row.find('a')
                    mobile_url = 'https://www.gsmarena.com/' + anker['href']
                    mobile_name = anker.find('strong').find('span').text.strip()
                    # To avoid storing apple watches and ipad we are checking if the name
                    # contains iphone, so its a phone. Therefore store it.
                    # if 'apple' in brand_name_.lower() and "iphone" not in mobile_name.lower():
                    #     continue
                    m_full_name = brand_name_.lower().capitalize() + " " + mobile_name
                    img_src = anker.find('img')['src']
                    image = self.get_image(img_src)
                    self.save_mobile(name=mobile_name, full_name=m_full_name,
                    brand_name=brand_name_, brand=brand, url=mobile_url, image=image)
                    # import time
                    # time.sleep(10)
                except Exception as e:
                    print('Exception occured while fetching mobile: ', e)
                    continue

class DoroMobileSpider(AbstractMobileSpider):
    def __init__(self):
        self.doro_urls = [
            'https://www.doro.com/en-gb/products/mobile-phones/',
            'https://www.doro.com/en-gb/products/smartphones/'
        ]
        super().__init__()

    def fetch_mobiles(self, brand_name_):
        # import pdb; pdb.set_trace()
        pages = []
        for url in self.doro_urls:
            response = requests.get(url=url, headers=self.headers.get_header())
            pages.append(response.content)
        for page in pages:
            soup = BeautifulSoup(page, 'html.parser')
            product_o_div = soup.find_all('div', {'class', 'products-tile'})
            for p in product_o_div:
                a_tag = p.find('div', {'class', 'product'}).find('a')
                mobile_url = 'https://www.doro.com' + a_tag['href']
                full_name = a_tag['data-name'].strip()
                name = full_name.split(' ', 1)[1]
                image_url = a_tag.find('div', {'class', 'products-tile-image'}).find('img')['src']
                image_url = 'https://www.doro.com' + image_url
                image = self.get_image(image_url)
                # brand_name = 'Doro'
                self.save_mobile(name=name, full_name=full_name, brand_name=brand_name_,
                                url=mobile_url, image=image)


class MotorolaMobileSpider(AbstractMobileSpider):
    def __init__(self):
        self.nokia_urls = [
            'https://www.gsmarena.com/nokia-phones-1.php'
        ]
        self.sony_urls = [
            'https://www.gsmarena.com/sony-phones-7.php',
            'https://www.gsmarena.com/sony-phones-f-7-0-p2.php',
            'https://www.gsmarena.com/sony-phones-f-7-0-p3.php',
            'https://www.gsmarena.com/sony-phones-f-7-0-p4.php',
            'https://www.gsmarena.com/sony-phones-f-7-0-p5.php',
        ]
        self.one_urls = [
            'https://www.gsmarena.com/oneplus-phones-95.php',
        ]
        self.motorola_urls = [
            'https://www.gsmarena.com/motorola-phones-4.php',
            'https://www.gsmarena.com/motorola-phones-f-4-0-p2.php',
            'https://www.gsmarena.com/motorola-phones-f-4-0-p3.php',
            'https://www.gsmarena.com/motorola-phones-f-4-0-p4.php',
            'https://www.gsmarena.com/motorola-phones-f-4-0-p5.php',
            'https://www.gsmarena.com/motorola-phones-f-4-0-p6.php',
            'https://www.gsmarena.com/motorola-phones-f-4-0-p7.php',
            'https://www.gsmarena.com/motorola-phones-f-4-0-p8.php',
            'https://www.gsmarena.com/motorola-phones-f-4-0-p9.php',
            'https://www.gsmarena.com/motorola-phones-f-4-0-p10.php',
        ]
        super().__init__()

    def fetch_mobiles(self, brand_name_):
        pages = []
        for url in self.sony_urls:
            response = requests.get(url=url, headers=self.headers.get_header())
            pages.append(response.content)

        for page in pages:
            soup = BeautifulSoup(page, "html.parser")
            rows = soup.find('div', {'class', 'makers'}).find('ul').find_all('li')
            print("GOT mobiles = ", len(rows))
            for row in rows:
                try:
                    anker = row.find('a')
                    mobile_url = 'https://www.gsmarena.com/' + anker['href']
                    img_src = anker.find('img')['src']
                    image = self.get_image(img_src)
                    mobile_name = anker.find('strong').find('span').text.strip()
                    m_full_name = brand_name_ + " " + mobile_name
                    self.save_mobile(name=mobile_name, full_name=m_full_name,
                    brand_name=brand_name_, url=mobile_url, image=image)
                except Exception as e:
                    print('Exception occured while fetching Motorola mobile: ', e)
                    continue

    def get_image(self,img_src):
        image = None
        try:
            # img_src = img['src']
            if img_src and len(img_src.strip()) > 5:
                response = requests.get(img_src, stream=True).content
                image_file = io.BytesIO(response)
                image = Image.open(image_file)
                return image
        except Exception as e:
            print('Exception occured while downloading the image: ', e)

    # async def get_page(url):
    #     pass

def configure_driver():
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


class HuawaiMobileSpider():
    def __init__(self):
        self.headers = {'User-agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:61.0) Gecko/20100101 Firefox/61.0'}
        self.url = 'https://consumer.huawei.com/en/phones/'

    def close_webdriver(self, firefox_driver):
        if firefox_driver:
            firefox_driver.close()
            firefox_driver.quit()

    def fetch_mobiles(self, brand_name_):
        firefox_driver = configure_driver()
        try:
            firefox_driver.get(self.url)
            devices = WebDriverWait(firefox_driver, 60).until(
                EC.presence_of_element_located((By.CLASS_NAME, "product-block__background"))
            )
            try:
                load_more_button = firefox_driver.find_element(By.XPATH, "//*[text()='Load More']")
                load_more_button.send_keys(Keys.RETURN)
            except Exception as e:
                print(e)

            soup = BeautifulSoup(firefox_driver.page_source, "html.parser")
            p_rows = soup.find_all('div', {'class', 'product-row row'})
            rows = p_rows[0].find_all('div', {'class', 'product-col'})
            print("ROWS == ", len(p_rows))
            for row in rows:
                mobile_box = row.find('div', {'class', 'product-block'})
                mobile_info_box = mobile_box.find('div', {'class', 'product-block__details'})
                mobile_name_a = mobile_info_box.find('div', {'class', 'heading product-block__title'}).find('a')
                
                full_name = mobile_name_a.text.strip()
                name = full_name.split(" ", 1)[1]
                mobile_url = mobile_name_a['href']
                image_box = row.find('div',{'class','product-block__in js-product-block'})
                image_a = image_box.find('div', {'class','product-block__holder js-img-holder'}).find('a')
                images = image_a.find_all('img')
                image = None
                for img in images:
                    try:
                        img_src = img['data-src']
                        if img_src and len(img_src.strip()) > 5:
                            img_src = 'https://consumer.huawei.com' + img_src
                            response = requests.get(img_src, stream=True).content
                            image_file = io.BytesIO(response)
                            image = Image.open(image_file)
                            break
                    except (KeyError, Exception) as e:
                        print('Exception: ', e)
                        continue
                self.save_huawei_mobile(
                    name=name,
                    full_name=full_name,
                    image=image,
                    url=mobile_url,
                )
            self.close_webdriver(firefox_driver)
        except (TimeoutException, ElementNotVisibleException, Exception) as e:
            print('TIMEOUT - ', e)
            self.close_webdriver(firefox_driver)

    def save_huawei_mobile(self, name, full_name=None, url=None, image=None):
        try:
            # brand = MobileBrand.objects.filter(name__iexact='huawei')
            # if brand: 
            #     brand = brand[0]
            mobile = Mobile.objects.filter(name__iexact=name)[0]
            thumb_io = io.BytesIO()
            image.save(thumb_io, image.format, quality=90)
            mobile.image.save(image.filename, ContentFile(thumb_io.getvalue()), save=False)
            mobile.save()
            print("Saved a new mobile: ", mobile.full_name)
        except Exception as e:
            print("Exception while saving Mobile: ", e)


# def samsung_models_spider():
#     headers = {'User-agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:61.0) Gecko/20100101 Firefox/61.0'}
#     response = requests.get('https://www.phonemodelslist.com/samsung/', headers=headers)
#     content = response.content
#     soup = BeautifulSoup(content, "html.parser")
#     rows = soup.find("table", {"id": "tablepress-39"}).find("tbody", {"class", "row-hover"}).find_all("tr")
#     brand = MobileBrand.objects.get(name='Samsung')
#     for row in rows:
#         try:
#             name1 = row.find("td", {"column-1"}).text.strip().split(' ', 1)[1].strip()
#             name2 = row.find("td", {"column-2"}).text.strip().split(" ", 1)[1].strip()
#             # print(name1)
#             # print(name2)
#             _ = Mobile.objects.get_or_create(name=name1, brand=brand)
#             _ = Mobile.objects.get_or_create(name=name2, brand=brand)
#         except:
#             pass
