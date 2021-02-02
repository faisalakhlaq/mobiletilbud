from bs4 import BeautifulSoup
from celery import shared_task
from dateutil import parser
from django.core.exceptions import ObjectDoesNotExist
from django.core.files.base import ContentFile
from django.db.models import Q, F
import io
import logging
from PIL import Image
import requests
import random 
import time
from urllib3.connection import HTTPSConnection
from requests.exceptions import ReadTimeout
# from urllib3.exceptions import HTTPSConnectionPool

from .models import (Mobile, MobileBrand, MobileTechnicalSpecification,
                     MobileCameraSpecification, MobileVariation, Variation)
from .utils import HeaderFactory, ProxyFactory, update_mobile_launch_date
from itertools import cycle

logger = logging.getLogger(__name__)


class PricePusher:
    def __init__(self):
        self.headers = HeaderFactory()
        self.urls = {
            'Apple': 'https://pricepusher.dk/mobil/Apple-tilbud-priser-uden-mobilabonnement',
            'Samsung': 'https://pricepusher.dk/mobil/Samsung-tilbud-priser-uden-mobilabonnement',
            'Motorola': 'https://pricepusher.dk/mobil/Motorola-tilbud-priser-uden-mobilabonnement',
            'Nokia': 'https://pricepusher.dk/mobil/Nokia-tilbud-priser-uden-mobilabonnement',
            'Sony': 'https://pricepusher.dk/mobil/Sony-tilbud-priser-uden-mobilabonnement',
            'Huawei': 'https://pricepusher.dk/mobil/Huawei-tilbud-priser-uden-mobilabonnement',
            'OnePlus': 'https://pricepusher.dk/mobil/OnePlus-tilbud-priser-uden-mobilabonnement',
            'Doro': 'https://pricepusher.dk/mobil/Doro-tilbud-priser-uden-mobilabonnement',
        }

    def fetch_all_brand_price(self):
        for k,v in self.urls.items():
            try:
                self.fetch_price(_brand_name=k, _url=v)
                print('Going to sleep for 2 minutes')
                time.sleep(120)
            except Exception as e:
                print('Exception while fetching prices for ', k)
                print('Going to sleep for 2 minutes')
                time.sleep(120)
                continue

    def fetch_brand_price(self, _brand_name):
        url = self.urls[_brand_name]
        self.fetch_price(_brand_name=_brand_name, _url=url)

    def fetch_price(self, _brand_name, _url):
        response = requests.get(
        url=_url, 
        headers=self.headers.get_header(),
        timeout=20, # timeout in 20 seconds in order to avoid hanging/freezing
        )
        soup = BeautifulSoup(response.content, 'html.parser')
        section = soup.find('section', {'class', 'product-row product-row-4-each'})
        rows = section.find_all('div', {'class', 'row'})
        mobile_divs = []
        for row in rows:
            res = row.find_all('div')
            if res:
                mobile_divs += res
        for mobile_detail in mobile_divs:
            try:
                name = mobile_detail.find('h4').text.strip()
                mobile = Mobile.objects.filter(Q(full_name__iexact=name), 
                                               Q(brand__name__iexact=_brand_name))
                # If this mobile is not in out database then discard and go to next mobile
                if not mobile: continue
                else: mobile = mobile[0]
                dl = mobile_detail.find('dl')
                data = dl.find_all('b')
                if len(data) == 2 and 'kr' in data[0].text:
                    price = data[0].text
                    price = (''.join(i for i in price if i.isdigit()))
                    mobile.cash_price = float(price)
                    mobile.save()
                    print('Updated price for ', mobile)
            except AttributeError as e:
                # Divs inside the mobile div are also fetched and they have no name or price field
                continue
            except Exception as e:
                print('Exception while getting mobile price. ', e)
                continue

class ElgigantenSpider:
    def __init__(self):
        self.apple_url = 'https://www.elgiganten.dk/catalog/mobil-gps/dk_mobiltelefoner/mobiltelefoner?SearchParameter=%26%40QueryTerm%3D*%26ContextCategoryUUID%3Dr_KsGQV5iqQAAAFDhNY2st58%26discontinued%3D0%26ManufacturerName%3DApple%26online%3D1%26%40Sort.ViewCount%3D1%26%40Sort.ProductListPrice%3D0&PageSize=12&ProductElementCount=&searchResultTab=Products&CategoryName=dk_mobiltelefoner&CategoryDomainName=store-elgigantenDK-ProductCatalog#filter-sidebar'
        self.headers = HeaderFactory()

    def fetch_price(self):
        response = requests.get(
            url=self.apple_url, 
            headers=header,
            timeout=20, # timeout in 20 seconds in order to avoid hanging/freezing
        )
        soup = BeautifulSoup(response.content, 'html.parser')
        main = soup.find('main', {'class', 'master-main row'})
        search_products = main.find('div', {'class', 'searchProductsInfo'})
        if not search_products:
            search_products = soup.find('div', {'class', 'searchProductsInfo'})
        if not search_products: 
            print('No products found')
            return


# TODO use logging
class GsmarenaMobileSpecSpider:
    def __init__(self):
        self.headers = HeaderFactory()
        self.proxies = None
        # Run main coroutine
        # loop = asyncio.new_event_loop()
        # asyncio.set_event_loop(loop)
        # loop = asyncio.get_event_loop()
        # self.proxies = loop.run_until_complete(get_proxies())
        # self.proxies = asyncio.run(get_proxies())
        # loop.close()
    def fetch_mobile(self, mobile_name, brand_name, url):
        '''Fetch the mobile and its specs from the given url.
        The fetched mobile and specs will be saved in the DB.'''
        if not url or url.strip() == '': return 
        # Check if this mobile already exists. Otherwise create a new mobile
        mobile = Mobile.objects.filter(Q(full_name__iexact=mobile_name), 
                                Q(brand__name__iexact=brand_name))
        # If we have not found mobile with full name and try with the name
        if not mobile:
            mobile = Mobile.objects.filter(Q(name__iexact=mobile_name), 
                                            Q(brand__name__iexact=brand_name))
        if mobile: mobile = mobile[0]
        else:
            brand = MobileBrand.objects.filter(name__iexact=brand_name)
            if brand: brand = brand[0]
            mobile = Mobile.objects.create(
                name=mobile_name, 
                url=url,
                brand = brand,
                )
        header = self.headers.get_header()
        print(f'Sending Request to fetch mobile')
        response = requests.get(
            url=url, 
            headers=header,
            timeout=20, # timeout in 20 seconds in order to avoid hanging/freezing
        )
        soup = BeautifulSoup(response.content, 'html.parser')
        tables = soup.find_all('table')
        rows = []
        for table in tables:
            new_rows = table.find_all('tr')
            if new_rows: rows = rows + new_rows
        if not mobile.image:
            image = self.download_mobile_image(
                soup=soup, 
                mobile=mobile, 
                brand_name=brand_name)
        self.extract_mobile_info(rows, mobile)

    def download_mobile_image(self, soup, mobile, brand_name):
        img_src = soup.find('div', {'class':"specs-photo-main"}).find('a').find('img')['src']
        try:
            if img_src and len(img_src.strip()) > 5:
                response = requests.get(img_src, stream=True, timeout=30).content
                image_file = io.BytesIO(response)
                image = Image.open(image_file)
                # return image
                if image:
                    thumb_io = io.BytesIO()
                    image.save(thumb_io, image.format, quality=95)
                    # TODO if mobile/ OR ANyName/ is not provided in the save method then 
                    # the image is saved to the parent folder i.e. media
                    # mobile.image.save('sony/'+image.filename, ContentFile(thumb_io.getvalue()), save=False)
                    mobile.image.save(brand_name+'/'+image.filename, ContentFile(thumb_io.getvalue()), save=False)
                    mobile.save()
        except Exception as e:
            msg = f'Exception occured while downloading the image: {e}'
            logger.error(msg)

    def fetch_single_specs(self, mobile):
        '''Fetches specs for a single mobile and 
        fails in case of an exception'''
        if not mobile.url: return
        #  or MobileTechnicalSpecification.objects.filter(mobile=mobile): continue
        # proxy = next(proxy_pool)
        header = self.headers.get_header()
        print(f'Sending Request for mobile = {mobile}')
        response = requests.get(
            url=mobile.url, 
            # proxies={"http": proxy, "https": proxy}, 
            headers=header,
            timeout=20, # timeout in 20 seconds in order to avoid hanging/freezing
        )
        soup = BeautifulSoup(response.content, 'html.parser')
        tables = soup.find_all('table')
        rows = []
        for table in tables:
            new_rows = table.find_all('tr')
            if new_rows: rows = rows + new_rows
        self.extract_mobile_info(rows, mobile)

    # @shared_task
    def fetch_mobile_specs(self, brand_name):
        """Get url links for all mobile in he given brand.
        If there is a link given for the mobile, fetch its
        data."""
        brand = None
        try:
            brand = MobileBrand.objects.get(name__icontains=brand_name)
        except ObjectDoesNotExist as e:
            print(f'Brand with the given name {band_name} not found: ', e)
            return None
        # mobiles = Mobile.objects.filter(brand=brand)
        # mobiles = Mobile.objects.filter(brand=brand).order_by(F('launch_date').desc(nulls_last=True))
        # mobiles = Mobile.objects.filter(brand__name=brand_name)[:100]
        mobiles = Mobile.objects.filter(brand=brand, technical_specs__isnull=True)[:100]
        # mobiles = mobiles.filter(technical_specs=None)
        # self.proxies = ProxyFactory().get_proxies(5)
        # proxy_pool = cycle(self.proxies)
        for index, mobile in enumerate(mobiles):
            try:
                # TODO check if specs data is null by using
                # MobileTechnicalSpecification.objects.filter(data__isnull=True)
                if not mobile.url: continue
                #  or MobileTechnicalSpecification.objects.filter(mobile=mobile): continue
                # proxy = next(proxy_pool)
                header = self.headers.get_header()
                print(f'Remaining {len(mobiles)-index} Sending Request # {index} for mobile = {mobile}')
                response = requests.get(
                    url=mobile.url, 
                    # proxies={"http": proxy, "https": proxy}, 
                    headers=header,
                    timeout=20, # timeout in 20 seconds in order to avoid hanging/freezing
                )
                soup = BeautifulSoup(response.content, 'html.parser')
                tables = soup.find_all('table')
                rows = []
                for table in tables:
                    new_rows = table.find_all('tr')
                    if new_rows: rows = rows + new_rows
                self.extract_mobile_info(rows, mobile)
                # if index !=0 and index % 20 == 0:
                    # after every 20 requests update the proxy list 
                    # in order to avoid dead proxies
                    # self.proxies = ProxyFactory().get_proxies(5)
                    # print('Got new proxy pool')
                    # proxy_pool = cycle(self.proxies)
                if index % 3 == 0:
                    time.sleep(25)
                else:
                    time.sleep(15)
                print('Went to sleep')
            except ReadTimeout as rt:
                print('Read time out. Trying again')
                continue
            except HTTPSConnection as nce:
                print('Unable to establish connection!', nce)
                return
            except Exception as e:
                print(f'Exception occured while fetching specs for {mobile}', e)
                # with open('to_fetch_motorola.txt', 'a') as f:
                #     f.write(str(mobile))
                #     f.write('\n')
                continue
                # if index !=0 and index % 20 == 0:
                    # after every 20 requests update the proxy list 
                    # in order to avoid dead proxies
                    # self.proxies = ProxyFactory().get_proxies(5)
                    # print('Got new proxy pool')
                    # proxy_pool = cycle(self.proxies)


    def extract_mobile_info(self, rows, mobile):
        """Extract the data from the webpage 
        and put it in a dictionary"""
        # isinstance(rows, list)
        if len(rows) == 0:
            print(f'Got no data for {mobile.name}')
            return None
        info_dict = {}
        th_title = ''
        for row in rows:
            try:
                th = row.find('th')
                if th: th_title = th.text.strip().lower()
                tds = row.find_all('td')
                if len(tds) < 2: continue
                t = tds[0]
                i = tds[1]
                key = th_title + "-" + t.find('a').text.strip().lower()
                info = i.text.strip()
                info_dict[key] = info
            except AttributeError as e:
                # a row is empty and accessing its text generates NoneType. Skip it
                continue
            except Exception as e:
                print('Exception while extracting ', mobile)
                print(e)
                continue
        self.save_mobile_info(info_dict, mobile)
        self.save_camera_specs(info_dict, mobile)
        self.save_variations(info_dict, mobile)

    def save_mobile_info(self, data_dict, mobile):
        old_specs = MobileTechnicalSpecification.objects.filter(mobile=mobile)
        mob_specs = MobileTechnicalSpecification.objects.create(mobile=mobile)
        technology = data_dict.get('network-technology')
        if technology and '5g' in technology.lower():
            mob_specs.five_g = True
        WLAN = data_dict.get('comms-wlan')
        if WLAN:
            mob_specs.WLAN = WLAN.strip()
            if 'wi-fi' in WLAN.lower():
                mob_specs.WiFi = True
        sim = data_dict.get('body-sim')
        if sim and 'dual sim' in sim.lower():
            mob_specs.dual_sim = True
        dimensions = data_dict.get('body-dimensions')
        if dimensions:
            mob_specs.dimensions = dimensions.strip()
        weight = data_dict.get('body-weight')
        if weight:
            mob_specs.weight = weight.strip()
        screen_type = data_dict.get('display-type')
        if screen_type:
            mob_specs.screen_type = screen_type.strip()
        screen_size = data_dict.get('display-size')
        if screen_size:
            mob_specs.screen_size = screen_size.strip()
        screen_resolution = data_dict.get('display-resolution')
        if screen_resolution:
            mob_specs.screen_resolution = screen_resolution.strip()
        internal_storage = data_dict.get('memory-internal')
        if internal_storage and len(internal_storage.strip()) > 0:
            mob_specs.internal_storage = internal_storage.strip()
        external_storage = data_dict.get('memory-card slot')
        if external_storage and len(external_storage.strip()) > 0:
            mob_specs.external_storage = external_storage.strip()
        bluetooth = data_dict.get('comms-bluetooth')
        if bluetooth:
            mob_specs.bluetooth = bluetooth
        nfc = data_dict.get('comms-nfc')
        if nfc and 'yes' in nfc.lower():
            mob_specs.NFC = True
        usb = data_dict.get('comms-usb')
        if usb and len(usb.strip()) > 0:
            mob_specs.USB = usb.strip()
        battery_type = data_dict.get('battery-type')
        if battery_type and len(battery_type.strip()) > 0:
            mob_specs.battery_type = battery_type.strip()
        wireless_charging = data_dict.get('battery-charging')
        if wireless_charging and 'wireless' in wireless_charging:
            mob_specs.wireless_charging = 'JA tilgængelig'
        fast_charging = data_dict.get('battery-charging')
        if fast_charging:
            mob_specs.fast_charging = fast_charging
        chipset = data_dict.get('platform-chipset')
        if chipset and len(chipset) > 0:
            mob_specs.chipset = chipset
        operating_system = data_dict.get('platform-os')
        if operating_system and len(operating_system) > 0:
            mob_specs.operating_system = operating_system
        ram = data_dict.get('memory-internal')
        if ram and len(ram.strip()) > 0:
            try:
                extracted_ram = ram.strip().split(',')[0].split(" ", 1)[1]
                mob_specs.ram = extracted_ram
            except:
                mob_specs.ram = None
        launch = ''
        announced = data_dict.get('launch-announced')
        if announced:
            launch = 'Announced: ' + announced.strip()
            try:
                dt = parser.parse(announced.strip())
                mobile.launch_date = dt
                mobile.save()
            except:
                print('Unable to save launch date for: ', mobile)
                update_mobile_launch_date(launch_date=announced.strip(), mobile=mobile)

        status = data_dict.get('launch-status')
        if status:
            launch = launch  + " - Status " + status.strip()
        if launch:
            mob_specs.launch = launch
        if old_specs:old_specs.delete()
        mob_specs.save()
        print('Saved specs for ', mobile)

    def save_variations(self, data_dict, mobile):
        # Save the variations for color and memory. 
        variation, _ = Variation.objects.get_or_create(name='colour', mobile=mobile)
        color = data_dict.get('misc-colors')
        if color:
            colors = color.split(',')
            for col in colors:
                try:
                    # Avoid creating the save variation with lower / upper case value
                    mv = MobileVariation.objects.filter(variation=variation, 
                                                                value__iexact=col.strip())
                    if mv and len(mv) > 0: continue
                    mobileVariation = MobileVariation.objects.create(variation=variation, 
                                                                value=col.strip())
                except:
                    # MobileVariation already exists. So continue
                    continue
        variation, _ = Variation.objects.get_or_create(name='memory', mobile=mobile)
        memory = data_dict.get('memory-internal')
        if memory:
            memories = memory.split(',')
            for mem in memories:
                try:
                    mv = MobileVariation.objects.filter(variation=variation, 
                                                                value__iexact=mem.strip())
                    if mv and len(mv) > 0: continue
                    mobileVariation = MobileVariation.objects.create(variation=variation, 
                                                                value=mem.strip())
                except:
                    continue
        print('Saved Variation for ', mobile)

    def save_camera_specs(self, data_dict, mobile):
        old_cam_specs = MobileCameraSpecification.objects.filter(mobile=mobile)
        cam_specs = MobileCameraSpecification.objects.create(mobile=mobile)
        single = data_dict.get('main camera-single')
        features = data_dict.get('main camera-features')
        if features and len(features.strip()) > 0: 
            features = features.strip()
        if single and len(single.strip()) > 0:
            cam_specs.rear_cam_lenses = 1
            rear_mp = single.strip() 
            if features:
                rear_mp = rear_mp + '- Features: ' + features
            cam_specs.rear_cam_megapixel = rear_mp[:254]
        elif data_dict.get('main camera-double'):
            cam_specs.rear_cam_lenses = 2
            rear_mp = data_dict.get('main camera-double').strip() 
            if features:
                rear_mp = rear_mp + '- Features: ' + features
            cam_specs.rear_cam_megapixel = rear_mp[:254]
        elif data_dict.get('main camera-triple'):
            cam_specs.rear_cam_lenses = 3
            rear_mp = data_dict.get('main camera-triple').strip() 
            if features:
                rear_mp = rear_mp + '- Features: ' + features
            cam_specs.rear_cam_megapixel = rear_mp[:254]
        elif data_dict.get('main camera-quad'):
            cam_specs.rear_cam_lenses = 4
            rear_mp = data_dict.get('main camera-quad').strip()
            if features:
                rear_mp = rear_mp + '- Features: ' + features
            cam_specs.rear_cam_megapixel = rear_mp[:254]
        rear_cam_video_resolution = data_dict.get('main camera-video')
        if rear_cam_video_resolution:
            cam_specs.rear_cam_video_resolution = rear_cam_video_resolution.strip()[:50]
        front_single = data_dict.get('selfie camera-single')
        front_features = data_dict.get('selfie camera-features')
        if front_features and len(front_features.strip()) > 0: front_features = front_features.strip()
        if front_single and len(front_single.strip()) > 0:
            cam_specs.front_cam_lenses = 1
            front_mp = front_single.strip()
            if front_features:
                front_mp = front_mp + '- Features: ' + front_features
            cam_specs.front_cam_megapixel = front_mp[:254]
        elif data_dict.get('selfie camera-double'):
            cam_specs.front_cam_lenses = 2
            front_mp = data_dict.get('selfie camera-double').strip()
            if front_features:
                front_mp = front_mp + '- Features: ' + front_features
            cam_specs.front_cam_megapixel = front_mp[:254]
        front_cam_video_resolution = data_dict.get('selfie camera-video')
        if front_cam_video_resolution:
            cam_specs.front_cam_video_resolution = front_cam_video_resolution.strip()[:50]
        if old_cam_specs: old_cam_specs.delete()
        cam_specs.save()
        print('Saved Camera Specs for ', mobile)


class GadgetsMobileSpecSpider:
    def __init__(self, brand_name_):
        # self.headers = {'User-agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:61.0) Gecko/20100101 Firefox/61.0'}
        self.headers = HeaderFactory()
        self.brand_name = brand_name_
        self.proxies = ProxyFactory().get_proxies(5)

    def fetch_mobile_specs(self):
        brand = MobileBrand.objects.get(name__iexact=self.brand_name)
        # updated_urls = Mobile.objects.filter(Q(brand=brand),Q(url__icontains='gadgets'))
        # Read the file 
        # with open('to_fetch_mobile_specs.txt', 'r') as f:
        #     lines = f.readlines()
        proxy_pool = cycle(self.proxies)
        # check the index and change sleep time to avoid regular intervals
        for index, l in enumerate(lines):
            try:
                name = l.strip('\n')
                qs = Mobile.objects.filter(
                    Q(full_name=name),
                    Q(brand=brand),
                    Q(url__icontains='gadgets'))
                mobile = qs[0]
                # we are scraping for MobileTechnicalSpecs, 
                # if the mobile aleady has the specs then continue to the next 
                if MobileTechnicalSpecification.objects.filter(mobile=mobile):
                    # unrequired check. All mobiles have urls to this point
                    continue
                proxy = next(proxy_pool)
                header = self.headers.get_header()
                print(f'Sending Request # {index} for mobile = {mobile} with proxy = {proxy} and headers = \n {header}')
                response = requests.get(
                    url=mobile.url, 
                    proxies={"http": proxy, "https": proxy}, 
                    headers=header,
                )
                soup = BeautifulSoup(response.content, 'html.parser')
                divs = soup.find_all('div', {'class', '_gry-bg _spctbl _ovfhide'})
                tables = []
                for d in divs:
                    tables.append(d.find('table'))
                rows = []
                for table in tables:
                    rows = rows + table.find_all('tr')
                data_dict = {}
                for row in rows:
                    tds = row.find_all('td')
                    if len(tds) > 1:
                        title = tds[0]
                        info = tds[1]
                        if title and info:
                            data_dict[title.text.strip()] = info.text.strip()
                self.save_mob_specs(data_dict, mobile)
                print('Saved specifications for: ', mobile)
                self.save_camera_specs(data_dict, mobile)
                print('Saved CAMERA specifications for: ', mobile)
                self.save_variations(data_dict, mobile)
                print('Saved VARIATIONS for: ', mobile)
                if index !=0 and index % 10 == 0:
                    # after every 10 requests update the proxy list 
                    # in order to avoid dead proxies
                    self.proxies = ProxyFactory().get_proxies(5)
                    print('Got new proxy pool')
                    proxy_pool = cycle(self.proxies)
                if index % 3 == 0:
                    time.sleep(20)
                else:
                    time.sleep(10)
                print('Went to sleep')
            except Exception as e:
                # Save the unsaved mobile in a file for later retry
                # with open('to_fetch_mobile_specs.txt', 'a') as f:
                #     f.write(str(mobile))
                #     f.write('\n')
                print(f'Exception occured while fetching specs for {mobile}', e)
                continue

    def save_variations(self, data_dict, mobile):
        # mobile = Mobile.objects.get(name__iexact='iPhone 12 Pro Max')
        variation, _ = Variation.objects.get_or_create(name='colour', mobile=mobile)
        color = data_dict.get('Colours')
        if color:
            colors = color.split(',')
            for col in colors:
                mobileVariation = MobileVariation.objects.create(variation=variation, 
                                                                value=col.strip())

    def save_camera_specs(self, data_dict, mobile):
        # mobile = Mobile.objects.get(name__iexact='iPhone 12 Pro Max')
        cam_specs = MobileCameraSpecification.objects.create(mobile=mobile)
        rear_cam_megapixel = data_dict.get('Rear camera')
        if rear_cam_megapixel and len(rear_cam_megapixel.strip()) > 0:
            cam_specs.rear_cam_megapixel = rear_cam_megapixel
        front_cam_megapixel = data_dict.get('Front camera')
        if front_cam_megapixel and len(front_cam_megapixel.strip()) > 0:
            cam_specs.front_cam_megapixel = front_cam_megapixel
        cam_specs.save()

    def save_mob_specs(self, data_dict, mobile):
        # mobile = Mobile.objects.get(name__iexact='iPhone 12 Pro Max')
        mob_specs = MobileTechnicalSpecification.objects.create(mobile=mobile)
        three_g = data_dict.get('3G') 
        if three_g and 'Yes' in three_g:
            mob_specs.three_g = True
        four_g = data_dict.get('4G/ LTE')
        if four_g and 'Yes' in four_g:
            mob_specs.four_g = True
        five_g = data_dict.get('5G')
        if five_g and 'Yes' in five_g:
            mob_specs.five_g = True
        WiFi = data_dict.get('Wi-Fi')
        if WiFi and 'Yes' in WiFi:
            mob_specs.WiFi = True
        dual_sim = data_dict.get('Number of SIMs')
        if dual_sim and '2' in dual_sim:
            mob_specs.dual_sim = True
        dimensions = data_dict.get('Dimensions (mm)')
        if dimensions and len(dimensions.strip()) > 0:
            mob_specs.dimensions = dimensions
        weight = data_dict.get('Weight (g)')
        if weight and len(weight.strip()) > 0:
            mob_specs.weight = weight
        screen_size = data_dict.get('Screen size (inches)')
        if screen_size and len(screen_size.strip()) > 0:
            mob_specs.screen_size = screen_size
        screen_resolution = data_dict.get('Resolution')
        if screen_resolution and len(screen_resolution.strip()) > 0:
            mob_specs.screen_resolution = screen_resolution
        ip_certification = data_dict.get('IP rating')
        if ip_certification and len(ip_certification.strip()) > 0:
            mob_specs.ip_certification = ip_certification
        internal_storage = data_dict.get('Internal storage')
        if internal_storage and len(internal_storage.strip()) > 0:
            mob_specs.internal_storage = internal_storage
        external_storage = data_dict.get('Expandable storage')
        if external_storage and len(external_storage.strip()) > 0:
            mob_specs.external_storage = external_storage
        bluetooth = data_dict.get('Bluetooth')
        if bluetooth and len(bluetooth.strip()) > 0:
            mob_specs.bluetooth = bluetooth
        NFC = data_dict.get('NFC')
        if NFC and 'Yes' in NFC.strip():
            mob_specs.NFC = True
        USB = data_dict.get('USB OTG')
        if not USB:
            USB = data_dict.get('USB Type-C')
        if USB and len(USB.strip()) > 0:
            mob_specs.USB = USB
        wireless_charging = data_dict.get('Wireless charging')
        if wireless_charging and len(wireless_charging.strip()) > 0:
            mob_specs.wireless_charging = wireless_charging
        fast_charging = data_dict.get('Fast charging')
        if fast_charging and len(fast_charging.strip()) > 0:
            mob_specs.fast_charging = fast_charging
        chipset = ""
        processor = data_dict.get('Processor')
        processor_make = data_dict.get('Processor make')
        if processor: 
            chipset = chipset + processor.strip()
        if processor_make:
            chipset = chipset + " " +processor_make.strip() 
        if len(chipset.strip()) > 0:
            mob_specs.chipset = chipset
        operating_system = data_dict.get('Operating system')
        if operating_system and len(operating_system.strip()) > 0:
            mob_specs.operating_system = operating_system
        ram = data_dict.get('RAM')
        if ram and len(ram.strip()) > 0:
            mob_specs.ram = ram
        mob_specs.save()

# ////////////////////////////////////////////
# mobile
# two_g
# three_g
# four_g
# five_g    - Network 	Technology
# WiFi      - Comms 	WLAN
# dual_sim  - BODY SIM
# dimensions - BODY Dimensions
# weight     - BODY Weight
# screen_type - DISPLAY Type
# screen_size - DISPLAY Size
# screen_resolution - DISPLAY Resolution
# ip_certification
# internal_storage  - Memory 	Internal
# external_storage  - Memory 	Card slot
# WLAN              - Comms 	WLAN
# bluetooth         - Comms 	Bluetooth
# NFC               - Comms 	NFC (BooleanField)
# USB               - Comms 	USB
# battery_type      - Battery 	Type
# wireless_charging - Battery Charging (Extract) if there is wireless written then write yes
# fast_charging     - Battery Charging
# chipset           - Platform Chipset
# operating_system  - Platform 	OS
# ram               - Memory 	Internal (extract from this)
# Launch 	Announced + Launch 	Status

# Variation memory and color
# 