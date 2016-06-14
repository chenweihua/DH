# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class SCStockItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    name = scrapy.Field()  # 新闻标题
    url = scrapy.Field()  # 新闻网页链接
    content = scrapy.Field()  # 新闻内容
    published_time = scrapy.Field()  # 新闻发布时间
    origin_from = scrapy.Field()  # 新闻来源地
    flag_pn = scrapy.Field()  # 新闻的类型,1为利好,0为利空
