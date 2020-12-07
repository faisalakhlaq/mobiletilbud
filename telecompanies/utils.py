from itertools import chain

from telecompanies.models import Offer

def get_popular_offers(offers=None, offers_per_company=1):
    """Returns highest discount offers. 
    number of offers_per_company for each telecomcompany."""
    if not offers:
        offers = Offer.objects.all().order_by('updated')
    telenor_best_offer = offers.filter(
        telecom_company__name__iexact='Telenor').order_by('-discount_offered')
    if not telenor_best_offer:
        telenor_best_offer = offers.filter(telecom_company__name__iexact='Telenor')
    if telenor_best_offer and len(telenor_best_offer) > offers_per_company:
        telenor_best_offer = telenor_best_offer[:offers_per_company]
    three_best_offer = offers.filter(
        telecom_company__name__iexact='3').order_by('-discount_offered')
    if not three_best_offer:
        three_best_offer = offers.filter(telecom_company__name__iexact='3')
    if three_best_offer and len(three_best_offer) > offers_per_company:
        three_best_offer = three_best_offer[:offers_per_company]
    telia_best_offer = offers.filter(
        telecom_company__name__iexact='Telia').order_by('-discount_offered')[:5]
    if not telia_best_offer:
        telia_best_offer = offers.filter(telecom_company__name__iexact='Telia')
    if telia_best_offer and len(telia_best_offer) > offers_per_company:
        telia_best_offer = telia_best_offer[:offers_per_company]
    result_list = list(chain(telenor_best_offer, three_best_offer, telia_best_offer))
    return result_list
