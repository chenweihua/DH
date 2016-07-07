# -*- coding: utf-8 -*-
import scrapy
import pymysql
from KmeansData.items import KmeansdataItem

# 若缺少某天的数据,可以用history_kdata的代码抓取.

def getStockId():  # 获取股票代码
    con = pymysql.connect(db='choose_stock',
                          user='root',
                          password='1111ssss',
                          charset='utf8')
    cur = con.cursor()
    # sql = "SELECT stock_id, stock_name FROM choose_stock_name_id WHERE stock_id = '300519'"
    sql = "SELECT stock_id, stock_name FROM choose_stock_name_id"
    try:
        cur.execute(sql)
    except Exception as e:
        print('*' * 64)
        print('Select Error:', e)
    res = cur.fetchall()
    con.commit()
    cur.close()
    con.close()
    # print(res)
    return res


# getStockId()


class Eachday_Kdata(scrapy.Spider):
    name = 'eachday_kdata'  # 获取最近三个月的股票数据,只需要获取一次即可
    allowed_domains = ["http://table.finance.yahoo.com/"]  # 在雅虎网获取

    def start_requests(self):
        req = []
        res = getStockId()  # 获取股票代码
        # 雅虎股票获取接口的网址为:http://table.finance.yahoo.com/table.csv?a=0&b=1&c=2012&d=3&e=19&f=2012&s=600690.ss
        # a:开始月份，从0开始计数，1月份表示为0；b:开始日期；c:开始年份；d:结束月份，从0开始计数，1月份表示为0；e:结束日期；f:结束年份。
        # url_prefix = 'http://table.finance.yahoo.com/table.csv?a=5&b=24&c=2016&d=5&e=24&f=2016&s='
        # 貌似雅虎股票查询不了当日股票信息,改用新浪股票接口
        url_prefix = 'http://hq.sinajs.cn/list='
        for each_id in res:
            stock_data = KmeansdataItem()
            stock_id = each_id[0]
            stock_data['stock_id'] = stock_id
            stock_name = each_id[1]
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
            yield stock_data
        except Exception as e:
            print(response.url, '抓取数据错误:', e)
