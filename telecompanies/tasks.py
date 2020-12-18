#!/usr/bin/python3.8
# from celery.decorators import periodic_task
# from celery import shared_task
# from celery.utils.log import get_task_logger

from .tilbud_spider import TelenorSpider, TeliaSpider, ThreeSpider, YouSeeSpider

# logger = get_task_logger(__name__)

# @shared_task
def task_fetch_telenor_offers():
    """
    Saves latest offers from Telenor 
    """
    TelenorSpider().fetch_offers()
    # logger.info("Saved latest Telenor offers")

# @shared_task
def task_fetch_yousee_offers():
    """
    Saves latest offers from YouSee 
    """
    YouSeeSpider().fetch_offers()
    # logger.info("Saved latest YouSee offers")

# @shared_task
def task_fetch_telia_offers():
    """
    Saves latest offers from Telia 
    """
    TeliaSpider().get_telia_offers()
    # logger.info("Saved latest Telia offers")

# @shared_task
def task_fetch_three_offers():
    """
    Saves latest offers from Three 
    """
    ThreeSpider().get_three_offers()
    # logger.info("Saved latest Three offers")
