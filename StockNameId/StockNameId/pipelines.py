# -*- coding: utf-8 -*-
from scrapy.exceptions import DropItem
import pymysql

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html


class StocknameidPipeline(object):
    def __init__(self):
        self.ids_seen = set()  # 简单的去重方式,利用股票代码去重.

    def process_item(self, item, spider):
        if item['stock_id'] in self.ids_seen:
            print('*' * 64)
            raise DropItem("Duplicate stock_id found: %s" % item['stock_id'])
        else:
            self.ids_seen.add(item['stock_id'])
            # 将数据插入到数据库中
            con = pymysql.connect(db='choose_stock',
                                  user='root',
                                  password='1111ssss',
                                  charset='utf8')  # 建立链接
            cur = con.cursor()  # 建立游标
            sql = ('insert into choose_stock_name_id (stock_name, stock_id) '
                   'values (%s, %s)')  # sql执行语句
            lis = (item['stock_name'], item['stock_id'])  # 需要插入的数据
            try:
                cur.execute(sql, lis)
            except Exception as e:
                print('*' * 64)
                print('Insert Error_name_id:', e)
                con.rollback()
            else:
                con.commit()
            cur.close()
            con.close()

            return item
