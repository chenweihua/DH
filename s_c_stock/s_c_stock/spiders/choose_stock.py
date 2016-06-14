# -*- coding: utf-8 -*-
import scrapy
import re
from datetime import datetime
from s_c_stock.items import SCStockItem
import sys  # 用于错误输出

now = datetime.now()  # 现在时刻
today = now.strftime('%m-%d')  # 今日日期
# today = '06-10'  # 测试用特定日期


def pos_or_neg(title):  # 判断是利好消息还是利空消息,利好为1,利空为0,其余为-1
    key_word_pos = '收购|并购|入股|重组|投资|发行|联合|合作|改革|复牌|高送转|证金|增持|携手'  # 股市热门概念
    pattern_pos = '(?:' + key_word_pos + ')'
    pattern_pos = re.compile(pattern_pos)
    key_word_neg = '撤销|停止|取消|不确定|终止|减持|起诉|违约|叫停'
    pattern_neg = '(?:' + key_word_neg + ')'
    pattern_neg = re.compile(pattern_neg)
    if pattern_pos.search(title) and not pattern_neg.search(title):
        return 1  # 返回利好消息
    elif pattern_neg.search(title):
        return 0  # 返回利空消息
    else:
        return -1  # 被舍弃的消息


class CStockSpider(scrapy.Spider):
    name = 'choose_stock_news'

    def start_requests(self):
        req = []
        url1 = 'http://ggjd.cnstock.com/gglist/search/ggkx/0'  # 中国证券网->上市公司专区->信息披露与公告解读->公告快讯
        req1 = scrapy.Request(url1, callback=self.parse_url1)
        req.append(req1)

        url2 = 'http://ggjd.cnstock.com/gglist/search/qmtbbdj/0'  # 中国证券网->上市公司专区->信息披露与公告解读->本网独家
        req2 = scrapy.Request(url2, callback=self.parse_url1)  # 亲测验证,抓取方式同req1
        req.append(req2)

        url5 = 'http://finance.eastmoney.com/news/cgsxw_1.html'  # 东方财富网->财经频道->公司新闻
        req5 = scrapy.Request(url5, callback=self.parse_url5)
        req.append(req5)

        return req

    def parse_url1(self, response):
        # 首先判断第一条新闻的时间,为今日日期,则开始抓取,不是今日日期,停止抓取.
        # 抓取完当前页后,再次判断最后一条新闻的时间,若为今日日期,则进入下一个页面抓取,若不是,则停止抓取.

        datetime_last = response.xpath('//div[@class="main-list"]'
                                       '/ul[@class="new-list"]/li/span/text()')[-1].extract()  # 最后一条消息的日期和时间
        date_last = datetime_last[:5]  # 最后一条消息的日期
        datetime_first = response.xpath('//div[@class="main-list"]'
                                        '/ul[@class="new-list"]/li/span/text()')[0].extract()  # 第一条消息时间
        date_first = datetime_first[:5]  # 第一条消息的日期

        if date_first == today:  # 第一条消息的时间为当前时间, 开始抓取
            lis = response.xpath('//div[@class="main-list"]/ul[@class="new-list"]/li')  # <li>的列表
            for li in lis:
                news_each = SCStockItem()  # 保存每一条新闻
                try:
                    title_time = li.xpath('span/text()')[0].extract()
                    if title_time[:5] == today:  # 如果消息的时间与今日的时间相同
                        title = li.xpath('a/@title')[0].extract()
                        flag_pn = pos_or_neg(title)  # 获取新闻类型
                        if flag_pn != -1:  # 如果符合热门概念
                            news_each['flag_pn'] = flag_pn  # 保存新闻类型
                            news_each['name'] = title  # 保存新闻标题
                            news_each['url'] = li.xpath('a/@href')[0].extract()  # 保存新闻网址
                            yield scrapy.Request(news_each['url'], meta={'item': news_each},
                                                 callback=self.parse_url1_detail)  # 进入新闻详细页面爬取
                except Exception as e:
                    print(e)
                    # sys.stderr.write(e)  # 没效果
            if date_last == today:  # 最后一条消息的时间为当前时间,进入下一个页面
                url = response.url  # 当前网址
                url_last_index = int(url[-1]) + 1
                url = url[:-1] + str(url_last_index)
                yield scrapy.Request(url, callback=self.parse_url1)

    def parse_url1_detail(self, response):
        news_each = response.meta['item']
        news_each['published_time'] = response.xpath('//div[1][@class="bullet"]/span[1]/text()')[0].extract()  # 新闻发布时间
        news_each['origin_from'] = response.xpath('//div[1][@class="bullet"]/span[2]/a/text()')[0].extract()  # 新闻来源地
        content = response.xpath('//div[@id="qmt_content_div"]/p').extract()  # 新闻的内容, 未考虑好是否需要<p>,列表的形式
        # 已尝试提取出页面的股票图表,未成功,源代码中无图表相关部分.
        news_each['content'] = ''.join(content)  # 转化为字符串,方法比较基础,但巧妙
        yield news_each

    def parse_url5(self, response):
        datetime_first = response.xpath('//div[@class="mainCont"]/div/div/ul/li/span/text()')[0].extract()  # 第一条消息时间
        date_first = datetime_first[5:10]  # 第一条消息日期
        # date_first = '06-10'
        datetime_last = response.xpath('//div[@class="mainCont"]/div/div/ul/li/span/text()')[-1].extract()  # 最后一条消息时间
        date_last = datetime_last[5:10]

        if date_first == today:  # 第一条消息的时间为当前时间, 开始抓取
            lis = response.xpath('//div[@class="mainCont"]/div/div/ul/li')  # <li>的列表
            for li in lis:
                news_each = SCStockItem()  # 保存每一条新闻
                try:
                    title_time = li.xpath('span/text()')[0].extract()
                    if title_time[5:10] == today:  # 如果消息的时间和今日的时间相同
                        title = li.xpath('a/@title')[0].extract()  # 提取新闻标题
                        flag_pn = pos_or_neg(title)  # 获取新闻类型
                        if flag_pn != -1:  # 如果符合热门概念
                            news_each['flag_pn'] = flag_pn  # 保存新闻类型
                            news_each['name'] = title
                            news_each['url'] = li.xpath('a/@href')[0].extract()  # 保存新闻网址
                            news_each['published_time'] = title_time  # 保存新闻发布时间
                            yield scrapy.Request(news_each['url'], meta={'item': news_each},
                                                 callback=self.parse_url5_detail)  # 进入新闻详细页面爬取
                except Exception as e:
                    print('*' * 64)
                    print(e)
            if date_last == today:  # 最后一条消息的时间为当前时间,进入下一个页面
                url = response.url  # 当前网址
                url_index = int(url[-6]) + 1  # 网页码计数器
                url = url[:-6] + str(url_index) + url[-5:]
                yield scrapy.Request(url, callback=self.parse_url5)

    def parse_url5_detail(self, response):
        news_each = response.meta['item']
        news_each['origin_from'] = '东方财富网'
        content = response.xpath('//div[@id="ContentBody"]/p').extract()  # 新闻的内容

        content_temp = []  # 将content中的图表变换到content末尾
        for each_content in content[:-1]:
            if 'style' in each_content:
                index = content.index(each_content)
                del content[index]
                content_temp.append(each_content)
        content.extend(content_temp)

        news_each['content'] = ''.join(content)  # 转化为字符串
        yield news_each
