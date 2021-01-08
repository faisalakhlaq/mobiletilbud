from itertools import chain

from core.models import TelecomCompany
from telecompanies.models import Offer

def get_popular_offers(offers=None, offers_per_company=1):
    """Returns offers with highest discount. Number of 
    offers_per_company for each telecomcompany."""
    telecompanies = TelecomCompany.objects.all()
    if not offers:
        offers = Offer.objects.all().order_by('updated')
    offers_list = []
    for telecompany in telecompanies:
        comp_offers = offers.filter(telecom_company = telecompany).order_by('-discount_offered')[:offers_per_company]
        if comp_offers and len(comp_offers) > 0:
            offers_list = offers_list + list(comp_offers)
    result_list = list(chain(offers_list))
    return result_list
