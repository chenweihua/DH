"""
WSGI config for project project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.9/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application
# 自定义引入模块
# import multiprocessing, time
# from datetime import datetime

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "project.settings")

application = get_wsgi_application()

# 自定义代码
# BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # 获取项目根目录文件夹
#
#
# def stock_process():  # 股票进程,应包含news, k_measn, capital三个处理阶段
#     while True:
#         now = datetime.now()  # 获取现在时刻
#         if (now.minute % 5) == 0:  # 每隔5分钟抓取
#             print('News process starts at', time.ctime())
#             news_path = os.path.join(BASE_DIR, 's_c_stock')
#             os.chdir(news_path)
#             os.system('scrapy crawl choose_stock_news')
#             time.sleep(60)  # 如果抓取时间过短, 保证在一分钟内不会重复抓取
#             print('News process ends at', time.ctime())
#
#
# stock_proc = multiprocessing.Process(target=stock_process)  # 建立子进程
# stock_proc.start()
