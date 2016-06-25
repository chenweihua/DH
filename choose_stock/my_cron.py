# 定义各种定时任务
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

print(BASE_DIR)


def scrapy_news():  # 定义抓取股票消息的函数
    path_news = os.path.join(BASE_DIR, 's_c_stock')
    print(path_news)
    os.chdir(path_news)
    # os.system('scrapy crawl choose_stock_news')
    os.system('scrapy list')
    os.system('scrapy crawl choose_stock_news')

# scrapy_news()
