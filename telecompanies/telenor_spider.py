from bs4 import BeautifulSoup
import requests

from .models import Offer
from core.models import Mobile, TelecomCompany


class TelenorSpider:
    def __init__(self):
        self.headers = {'User-agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:61.0) Gecko/20100101 Firefox/61.0'}
        self.telenor_tilbud_url = 'https://www.telenor.dk/shop/mobiler/campaignoffer/'
        self.mobile_urls = [
            'https://www.telenor.dk/shop/mobil/apple/apple-iphone-12-pro-max-128gb-graphite/?subscriptionId=11942872',
            'https://www.telenor.dk/shop/mobil/apple/apple-iphone-12-mini-64gb-black/?subscriptionId=11942872',
            'https://www.telenor.dk/shop/mobil/apple/apple-iphone-se-64gb-black/?subscriptionId=11462072&cycleCount=none',
            'https://www.telenor.dk/shop/mobil/apple/apple-iphone-12-128gb-black/?subscriptionId=11942872',
            'https://www.telenor.dk/shop/mobil/apple/apple-iphone-11-pro-space-grey-64gb/?subscriptionId=11942872',
            'https://www.telenor.dk/shop/mobil/apple/apple-iphone-11-black-64gb/?subscriptionId=11942872',
            'https://www.telenor.dk/shop/mobil/apple/apple-iphone-12-pro-128gb-graphite/?subscriptionId=11942872',
            'https://www.telenor.dk/shop/mobil/apple/apple-iphone-7-32gb-sort/?subscriptionId=11462072',
            'https://www.telenor.dk/shop/mobil/apple/apple-iphone-xr-black-64gb/?subscriptionId=11942872',
            'https://www.telenor.dk/shop/mobil/apple/apple-iphone-xs-max-512gb-graa/?subscriptionId=11942872',
        ]
    # TODO erase all the offers from telenor before running this.
    # Otherwise the offers will be duplicated if we run this every day
    def get_telenor_offers(self):
        # offer = Offer()
        # telecom_company = TelecomCompany.objects.filter(name='Telenor')
        # if telecom_company:
        #     offer.telecom_company = telecom_company[0]
        # else:
        #     offer.telecom_company = TelecomCompany.objects.create(name='Telenor')
        # offer.save()
        # return


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
                print("mobile_url = ", mobile_url)
                print("Full name = ", full_name)
                print("mobile name = ", mobile_name)
                print("mobile discount = ", discount)

                offer = Offer()
                offer.offer_url = mobile_url
                mobile = Mobile.objects.filter(name=mobile_name)
                if mobile: offer.mobile = mobile[0]
                telecom_company = TelecomCompany.objects.filter(name='Telenor')
                if telecom_company:
                    offer.telecom_company = telecom_company[0]
                else:
                    offer.telecom_company = TelecomCompany.objects.create(name='Telenor')
                offer.mobile_name = full_name
                offer.discount = discount
                offer.save()
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
