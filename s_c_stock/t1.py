import pymysql


DBKWARGS = {'db': 'choose_stock', 'user': 'root', 'password': '1111ssss',
            'host': 'localhost', 'use_unicode': True, 'charset': 'utf8'}

con = pymysql.connect(DBKWARGS)
