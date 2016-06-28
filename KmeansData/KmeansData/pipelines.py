# -*- coding: utf-8 -*-
import pymysql


# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html


class KmeansdataPipeline(object):
    def process_item(self, item, spider):

        con = pymysql.connect(db='choose_stock',
                              user='root',
                              password='1111ssss',
                              charset='utf8')  # 建立链接
        cur = con.cursor()  # 建立游标
        sql = ('insert into choose_stock_kmeansdata (stock_name, stock_id, stock_date, '
               'price_open, price_high, price_low, price_close, stock_volumn, stock_id_date) '
               'values (%s, %s, %s, %s, %s, %s, %s, %s, %s)')  # sql执行语句
        lis = (item['stock_name'], item['stock_id'], item['stock_date'], item['price_open'],
               item['price_high'], item['price_low'], item['price_close'], item['stock_volumn'],
               item['stock_id_date'])  # 需要插入的数据
        try:
            cur.execute(sql, lis)
        except Exception as e:
            print('*' * 64)
            print('Insert Error_kmeansdata:', e)
            con.rollback()
        else:
            con.commit()
        cur.close()
        con.close()
        return item
