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
    name = 'eachday_cdata'  # 获取最近30个交易日股票资金流量数据,只需要获取一次即可
    # allowed_domains = ["http://data.eastmoney.com/"]  # 若不隐藏,貌似不会抓取数据

    def start_requests(self):
        req = []
        res = getStockId()  # 获取股票代码
        # res = [('601258', '庞大集团')]  # 测试单个股票
        url_prefix1 = 'http://data.eastmoney.com/zjlx/'  # 在parse中设置抓取规则,先1后2
        for each_id in res:
            cash_data = CashflowdataItem()
            stock_id = each_id[0]
            cash_data['stock_id'] = stock_id
            stock_name = each_id[1]
            cash_data['stock_name'] = stock_name
            url_end = stock_id + '.html'
            url1 = url_prefix1 + url_end
            req_each1 = scrapy.Request(url1, callback=self.parse1, meta={'item': cash_data})
            req.append(req_each1)
        return req

    def parse1(self, response):  # 对股票控盘数据进行抓取
        cash_data = response.meta['item']
        url_prefix2 = 'http://data.eastmoney.com/stockcomment/'
        url_end2 = cash_data['stock_id'] + '.html'
        url2 = url_prefix2 + url_end2
        trs = response.xpath('//table[@id="dt_1"]/tbody/tr')  # 资金流数据列表
        tr = trs[0]  # 抓取最近一天的数据
        try:
            cash_data['stock_date'] = tr.xpath('td[1]/text()')[0].extract().strip()  # 获取成交日期
            cash_data['price_close'] = tr.xpath('td[2]/span/text()')[0].extract()  # 收盘价
            cash_data['var_degree'] = tr.xpath('td[3]/span/text()')[0].extract()  # 涨跌幅
            cash_data['maincash_in'] = tr.xpath('td[4]/span/text()')[0].extract()  # 主力净流入
            cash_data['maincash_in_rate'] = tr.xpath('td[5]/span/text()')[0].extract()  # 主力净占比,净流入占全部成交量的比例
            cash_data['stock_id_date'] = cash_data['stock_id'] + '_' + cash_data['stock_date']  # 判定数据唯一的标识
            yield scrapy.Request(url2, callback=self.parse2, meta={'item': cash_data})
        except Exception as e:
            print('*' * 64)
            print('抓取数据错误:', e)

    def parse2(self, response):
        cash_data = response.meta['item']
        try:
            cash_data['join_degree'] = response.xpath('//span[@id="sp_jgcyd"]/text()').re(r'\d.*%')[0]  # 机构参与度,百分数
            cash_data['control_type'] = response.xpath('//span[@id="sp_jgcyd"]/text()').re(r'属于.*')[0][2:].strip()  # 机构控盘类型
            cash_data['main_cost'] = response.xpath('//span[@id="sp_zlcb"]/text()').re(r'成本(\d.*?)元')[0]  # 主力最新交易日成本价
            yield cash_data
        except Exception as e:
            print('*' * 64)
            print('抓取数据错误:', e)
