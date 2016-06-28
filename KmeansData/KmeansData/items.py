# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class KmeansdataItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    stock_name = scrapy.Field()  # 股票名称
    stock_id = scrapy.Field()  # 股票代码
    stock_date = scrapy.Field() # 交易日期
    price_open = scrapy.Field()  # 开盘价
    price_high = scrapy.Field()  # 最高价
    price_low = scrapy.Field()  # 最低价
    price_close = scrapy.Field()  # 收盘价
    stock_volumn = scrapy.Field()  # 成交量
    stock_id_date = scrapy.Field()  # 重要,以股票代码及交易日期组成的字符,判断数据唯一的标示,django中model的unique为True
