# -*- coding: utf-8 -*-
# 以单独脚本的形式启动scrapy spider, 调试用
import scrapy
from scrapy.crawler import CrawlerProcess


class Eachday_Kdata(scrapy.Spider):
    name = 'eachday_kdata'  # 获取最近三个月的股票数据,只需要获取一次即可
    allowed_domains = ["http://table.finance.yahoo.com/"]  # 在雅虎网获取

    def start_requests(self):
        req = []
        res = '300511'  # 获取股票代码

        url_prefix = 'http://hq.sinajs.cn/list='

        stock_data = {}
        stock_id = res
        stock_data['stock_id'] = stock_id
        stock_name = '雪榕生物'
        stock_data['stock_name'] = stock_name
        if stock_id.startswith('6'):
            url_end = 'sh' + stock_id  # 以6开头为上证股票
        else:
            url_end = 'sz' + stock_id  # 以非6开头(0或3开头)为深证股票
        url = url_prefix + url_end
        req_each = scrapy.Request(url, callback=self.parse, meta={'item': stock_data})
        req.append(req_each)
        return req

    def parse(self, response):
        datas = response.body.split(b',')
        try:
            stock_data = response.meta['item']
            stock_date = datas[-3].decode()  # 股票交易日期
            stock_data['stock_date'] = stock_date
            price_open = datas[1].decode()  # 股票开盘价
            stock_data['price_open'] = price_open
            price_high = datas[4].decode()  # 股票最高价
            stock_data['price_high'] = price_high
            price_low = datas[5].decode()  # 股票最低价
            stock_data['price_low'] = price_low
            price_close = datas[3].decode()  # 股票收盘价
            stock_data['price_close'] = price_close
            stock_volumn = datas[8].decode()  # 股票成交量,以股为单位
            stock_data['stock_volumn'] = stock_volumn
            stock_data['stock_id_date'] = stock_data['stock_id'] + '_' + stock_date
            # print(stock_data)
            yield stock_data
        except Exception as e:
            print('抓取数据错误:', e)

# 暂时屏蔽以下三项,因为scrapy list要启动它

# process = CrawlerProcess()
# process.crawl(Eachday_Kdata)
# process.start()
