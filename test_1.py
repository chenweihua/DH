import os
os.chdir(r'/Users/DQ/Desktop/Python/CHOOSE_STOCK/project')

from datetime import datetime, timedelta
from django.conf import settings
##settings.configure()


from choose_stock.models import KmeansData












def KmeansStrategy():  # 根据策略:跌-跌-涨-涨,最后一天下影线越短越好 选择符合要求的股票
    tradeday_3 = KmeansData.objects.filter(stock_id='601988').dates('stock_date', 'day', order='DESC')[
        3]  # 提取中国银行的倒数第四个交易日,作为所有股票的倒数第四个交易日
    
    judge_3 = KmeansData.objects.filter(stock_date=tradeday_3).values_list('stock_id', 'price_open',
                                                                           'price_close')  # 获取倒数第四个交易日的股票代码,开盘价,收盘价
    stock_id_list3 = [s[0] for s in judge_3 if s[1] > s[2]]  # 倒数第四日满足开盘价大于收盘价(绿)的股票代码
    tradeday_2 = tradeday_3 + timedelta(days=1)  # 倒数第3日
    judge_2 = KmeansData.objects.filter(stock_id__in=stock_id_list3, stock_date=tradeday_2).values_list('stock_id',
                                                                                                        'price_open',
                                                                                                        'price_close')  # 获取倒数第三个交易日的股票代码,开盘价,收盘价
    stock_id_list2 = [s[0] for s in judge_2 if s[1] > s[2]]  # 倒数第三日绿色股票代码
    tradeday_1 = tradeday_2 + timedelta(days=1)  # 倒数第2日
    judge_1 = KmeansData.objects.filter(stock_id__in=stock_id_list2, stock_date=tradeday_1).values_list('stock_id',
                                                                                                        'price_open',
                                                                                                        'price_close')  # 倒数第二个交易日股票数据
    stock_id_list1 = [s[0] for s in judge_1 if s[1] < s[2]]  # 倒数第2日红色股票代码
    tradeday_0 = tradeday_1 + timedelta(days=1)  # 倒数第1日
    judge_0 = KmeansData.objects.filter(stock_id__in=stock_id_list1, stock_date=tradeday_0).values_list('stock_id',
                                                                                                        'price_open',
                                                                                                        'price_close')  # 倒数第一日交易日股票数据
    stock_id_list0 = [s[0] for s in judge_0 if s[1] < s[2]]  # 倒数第1日红色股票代码
    return stock_id_list0


ss = KmeansStrategy()
