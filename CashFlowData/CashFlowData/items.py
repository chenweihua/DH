# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class CashflowdataItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    stock_name = scrapy.Field()  # 股票名称
    stock_id = scrapy.Field()  # 股票代码
    stock_date = scrapy.Field()  # 交易日期

    price_close = scrapy.Field()  # 收盘价
    var_degree = scrapy.Field()  # 股票的涨跌幅度,如-3.2%
    maincash_in = scrapy.Field()  # 主力净流入
    maincash_in_rate = scrapy.Field()  # 主力净占比
    join_degree = scrapy.Field()  # 机构参与度
    control_type = scrapy.Field()  # 控盘类型:不控盘,轻度控盘,中度控盘,完全控盘
    main_cost = scrapy.Field()  # 主力成本
    # 可以绘制机构参与程度变化图,很有参考价值 http://data.eastmoney.com/stockcomment/601258.html
    stock_id_date = scrapy.Field()  # 重要,以股票代码及交易日期组成的字符,判断数据唯一的标示,django中model的unique为True
