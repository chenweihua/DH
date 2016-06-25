# -*- coding: utf-8 -*-
import scrapy
from StockNameId.items import StocknameidItem


class StockNameId(scrapy.Spider):
    name = 'crawl_name_id'
    allowed_domains = ["eastmoney.com"]
    start_urls = ['http://quote.eastmoney.com/stocklist.html']

    def parse(self, response):
        lis = response.xpath('//div[@id="quotesearch"]/ul/li')  # 股票代码<li>列表
        for li in lis:
            stock_name_id = StocknameidItem()
            content = li.xpath('a/text()')[0].extract()  # 含有股票代码和名称的字符串
            stock_name = content.split('(')[0]
            stock_id = content.split('(')[1][:-1]
            if stock_id.startswith('6') or stock_id.startswith('0') or stock_id.startswith('3'):
                stock_name_id['stock_name'] = stock_name
                stock_name_id['stock_id'] = stock_id
                yield stock_name_id
