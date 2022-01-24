# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy
from w3lib.html import remove_tags
from itemloaders.processors import TakeFirst, MapCompose, Identity, Join

def remove_tag(item):
    if item:
        item = item.strip()
        item = item.replace('\t', "")
        item = item.replace('\n', "")
        item = " ".join(item.split())
        item = item.encode('ascii', 'ignore')
        item = item.decode()
        item = remove_tags(item)
        return item


class AmazonItem(scrapy.Item):
    Category = scrapy.Field(
        input_processor=MapCompose(remove_tag),
        output_processor=TakeFirst()
    )
    Sub_Category = scrapy.Field(
        output_processor=TakeFirst()
    )
    Product_Model = scrapy.Field(
        output_processor=TakeFirst()
    )
    Product_Name = scrapy.Field(
        output_processor=TakeFirst()
    )
    Price = scrapy.Field(
        output_processor=TakeFirst()
    )
    Available_Quantity = scrapy.Field(
        output_processor=TakeFirst()

    )
    Description = scrapy.Field(
        input_processor=MapCompose(lambda x:remove_tag(x)),
        output_processor=Join('\n')
    )
    Product_Spec = scrapy.Field(
        input_processor=MapCompose(lambda x:x.strip()),
        output_processor=Identity()
    )
    Color = scrapy.Field(
        output_processor=TakeFirst()
    )
    Size = scrapy.Field(
        output_processor=TakeFirst()
    )
    Weight = scrapy.Field(
        output_processor=TakeFirst()
    )
    Stock_Status = scrapy.Field(
        output_processor=TakeFirst()
    )
    Images = scrapy.Field(
        output_processor=Join('\n')
    )
    # Product_Url = scrapy.Field(
    #     output_processor=TakeFirst())
    Package_Includes = scrapy.Field(
        output_processor=Join('\n')
    )