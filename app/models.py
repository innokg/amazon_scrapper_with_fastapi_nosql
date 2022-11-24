from cassandra.cqlengine import columns
from cassandra.cqlengine.models import Model

data = {
    "asin": "TESTING123D",
    "title": "Mark 1"
}


class Product(Model):  # turn into table, need inherit from Model
    __keyspace__ = "scrapper_app"
    asin = columns.Text(primary_key=True, required=True)
    title = columns.Text()
    price_str = columns.Text(default="-100")


class ProductScrapeEvent(Model):  # turn into table, need inherit from Model
    __keyspace__ = "scrapper_app"
    uuid = columns.UUID(primary_key=True)
    asin = columns.Text(index=True)
    title = columns.Text()
    price_str = columns.Text(default="-100")


# def this Product.objects().filter(asin="AMZNIDNUMBER")


# not this Product.objects().filter(title = "Mark 1")
