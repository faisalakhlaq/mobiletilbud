from django.core.management.base import (BaseCommand, 
CommandError, no_translations)
from telecompanies.tilbud_spider import task_fetch_offers

class Command(BaseCommand):
    help = 'Fetches the offers for all telecom companies'
    
    @no_translations
    def handle(self, *args, **options):
        try:
            task_fetch_offers()
            self.stdout.write(self.style.SUCCESS('Successfully fetched offers from telecom companies'))
        except Exception as e:
            raise CommandError('Failed to fetch offers', e)
