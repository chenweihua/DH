# -*- coding: utf-8 -*-
import scrapy
import pymysql
from CashFlowData.items import CashflowdataItem


def getStockId():  # 获取股票代码
    con = pymysql.connect(db='choose_stock',
                          user='root',
                          password='1111ssss',
                          charset='utf8')
    cur = con.cursor()
    # sql = "SELECT stock_id, stock_name FROM choose_stock_name_id WHERE stock_id = '600612'"
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


class HistoryCdata(scrapy.Spider):
    name = 'history_cdata'  # 获取最近30个交易日股票资金流量数据,只需要获取一次即可
    # allowed_domains = ["http://data.eastmoney.com/"]  # 在东方财富网获取

    def start_requests(self):
        req = []
        res = getStockId()  # 获取股票代码
        # res = [('601258', '庞大集团')]  # 测试单个股票
        url_prefix1 = 'http://data.eastmoney.com/zjlx/'  # 在parse中设置抓取规则,先1后2
        # url_prefix2 = 'http://data.eastmoney.com/stockcomment/'  # 在parse2中设置抓取规则
        for each_id in res:
            cash_data = CashflowdataItem()
            stock_id = each_id[0]
            cash_data['stock_id'] = stock_id
            stock_name = each_id[1]
            cash_data['stock_name'] = stock_name
            url_end = stock_id + '.html'
            url1 = url_prefix1 + url_end
            # url2 = url_prefix2 + url_end
            req_each1 = scrapy.Request(url1, callback=self.parse1, meta={'item': cash_data})
            # req_each2 = scrapy.Request(url2, callback=self.parse2, meta={'item': cash_data})
            req.append(req_each1)
            # req.append(req_each2)
        return req

    def parse1(self, response):  # 对股票控盘数据进行抓取

        trs = response.xpath('//table[@id="dt_1"]/tbody/tr')  # 资金流数据列表
        for tr in trs[1:]:  # 最近的一天不抓取,留待eachday_cdata抓取
            try:
                cash_data = response.meta['item']
                cash_data['stock_date'] = tr.xpath('td[1]/text()')[0].extract().strip()  # 获取成交日期
                cash_data['price_close'] = tr.xpath('td[2]/span/text()')[0].extract()  # 收盘价
                cash_data['var_degree'] = tr.xpath('td[3]/span/text()')[0].extract()  # 涨跌幅
                cash_data['maincash_in'] = tr.xpath('td[4]/span/text()')[0].extract()  # 主力净流入
                cash_data['maincash_in_rate'] = tr.xpath('td[5]/span/text()')[0].extract()  # 主力净占比,净流入占全部成交量的比例
                cash_data['stock_id_date'] = cash_data['stock_id'] + '_' + cash_data['stock_date']  # 判定数据唯一的标识
                cash_data['join_degree'] = ''  # 无数据时,用空字符代替
                cash_data['control_type'] = ''
                cash_data['main_cost'] = ''

                yield cash_data
            except Exception as e:
                print('*' * 64)
                print('抓取数据错误:', e)
