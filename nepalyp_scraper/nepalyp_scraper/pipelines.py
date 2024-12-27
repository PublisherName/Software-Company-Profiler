# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter


class NepalypScraperPipeline:
    @staticmethod
    def process_item(item, spider):
        adapter = ItemAdapter(item)
        for field in adapter.field_names():
            value = adapter.get(field)
            if value:
                adapter[field] = value.strip()
            else:
                adapter[field] = ""
        return item
