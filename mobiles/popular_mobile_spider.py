from abc import ABC, abstractmethod
import asyncio
from bs4 import BeautifulSoup
from django.db.models import Q
import requests

from mobiles.models import Mobile, PopularMobile
from mobiles.utils import HeaderFactory, ProxyFactory

class AbstractPopularMobile(ABC):
    def __init__(self):
        super().__init__()

    def save_popular_mobiles(self, mobile_names_list):
        """Gets a dictionary containing mobile name and 
        brand. Replaces popular mobiles with the new ones"""
        # batchcreate
        mobiles = Mobile.objects.filter(Q(name__in=mobile_names_list) | 
        Q(full_name__in=mobile_names_list))
        # import pdb; pdb.set_trace()
        for mobile in mobiles:
            try:
                PopularMobile.objects.create(mobile=mobile)
                print('Created popular mobile: ', mobile)
            except Exception as e:
                print('Exception while saving popular mobile: ', e)
                continue

    @abstractmethod
    def fetch_popular_mobiles(self):
        print('Fetching popular mobiles')

class MobilkundenSpider(AbstractPopularMobile):
    def __init__(self):
        self.url = 'https://mobilkunden.dk/populaere-telefoner'
        self.headers = HeaderFactory()
        super().__init__()

    def get_response(self, header, proxy):
        response = requests.get(
            url=self.url, 
            proxies={"http": proxy, "https": proxy}, 
            headers=header,
            timeout=20, # timeout in 20 seconds in order to avoid hanging/freezing
        )
        return response

    def fetch_popular_mobiles(self):
        # proxies = asyncio.run(ProxyFactory().get_valid_proxies())
        # Get two proxies to make two requests.
        proxies = ProxyFactory().get_proxies(number_of_proxies=2)
        popular_mobiles = []
        header = self.headers.get_header()
        response = None
        try:
            response = self.get_response(header, proxies.pop())
        except Exception as e:
            print('Exception occured while sending request for popular mobiles: ', e)
            # Send second request in case of timeout exception 
            response = self.get_response(header, proxies.pop())
        soup = BeautifulSoup(response.content, 'html.parser')
        div_phone_list = soup.find('div', {'class', 'mobilkunden-phone-list'})
        div_phones = None
        if div_phone_list:
            div_phones = div_phone_list.find_all('div', {'class', 'mobilkunden-phone clearfix'})
        if not div_phones:
            soup.find_all('div', {'class', 'mobilkunden-phone clearfix'})
        for phone in div_phones:
            mobile_name = None
            h2 = phone.find('h2')
            if h2 and len(h2.text.strip()) > 0:
                mobile_name = h2.text.strip()
            else:
                # if we cannot find name of mobile then proceede to the next mobile
                continue
            popular_mobiles.append(mobile_name)
        self.save_popular_mobiles(popular_mobiles)
