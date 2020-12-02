from celery.decorators import task
# from celery import shared_task
from celery.utils.log import get_task_logger

from mobiles.mobile_specs_spider import GsmarenaMobileSpecSpider

logger = get_task_logger(__name__)

@task(bind=True)
def fetch_mobiles_task(brand_name):
    """
    Fetch and save mobile technical details 
    """
    GsmarenaMobileSpecSpider().fetch_mobile_specs(brand_name)
    logger.info("Saved Motorola Mobiles")
