from bs4 import BeautifulSoup
from celery import shared_task
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q
import requests
import random 
import time
from .models import (Mobile, MobileBrand, MobileTechnicalSpecification,
                     MobileCameraSpecification, MobileVariation, Variation)
from itertools import cycle


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
        # import pdb; pdb.set_trace()
        mobiles = Mobile.objects.filter(brand=brand)
        self.proxies = get_proxies()
        proxy_pool = cycle(self.proxies)
        for index, mobile in enumerate(mobiles):
            try:
                # TODO check if specs data is null by using
                # MobileTechnicalSpecification.objects.filter(data__isnull=True)
                if not mobile.url or MobileTechnicalSpecification.objects.filter(mobile=mobile): continue
                proxy = next(proxy_pool)
                header = self.headers.get_header()
                print(f'Remaining {len(mobiles)-index} Sending Request # {index} for mobile = {mobile} with proxy = {proxy} and headers = \n {header}')
                response = requests.get(
                    url=mobile.url, 
                    proxies={"http": proxy, "https": proxy}, 
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
                if index !=0 and index % 20 == 0:
                    # after every 10 requests update the proxy list 
                    # in order to avoid dead proxies
                    self.proxies = get_proxies()
                    print('Got new proxy pool')
                    proxy_pool = cycle(self.proxies)
                if index % 3 == 0:
                    time.sleep(20)
                else:
                    time.sleep(10)
                print('Went to sleep')
            except Exception as e:                
                print(f'Exception occured while fetching specs for {mobile}', e)
                with open('to_fetch_motorola.txt', 'a') as f:
                    f.write(str(mobile))
                    f.write('\n')
                continue
                if index !=0 and index % 20 == 0:
                    # after every 10 requests update the proxy list 
                    # in order to avoid dead proxies
                    self.proxies = get_proxies()
                    print('Got new proxy pool')
                    proxy_pool = cycle(self.proxies)


    def extract_mobile_info(self, rows, mobile):
        """Extract the data from the webpage 
        and put it in a dictionary"""
        # isinstance(rows, list)
        # import pdb; pdb.set_trace()
        if len(rows) == 0:
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
            except Exception as e:
                print('Exception while extracting ', mobile)
                print(e)
                continue
        self.save_mobile_info(info_dict, mobile)
        self.save_camera_specs(info_dict, mobile)
        self.save_variations(info_dict, mobile)

    def save_mobile_info(self, data_dict, mobile):
        # import pdb; pdb.set_trace()
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
        status = data_dict.get('launch-status')
        if status:
            mob_specs.launch = launch  + " - Status " + status.strip()

        mob_specs.save()
        print('Saved specs for ', mobile)

    def save_variations(self, data_dict, mobile):
        # import pdb; pdb.set_trace()
        # Save the variations for color and memory
        variation, _ = Variation.objects.get_or_create(name='colour', mobile=mobile)
        color = data_dict.get('misc-colors')
        if color:
            colors = color.split(',')
            for col in colors:
                mobileVariation = MobileVariation.objects.create(variation=variation, 
                                                                value=col.strip())
        variation, _ = Variation.objects.get_or_create(name='memory', mobile=mobile)
        memory = data_dict.get('memory-internal')
        if memory:
            memories = memory.split(',')
            for mem in memories:
                mobileVariation = MobileVariation.objects.create(variation=variation, 
                                                                value=mem.strip())
        print('Saved Variation for ', mobile)

    def save_camera_specs(self, data_dict, mobile):
        # import pdb; pdb.set_trace()

        cam_specs = MobileCameraSpecification.objects.create(mobile=mobile)
        single = data_dict.get('main camera-single')
        features = data_dict.get('main camera-features')
        if features and len(features.strip()) > 0: 
            features = features.strip()
        if single and len(single.strip()) > 0:
            cam_specs.rear_cam_lenses = 1
            # TODO check if the len > 255 strip [:254]
            rear_mp = single.strip() 
            if features:
                rear_mp = rear_mp + '- Features: ' + features
            cam_specs.rear_cam_megapixel = rear_mp[:254]
        elif data_dict.get('main camera-double'):
            cam_specs.rear_cam_lenses = 2
            # TODO check if the len > 255 strip [:254]
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
            # TODO check if the len > 255 strip [:254]
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
            # TODO check if the len > 255 strip [:254]
            front_mp = front_single.strip()
            if front_features:
                front_mp = front_mp + '- Features: ' + front_features
            cam_specs.front_cam_megapixel = front_mp[:254]
            # cam_specs.front_cam_megapixel = front_single.strip() + '- Features: ' + front_features
        elif data_dict.get('selfie camera-double'):
            cam_specs.front_cam_lenses = 2
            # TODO check if the len > 255 strip [:254]
            front_mp = data_dict.get('selfie camera-double').strip()
            if front_features:
                front_mp = front_mp + '- Features: ' + front_features
            cam_specs.front_cam_megapixel = front_mp[:254]
        front_cam_video_resolution = data_dict.get('selfie camera-video')
        if front_cam_video_resolution:
            cam_specs.front_cam_video_resolution = front_cam_video_resolution.strip()[:50]
        cam_specs.save()
        print('Saved Camera Specs for ', mobile)


class GadgetsMobileSpecSpider:
    def __init__(self, brand_name_):
        # self.headers = {'User-agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:61.0) Gecko/20100101 Firefox/61.0'}
        self.headers = HeaderFactory()
        self.brand_name = brand_name_
        self.proxies = get_proxies()

    def fetch_mobile_specs(self):
        brand = MobileBrand.objects.get(name__iexact=self.brand_name)
        # updated_urls = Mobile.objects.filter(Q(brand=brand),Q(url__icontains='gadgets'))
        # import pdb; pdb.set_trace()
        # Read the file 
        with open('to_fetch_mobile_specs.txt', 'r') as f:
            lines = f.readlines()
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
                    self.proxies = get_proxies()
                    print('Got new proxy pool')
                    proxy_pool = cycle(self.proxies)
                if index % 3 == 0:
                    time.sleep(20)
                else:
                    time.sleep(10)
                print('Went to sleep')
            except Exception as e:
                # Save the unsaved mobile in a file for later retry
                with open('to_fetch_mobile_specs.txt', 'a') as f:
                    f.write(str(mobile))
                    f.write('\n')
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