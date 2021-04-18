from django.core.management.base import (BaseCommand, 
CommandError, no_translations)
from mobiles.mobile_spider import GsmarenaMobileSpecSpider

class Command(BaseCommand):
    """Download the mobile and its details by providing name, brand_name and url.
    python ../../../manage.py fetch_mobile mobile_full_name, brand_name, url"""
    help = 'Fetches the mobile and its details from a given url. \
    Please write the command and provide arguments like \
    python ../../../manage.py fetch_mobile mobile_full_name, brand_name, url'

    def add_arguments(self, parser):
        parser.add_argument('mobile_name', type=str, help='Mobile name to be fetched.')
        parser.add_argument('brand_name', type=str, help='Brand name of the mobile.')
        parser.add_argument('url', type=str, help='URL from which the mobile will be fetched.')

    @no_translations
    def handle(self, *args, **kwargs):
        try:
            mobile_name = kwargs['mobile_name']
            brand_name = kwargs['brand_name']
            url = kwargs['url']
            GsmarenaMobileSpecSpider().fetch_mobile(
                mobile_name=mobile_name, 
                brand_name=brand_name, 
                url=url,
                )
            self.stdout.write(self.style.SUCCESS('Successfully fetched mobile'))
        except Exception as e:
            raise CommandError('Failed to fetch mobile', e)
