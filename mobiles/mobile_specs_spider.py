from bs4 import BeautifulSoup
from django.core.exceptions import ObjectDoesNotExist
import requests
from .models import (Mobile, MobileBrand, MobileTechnicalSpecification,
                     MobileCameraSpecification, MobileVariation, Variation)


# TODO use logging
class GsmarenaMobileSpecSpider():
    def fetch_data(self, brand_name):
        """Get url links for all mobile in he given brand.
        If there is a link given for the mobile, fetch its
        data."""
        brand = None
        try:
            brand = MobileBrand.objects.get(name__icontains=brand_name)
        except ObjectDoesNotExist as e:
            print(f'Brand with the given name {band_name} not found: ', e)    
            return None
        import pdb; pdb.set_trace()
        mobiles = Mobile.objects.filter(brand=brand)
        for mobile in mobiles:
            if not mobile.url: continue
            headers = {'User-agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:61.0) Gecko/20100101 Firefox/61.0'}
            response = requests.get(url=mobile.url, headers=headers)
            soup = BeautifulSoup(response.content, 'html.parser')
            tables = soup.find_all('table')
            rows = []
            for table in tables:
                new_rows = table.find_all('tr')
                if new_rows: rows = rows + new_rows
            self.extract_mobile_info(rows, mobile)
    
    def extract_mobile_info(self, rows, mobile):
        """Extract the data from the webpage 
        and put it in a dictionary"""
        # isinstance(rows, list) 
        # import pdb; pdb.set_trace()
        if len(rows) == 0:
            return None
        info_dict = {}
        for row in rows:
            try:
                tds = row.find_all('td')
                if len(tds) < 2: continue
                t = tds[0]
                i = tds[1]
                title = t.find('a').text().strip()
                info = i.text().strip()
                info_dict[title] = info
            except Exception as e:
                print('Exception while extracting mobile info for ', mobile)
                print(e)
        self.save_mobile_info(info_dict, mobile)

    def save_mobile_info(self, data_dict, mobile):
        import pdb; pdb.set_trace()
        mob_specs = MobileTechnicalSpecification.objects.create(mobile=mobile)
        technology = data_dict.get('Technology')
        if technology and '5g' in technology:
            mob_specs.five_g = True
        WLAN = data_dict.get('WLAN')
        if WLAN:
            mob_specs.WLAN = WLAN.strip()
            if 'wi-fi' in WLAN.lower():
                mob_specs.WiFi = True
        sim = data_dict.get('SIM')
        if sim and 'dual sim' in sim.lower():
            mob_specs.dual_sim = True
        dimensions = data_dict.get('Dimensions')
        if dimensions:
            mob_specs.dimensions = dimensions.strip()
        weight = data_dict.get('Weight')
        if weight:
            mob_specs.weight = weight.strip()
        screen_size = data_dict.get('Size')
        if screen_size:
            mob_specs.screen_size = screen_size.strip()   
        screen_resolution = data_dict.get('Resolution')
        if screen_resolution:
            mob_specs.screen_resolution = screen_resolution.strip()
        internal_storage = data_dict.get('Internal')
        if internal_storage and len(internal_storage.strip()) > 0:
            mob_specs.internal_storage = internal_storage.strip()
        external_storage = data_dict.get('Card slot')
        if external_storage and len(external_storage.strip()) > 0:
            mob_specs.external_storage = external_storage.strip()
        bluetooth = data_dict.get('Bluetooth')
        if bluetooth:
            mob_specs.bluetooth = bluetooth
        nfc = data_dict.get('NFC')
        if nfc and 'yes' in nfc.lower():
            mob_specs.NFC = True
        usb = data_dict.get('USB')
        if usb and len(usb.strip()) > 0:
            mob_specs.USB = usb.strip()
        mob_specs.save()


class GadgetsMobileSpecSpider:
    def __init__(self):
        self.headers = {'User-agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:61.0) Gecko/20100101 Firefox/61.0'}
        self.iphone12pro_url = 'https://gadgets.ndtv.com/apple-iphone-761'
        self.mobile_name = 'iPhone'
    
    def fetch_mob_specs(self):
        response = requests.get(url=self.iphone12pro_url, headers=self.headers)
        soup = BeautifulSoup(response.content, 'html.parser')
        # from django.core.files import File
        # with open('iphone12protext.txt', 'r') as fl:
            # soup = BeautifulSoup(fl, 'html.parser')
        # with open('iphone12protext.txt', 'w') as fl:
        #     txtf = File(fl)
        #     txtf.write(soup.text)
        divs = soup.find_all('div', {'class', '_gry-bg _spctbl _ovfhide'})
        # tables = [d.find('table') for d in divs]
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
        mobile = Mobile.objects.get(name__iexact=self.mobile_name)
        self.save_mob_specs(data_dict, mobile)
        self.save_camera_specs(data_dict, mobile)
        self.save_variations(data_dict, mobile)

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
        
#????????????????????????????????????????????????????????????????/
    # mobile                      = models.ForeignKey("Mobile", 
    #                               on_delete=models.CASCADE)
    # two_g                       = models.BooleanField(blank=True, null=True)
    # three_g                     = models.BooleanField(blank=True, null=True) 
    # four_g                      = models.BooleanField(blank=True, null=True)
    # five_g                      = models.BooleanField(blank=True, null=True)
    # WiFi                        = models.BooleanField(blank=True, null=True)
    # dual_sim                    = models.BooleanField(blank=True, null=True)
    # dimensions                  = models.CharField(_("Dimensions"), 
    #                               max_length=50, blank=True, null=True)
    # weight                      = models.CharField(_("Weight"), max_length=50, 
    #                                 blank=True, null=True)
    # screen_type                 = models.CharField(_("Screen Type"), 
    #                               max_length=50, blank=True, null=True)
    # screen_size                 = models.CharField(_("Screen Size"), 
    #                               max_length=50, blank=True, null=True)
    # screen_resolution           = models.CharField(_("Screen Resolution"), 
    #                               max_length=50, blank=True, null=True)
    # ip_certification            = models.CharField(_("IP Certification"), 
    #                               max_length=50, blank=True, null=True)
    # internal_storage            = models.CharField(_("Internal Storage"), 
    #                               max_length=50, blank=True, null=True)
    # external_storage            = models.CharField(_("External Storage"), 
    #                               max_length=50, blank=True, null=True)
    # WLAN                        = models.CharField(_("WLAN"), 
    #                               max_length=50, blank=True, null=True)
    # bluetooth                   = models.CharField(_("Bluetooth"), 
    #                               max_length=50, blank=True, null=True)
    # NFC                         = models.BooleanField(default=True)
    # USB                         = models.CharField(_("USB"), 
    #                               max_length=50, blank=True, null=True)
    # wireless_charging           = models.CharField(_("Wireless Charging"), 
    #                               max_length=50, blank=True, null=True)
    # fast_charging               = models.CharField(_("Fast Charging"), 
    #                               max_length=50, blank=True, null=True)
    # chipset                     = models.CharField(_("chipset"), 
    #                               max_length=50, blank=True, null=True)
    # operating_system              = models.CharField(_("Control System"), 
    #                               max_length=50, blank=True, null=True)
    # ram                         = models.CharField(_("RAM"), 
    #                               max_length=50, blank=True, null=True)

# ////////////////////////////////////////////
# two_g
# three_g
# four_g
# taleVoLTE
# screen_type TODO
# ip_certification
# wireless_charging
# fast_charging
# chipset
# operating_system
# ram
