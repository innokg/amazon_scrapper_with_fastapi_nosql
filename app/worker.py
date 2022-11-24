"""
Worker module for creating tasks in celery
"""
from cassandra.cqlengine import connection
from cassandra.cqlengine.management import sync_table
from celery import Celery
from celery.schedules import crontab
from celery.signals import (
    beat_init,
    worker_process_init,
)  # import this for scheduling tasks
from loguru import logger
from . import config, db, models, schema, scrapper, crud
from .schema import ProductListSchema

celery_app = Celery(__name__)
settings = config.get_settings()

REDIS_URL = settings.redis_url
celery_app.conf.broker_url = REDIS_URL
celery_app.conf.result_backend = REDIS_URL

Product = models.Product
ProductScrapeEvent = models.ProductScrapeEvent


def celery_on_startup(*args, **kwargs):
    """
    function to start up celery
    :param args:
    :param kwargs:
    :return:
    """
    if connection.cluster is not None:
        connection.cluster.shutdown()
    if connection.session is not None:
        connection.cluster.shutdown()
    cluster = db.get_cluster()
    session = cluster.connect()
    connection.register_connection(str(session), session=session)
    connection.set_default_connection(str(session))
    sync_table(Product)
    sync_table(ProductScrapeEvent)


beat_init.connect(celery_on_startup())
worker_process_init.connect(celery_on_startup())


@celery_app.on_after_configure.connect
def setup_periodic_tasks(sender, *args, **kwargs):
    """
    creating periodic tasks
    """
    sender.add_periodic_task(
        crontab(minute="*/3"),
        scrape_products.s()
    )



@celery_app.task()
def random_task(name):
    """
    function to create random task
    :param name:
    :return:
    """
    logger.info(f"Who throws a shoe. Honestly {name}")
    session = db.get_session()


@celery_app.task()
def list_products():
    """
    function to get list of products
    :param:
    :return:
    """
    logger.info(list(Product.objects().all().values_list("asin", flat=True)))


@celery_app.task()
def scrape_asin(asin):
    logger.info(asin)
    s = scrapper.Scraper(asin=asin, endless_scroll=True)
    dataset = s.scrape()
    try:
        validated_data = schema.ProductListSchema(**dataset)
    except:
        validated_data = None
    if validated_data is not None:
        product, _ = crud.add_scrape_event(validated_data.dict())
        return asin, True
    return asin, False


@celery_app.task()
def scrape_products():
    """
    function to get list of products
    :param:
    :return:
    """
    logger.info('Doing scraping, please wait')
    qty = Product.objects().all().values_list("asin", flat=True)
    for asin in qty:
        scrape_asin.delay(asin)




