import aiohttp
import asyncio
from collections import OrderedDict
from lxml.html import fromstring
import random 
import requests

from .models import MobileBrand as new_brand
from mobiles.models import Mobile
from dateutil import parser

def update_launch_date(brand_name):
    'Update the Mobile launch date where None'
    # import pdb; pdb.set_trace()
    mobiles = Mobile.objects.filter(brand__name=brand_name) .filter(launch_date=None)
    for ph in mobiles:
        try:
            specs = ph.technical_specs.all()
            launch = None
            if specs:
                launch = specs[0].launch
                launch = launch.split(' ',1)[1]
                update_mobile_launch_date(mobile=ph, launch_date=launch)
                # dt = parser.parse(launch.strip())
                # ph.launch_date = dt
                # ph.save()
        except Exception as e:
            print('unable to update date for ', ph)
            print('Launch Date: ', launch)
            print('Exception: ', e)

def update_mobile_launch_date(mobile, launch_date):
    'Update the Mobile launch date where None'
    launch = None
    try:
        l1 = launch_date.split(' ',1)[0]
        if l1: 
            launch = parser.parse(l1.strip())
        l2 = launch_date.split(' ')[1]
        if l2:
            launch = parser.parse(str(l1+l2))
        if launch:
            mobile.launch_date = launch
            mobile.save()
            print(f'Saved {mobile} launch Date:', launch)
    except:
        if launch:
            mobile.launch_date = launch
            mobile.save()
            print(f'Saved {mobile} launch Date:', launch)
        else:
            print('Unable to update launch date for ', mobile)
            print('Launch Date Provided: ', launch_date)


def bulk_copy_table_data():
    queryset = core_mobile.objects.all().values('name', 'full_name', 'brand', 'cash_price', 'slug')
    # new_objects = [new_mobile(**values) for values in queryset]
    # new_mobile.objects.bulk_create(new_objects)
    for values in queryset:
        brand = MobileBrand.objects.get(id=values['brand'])
        values['brand'] = brand
        new_mobile.objects.create(**values)

def bulk_copy_brand_data():
    queryset = core_brand.objects.all().values()
    new_objects = [new_brand(**values) for values in queryset]
    new_brand.objects.bulk_create(new_objects)

class ProxyFactory:
    # TODO read again https://medium.com/@esfoobar/python-asyncio-for-beginners-c181ab226598
    # def get_proxies(self, number_of_proxies=10):
    #     """Returns max 10 free https proxies by scraping 
    #     free-proxy website.
    #     @arg number_of_proxies to be returned"""
    #     try:
    #         if number_of_proxies > 10: number_of_proxies = 10
    #         url = 'https://free-proxy-list.net/'
    #         response = requests.get(url)
    #         response_text = response.text
    #         parser = fromstring(response_text)
    #         proxies = set()
    #         # tasks = []
    #         for i in parser.xpath('//tbody/tr'):
    #             if len(proxies) >= number_of_proxies:
    #                 break
    #             if i.xpath('.//td[7][contains(text(),"yes")]'):
    #                 #Grabbing IP and corresponding PORT
    #                 proxy = ":".join([i.xpath('.//td[1]/text()')[0], i.xpath('.//td[2]/text()')[0]])
    #                 # tasks.append(asyncio.create_task(self.is_valid_proxy(proxy)))
    #                 # await tasks
    #                 proxies.add(proxy)
    #         return proxies
    #     except Exception as e:
    #         print('Exception while fetching proxies from free-proxy: ', e)
    #         return None

    # async def is_valid_proxy(self, proxy):
    #     """Check the validity of a proxy by sending 
    #     get request to google using the given proxy."""
    #     try:
    #         async with aiohttp.ClientSession() as session:
    #             session.proxies={"http": proxy, "https": proxy}
    #             async with session.get('http://8.8.4.4', 
    #             timeout=10) as response:
    #                 status_code = await response.status_code
    #         # response = await requests.get("https://www.google.com/", proxies={"http": proxy, "https": proxy}, timeout=10)
    #         # if await response.status_code == requests.codes.ok:
    #                 print('status_code: ', status_code)
    #                 if status_code == requests.codes.ok:
    #                     print('got a valid proxy')
    #                     return True
    #     except Exception as e:
    #         print('Invalid proxy. Exception: ', e)
    #         return False

    # async def get_valid_proxies(self, number_of_proxies=10):
    #     proxies = self.get_proxies(number_of_proxies)
    #     print(len(proxies), proxies)
    #     valid_proxies = []
        # try:
        #     loop = asyncio.new_event_loop()
        #     asyncio.set_event_loop(loop)
        #     print('GOT event loop')
        #     valid_proxies = loop.run_until_complete(asyncio.gather(*[self.is_valid_proxy(proxy) for proxy in proxies]))
        #     loop.close()
        # except:
        #     loop.close()
        # valid_proxies = await asyncio.gather(*[proxy for proxy in proxies if await self.is_valid_proxy(proxy)])
        # valid_proxies = await asyncio.gather(*[self.is_valid_proxy(proxy) for proxy in proxies])
        # for proxy in proxies:
        #     valid_proxies.append(await asyncio.gather(self.is_valid_proxy(proxy)))
    # return valid_proxies
    
    # TODO implement async
    def get_proxies(self, number_of_proxies):
        """Returns max 10 free https proxies by scraping 
        free-proxy website.
        @arg number_of_proxies to be returned"""

        url = 'https://free-proxy-list.net/'
        response = requests.get(url)
        parser = fromstring(response.text)
        proxies = set()
        for i in parser.xpath('//tbody/tr'):
            if len(proxies) >= number_of_proxies:
                break
            if i.xpath('.//td[7][contains(text(),"yes")]'):
                #Grabbing IP and corresponding PORT
                proxy = ":".join([i.xpath('.//td[1]/text()')[0], i.xpath('.//td[2]/text()')[0]])
                # Try to get google.com with the proxy to check if this proxy is ok.
                if self.valid_proxy(proxy):
                    proxies.add(proxy)
        return proxies

    def valid_proxy(self, proxy):
        """Check the validity of a proxy by sending 
        get request to google using this proxy."""
        try:
            t = requests.get("http://8.8.4.4", 
            proxies={"http": proxy, "https": proxy}, 
            timeout=20)
            if t.status_code == requests.codes.ok:
                print('got a valid proxy')
                return True
            else:
                return False
        except Exception as e:
            print('Invalid proxy = ', e)
            return False

class HeaderFactory:
    """Contains a list of headers with updated User-Agents."""
    def __init__(self):
        self.headers_list = [
            {
                'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:83.0) Gecko/20100101 Firefox/83.0',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Referer': 'https://www.google.com/',
                'DNT': '1',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
                'If-Modified-Since': 'Sun, 29 Nov 2020 21:16:58 GMT',
                'Cache-Control': 'max-age=0',
            },
        # Firefox 83 Mac
            {
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:83.0) Gecko/20100101 Firefox/83.0",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.5",
                'Referer': 'https://www.google.com/',
                "DNT": "1",
                "Connection": "keep-alive",
                "Upgrade-Insecure-Requests": "1"
            },
            # Firefox 83 Windows
            {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:83.0) Gecko/20100101 Firefox/83.0",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.5",
                "Accept-Encoding": "gzip, deflate, br",
                'Referer': 'https://www.google.com/',
                "DNT": "1",
                "Connection": "keep-alive",
                "Upgrade-Insecure-Requests": "1"
            },
            # Chrome 87 Mac
            {
                "Connection": "keep-alive",
                "DNT": "1",
                "Upgrade-Insecure-Requests": "1",
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
                "Sec-Fetch-Site": "none",
                "Sec-Fetch-Mode": "navigate",
                "Sec-Fetch-Dest": "document",
                "Referer": "https://www.google.com/",
                "Accept-Encoding": "gzip, deflate, br",
                "Accept-Language": "en-GB,en-US;q=0.9,en;q=0.8"
            },
            # Chrome 87 Windows 
            {
                "Connection": "keep-alive",
                "Upgrade-Insecure-Requests": "1",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
                "Sec-Fetch-Site": "same-origin",
                "Sec-Fetch-Mode": "navigate",
                "Sec-Fetch-User": "?1",
                "Sec-Fetch-Dest": "document",
                "Referer": "https://www.google.com/",
                "Accept-Encoding": "gzip, deflate, br",
                "Accept-Language": "en-US,en;q=0.9"
            },
        ]
        # Create ordered dict from Headers above
        self.ordered_headers_list = []
        for headers in self.headers_list:
            h = OrderedDict()
            for header,value in headers.items():
                h[header]=value
            self.ordered_headers_list.append(h)

    def get_header(self):
        """Returns a random header."""
        #Pick a random browser headers
        return random.choice(self.headers_list)
