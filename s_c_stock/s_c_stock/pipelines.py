# -*- coding: utf-8 -*-
from scrapy.exceptions import DropItem
import pymysql
import sys


# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html


class SCStockPipeline(object):
    def __init__(self):
        self.names_seen = set()  # 简单的去重方式,利用新闻标题不能相同的方式去重,后续考虑文本相似度的方法.

    def process_item(self, item, spider):
        # 首先去重,暂时考虑直接在本次抓取中去重,后续必须考虑与数据库中提取的数据相比去重.
        if item['name'] in self.names_seen:
            print('*' * 64)
            raise DropItem("Duplicate name found: %s" % item['name'])
        else:
            self.names_seen.add(item['name'])
            # 将数据插入到数据库中
            con = pymysql.connect(db='choose_stock',
                                  user='root',
                                  password='1111ssss',
                                  charset='utf8')  # 建立链接
            cur = con.cursor()  # 建立游标
            sql = ('insert into choose_stock_news (name, url, content, published_time, origin_from, flag_pn) '
                   'values (%s, %s, %s, %s, %s, %s)')  # sql执行语句
            lis = (item['name'], item['url'], item['content'], item['published_time'], item['origin_from'], item['flag_pn'])  # 需要插入的数据
            try:
                cur.execute(sql, lis)
            except Exception as e:
                print('*' * 64)
                print('Insert Error_guagua:', e)
                con.rollback()
            else:
                con.commit()
            cur.close()
            con.close()

            return item
