# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

from scrapy import Field, Item


class NepalypScraperItem(Item):
    name = Field()
    address = Field()
    city = Field()
    website = Field()
    career_page = Field()
    email = Field()
    linkedin = Field()
    phone = Field()
